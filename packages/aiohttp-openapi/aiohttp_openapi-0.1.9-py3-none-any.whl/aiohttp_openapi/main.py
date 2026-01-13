import inspect
import pathlib
import re
from typing import Tuple

from aiohttp import web


class AiohttpOpenAPI:

    def __init__(self):
        self._YAML_DATA = None
        self.path_prefix = None

    def setup_openapi(self, app, path_prefix='', yaml_path=None):
        self.path_prefix = path_prefix if path_prefix[-1] != '/' else path_prefix[:-1]
        self._YAML_DATA = ''

        self._load_yml(yaml_path)
        self._travers_endpoints(app)

        swagger_ui_path = pathlib.Path(__file__).parent / 'dist'
        app.router.add_static('/dist', swagger_ui_path, show_index=True)

        app.router.add_get('/docs', self.redirect_to_index)
        app.router.add_get('/swagger', self.stream_yaml)


    async def redirect_to_index(self, request):
        path = request.path.replace('docs', 'dist/index.html')
        return web.HTTPFound(path)


    async def stream_yaml(self, request):
        stream = web.StreamResponse()
        await stream.prepare(request)
        await stream.write(self._YAML_DATA.encode())
        await stream.write_eof()
        return stream


    def _travers_endpoints(self, app) -> None:
        d_tree = {}
        for route in app.router.routes():
            method = route.method.lower()
            if method == 'head':
                continue
            endpoint = route.resource.canonical

            if route.handler.__doc__ and '---' in route.handler.__doc__:
                try:
                    docstr = route.handler.__doc__.splitlines()
                except AttributeError:
                    return None
                opanapi_docstr, is_skip_verify = self._extract_openapi_docstr(docstr)
                endpoint_, method_ = self._get_path_method(opanapi_docstr)
                if not is_skip_verify and (method != method_ or endpoint != endpoint_):
                    handler_file = inspect.getfile(route.handler)
                    assert False, f'Docstr mismatch in {handler_file}: {method} {endpoint} != {method_} {endpoint_}'

                path_with_prefix = f'{self.path_prefix}{endpoint_}'
                if d_tree.get(path_with_prefix) is None:
                    d_tree[path_with_prefix] = {}
                clean_openapi_docstr = self._remove_endpoint_and_method(opanapi_docstr)
                d_tree[path_with_prefix][method_] = clean_openapi_docstr

        # join dict to a single file
        for endpoint in d_tree:
            if len(d_tree[endpoint]) > 0:
                self._YAML_DATA += f'    {endpoint}:'
                for method in d_tree[endpoint]:
                    self._YAML_DATA += f'\n        {method}:'
                    docstr = d_tree[endpoint][method]
                    self._YAML_DATA += docstr
        pass


    def _load_yml(self, yaml_path) -> None:
        """
        Load a global YAML file if one exists.
        :param yaml_path:
        :return: None
        """
        with open(yaml_path, 'r') as yaml_file:
            data = yaml_file.read()
            self._YAML_DATA += data
        if 'paths' not in self._YAML_DATA:
            self._YAML_DATA += 'paths:\n'


    @staticmethod
    def _get_path_method(docstr: str) -> Tuple[str, str]:
        """
        Check if the first two lines of the docstring match a handler's path & method.

        :param docstr: The docstring to parse.
        :return: A tuple of (path, method).
        :raises ValueError: If the docstring format is invalid.
        """
        # Regex pattern for matching path and method with flexible whitespace
        pattern = r'^\s*(\S+):\s*\n\s*(\S+):\s*'

        # Perform the search
        result = re.findall(pattern, docstr, re.MULTILINE)

        # Ensure a valid result is found
        if not result or len(result[0]) != 2:
            raise ValueError(f"Invalid docstring format:\n{docstr}")

        path, method = result[0]

        # Validate the HTTP method
        valid_methods = {"post", "get", "delete", "put", "patch", "option"}
        if method not in valid_methods:
            raise ValueError(f"Invalid HTTP method '{method}' in docstring:\n{docstr}")

        return path, method


    def _remove_endpoint_and_method(self, docstr: str) -> str:
        second_new_line = self._find_nth(docstr, '\n', 2)
        return docstr[second_new_line:]

    @staticmethod
    def _extract_openapi_docstr(endpoint_doc):
        swagger_start = None
        is_skip_verify = False

        for i, line in enumerate(endpoint_doc):
            if line.rstrip()[:3] == "---":
                swagger_start = i + 1
                is_skip_verify = "aiohtt-openapi: skip-verify" in line
                break

        if swagger_start is None:
            return "", False

        # Everything after --- (raw, untrusted indentation)
        lines = endpoint_doc[swagger_start:]

        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()

        # FORCE indentation — never trust docstring whitespace
        out = "\n".join(f"    {line.rstrip()}" for line in lines) + "\n"

        return out, is_skip_verify


    @staticmethod
    def _find_nth(haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+len(needle))
            n -= 1
        return start
