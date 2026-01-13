from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

from fastapptest.core.ast_parser import BaseVisitor, ParsedFile


@dataclass(frozen=True)
class FastAPIDetectionResult:
    is_fastapi_project: bool
    app_files: List[Path]
    router_files: List[Path]


class FastAPIDetector(BaseVisitor):
    """
    AST visitor that detects FastAPI and APIRouter usage.
    """

    def __init__(self, parsed_file: ParsedFile) -> None:
        super().__init__(parsed_file)
        self.found_fastapi_app = False
        self.found_router = False

    def visit_Call(self, node: ast.Call) -> None:
        """
        Detect calls like:
        - FastAPI()
        - APIRouter()
        """
        func = node.func

        if isinstance(func, ast.Name):
            if func.id == "FastAPI":
                self.found_fastapi_app = True

            elif func.id == "APIRouter":
                self.found_router = True

        elif isinstance(func, ast.Attribute):
            # Handles cases like fastapi.FastAPI()
            if func.attr == "FastAPI":
                self.found_fastapi_app = True

            elif func.attr == "APIRouter":
                self.found_router = True

        self.generic_visit(node)


def detect_fastapi_project(parsed_files: List[ParsedFile]) -> FastAPIDetectionResult:
    """
    Run FastAPI detection across all parsed files.
    """

    app_files: List[Path] = []
    router_files: List[Path] = []

    for parsed in parsed_files:
        detector = FastAPIDetector(parsed)
        detector.visit(parsed.tree)

        if detector.found_fastapi_app:
            app_files.append(parsed.path)

        if detector.found_router:
            router_files.append(parsed.path)

    return FastAPIDetectionResult(
        is_fastapi_project=bool(app_files),
        app_files=sorted(app_files),
        router_files=sorted(router_files),
    )
