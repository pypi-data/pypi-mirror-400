# core/schema_extractor.py
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from fastapptest.core.ast_parser import ASTParser, ParsedFile, BaseVisitor


@dataclass(frozen=True)
class PydanticField:
    name: str
    type_annotation: str | None
    default: Any = None


@dataclass(frozen=True)
class PydanticModel:
    name: str
    fields: List[PydanticField]
    file: Path


class PydanticModelVisitor(BaseVisitor):
    """
    Visitor to extract Pydantic models from a parsed Python file.
    """

    def __init__(self, parsed_file: ParsedFile):
        super().__init__(parsed_file)
        self.models: List[PydanticModel] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        # Direct BaseModel inheritance
        is_base_model = any(self._is_pydantic_base(b) for b in node.bases)
    
        # Indirect inheritance: inherits from another Pydantic model in same file
        base_names = [b.id for b in node.bases if isinstance(b, ast.Name)]
        if not is_base_model and any(name in [m.name for m in self.models] for name in base_names):
            is_base_model = True
    
        if is_base_model:
            fields: List[PydanticField] = []
    
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    if isinstance(stmt.target, ast.Name):
                        name = stmt.target.id
                        type_annotation = self._get_annotation(stmt.annotation)
                        default = self._get_default(stmt.value)
                        fields.append(PydanticField(name, type_annotation, default))
    
                elif isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            fields.append(PydanticField(
                                name=target.id,
                                type_annotation=None,
                                default=self._get_default(stmt.value)
                            ))
    
            self.models.append(PydanticModel(name=node.name, fields=fields, file=self.path))
    
        self.generic_visit(node)

    def _is_pydantic_base(self, base: ast.expr) -> bool:
        """
        Returns True if the base is BaseModel or a known Pydantic model.
        """
        if isinstance(base, ast.Name):
            # Direct BaseModel or previously collected model
            return base.id == "BaseModel"
        elif isinstance(base, ast.Attribute):
            return base.attr == "BaseModel"
        return False

    def _get_annotation(self, annotation: ast.expr) -> str | None:
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            value = self._get_annotation(annotation.value)
            slice_ = self._get_annotation(annotation.slice)
            if value and slice_:
                return f"{value}[{slice_}]"
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return None

    def _get_default(self, value: ast.expr) -> Any:
        if value is None:
            return None
        if isinstance(value, ast.Constant):
            return value.value
        elif isinstance(value, ast.List):
            return []
        elif isinstance(value, ast.Dict):
            return {}
        elif isinstance(value, ast.NameConstant):
            return value.value
        return None


def extract_pydantic_models(py_file: Path) -> List[PydanticModel]:
    """
    Extract all Pydantic models from a single Python file.
    """
    parser = ASTParser()
    parsed_file: ParsedFile = parser.parse_file(py_file)
    visitor = PydanticModelVisitor(parsed_file)
    visitor.visit(parsed_file.tree)
    return visitor.models
