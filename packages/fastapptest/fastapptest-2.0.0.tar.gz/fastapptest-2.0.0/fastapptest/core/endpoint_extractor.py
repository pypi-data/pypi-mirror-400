from __future__ import annotations
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Optional

from fastapptest.core.ast_parser import ASTParser, ParsedFile

HTTP_METHODS = {
    "get", "post", "put", "delete", "patch", "options", "head"
}


@dataclass(frozen=False)
class Endpoint:
    file: Path
    function_name: str
    path: str
    methods: Set[str]
    body_model_name: Optional[str] = None  


class EndpointExtractor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.endpoints: List[Endpoint] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            endpoint = self._parse_decorator(decorator, node.name)
            if endpoint:
                self.endpoints.append(endpoint)

        self.generic_visit(node)

    def _parse_decorator(self, decorator: ast.expr, function_name: str):
        if not isinstance(decorator, ast.Call):
            return None

        if not isinstance(decorator.func, ast.Attribute):
            return None

        method = decorator.func.attr.lower()
        if method not in HTTP_METHODS:
            return None

        if not decorator.args:
            return None

        path_node = decorator.args[0]
        if not isinstance(path_node, ast.Constant):
            return None
        if not isinstance(path_node.value, str):
            return None

        return Endpoint(
            file=self.file_path,
            function_name=function_name,
            path=path_node.value,
            methods={method.upper()},
        )


def extract_endpoints(py_file: Path) -> List[Endpoint]:
    """
    Extract endpoints from a single Python file using ASTParser.
    """
    parser = ASTParser()
    parsed_file: ParsedFile = parser.parse_file(py_file)
    extractor = EndpointExtractor(parsed_file.path)
    extractor.visit(parsed_file.tree)
    return extractor.endpoints
