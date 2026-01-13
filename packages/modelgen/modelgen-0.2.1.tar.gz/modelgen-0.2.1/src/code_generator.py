import ast
import os
import re
import subprocess  # nosec B404
from copy import copy
from pathlib import Path
from typing import List

import yaml

TEMPORARY_MODEL_FILE_NAME = "temporary_model.py"
TEMPORARY_API_FILE_NAME = "temporary_api.yaml"


class CodeGenerator:
    output_dir: str
    _source_code: str
    _imports: list[ast.Import | ast.ImportFrom]
    _classes: list[ast.ClassDef]

    def __init__(
        self,
        openapi_file_path: str,
        output_dir: str,
        parameters: list[str],
        include_models_dir: str | None = None,
    ):
        """
        notes:
            * parametersは、datemodel-code-generatorに準拠
            https://github.com/koxudaxi/datamodel-code-generator/
        """
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        temporary_model_filepath = os.path.join(output_dir, TEMPORARY_MODEL_FILE_NAME)
        temporary_api_filepath = os.path.join(output_dir, TEMPORARY_API_FILE_NAME)
        self._generate_merged_openapi_file(openapi_file_path, include_models_dir)
        self._generate_temporary_model_file(temporary_model_filepath, parameters)
        source_code = self._import_temporary_file(temporary_model_filepath)
        self._imports = self._extract_imports(source_code)
        self._classes = self._extract_classes(source_code)
        self._source_code = source_code
        os.remove(temporary_model_filepath)
        os.remove(temporary_api_filepath)

    def filter_import_node(
        self, import_node: ast.Import | ast.ImportFrom, used_imports: set[str]
    ) -> ast.Import | ast.ImportFrom | None:
        """
        used_importsに含まれるimportのみを返す
        """
        new_node = copy(import_node)
        new_node.names = []

        if names := [
            name
            for name in import_node.names
            if (name.asname if name.asname else name.name) in used_imports
        ]:
            new_node.names = names

        return new_node if new_node.names else None

    def execute(self):
        class_names = {node.name for node in self._classes}

        for class_node in self._classes:
            class_source_code: str | None = ast.get_source_segment(
                self._source_code, class_node
            )

            if not class_source_code:
                continue

            # クラスの型ヒントから、importを取得
            class_imports = set()
            class_annotations = [
                attr.annotation
                for attr in class_node.body
                if isinstance(attr, ast.AnnAssign)
            ]
            for annotation in class_annotations:
                if isinstance(annotation, ast.Name) and annotation.id in class_names:
                    class_imports.add(annotation.id)

                if isinstance(annotation, ast.BinOp):
                    left = annotation.left
                    right = annotation.right

                    if isinstance(left, ast.Name) and isinstance(right, ast.Constant):
                        if left.id in class_names:
                            class_imports.add(left.id)

            # インポートのソースコード生成
            used_imports: set[str] = self._get_imports_for_class(class_node)
            import_nodes: list[ast.Import | ast.ImportFrom | None] = [
                self.filter_import_node(import_node, used_imports)
                for import_node in self._imports
            ]
            import_source_codes = [ast.unparse(node) for node in import_nodes if node]

            # モデル同士のインポート追加
            if class_imports:
                module = self.output_dir.replace("/", ".")
                if module[-1] != ".":
                    module = module + "."
                class_import_source_codes = [
                    f"from {module}{self._convert_to_snake_case(str(class_import))} import {class_import}"
                    for class_import in class_imports
                ]
                import_source_codes.extend(class_import_source_codes)

            content = "\n\n\n".join(
                [
                    "\n".join(import_source_codes),
                    class_source_code,
                ]
            )

            with open(
                Path(
                    self.output_dir,
                    f"{self._convert_to_snake_case(class_node.name)}.py",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(content + "\n")

    def _get_imports_for_class(self, class_node: ast.ClassDef) -> set[str]:
        used_names = set()
        for node in ast.walk(class_node):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
        return used_names

    @staticmethod
    def _find_refs(obj):
        """再帰的に $ref の値を取得する"""
        refs = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "$ref":
                    refs.add(v)
                else:
                    refs.update(CodeGenerator._find_refs(v))
        elif isinstance(obj, list):
            for item in obj:
                refs.update(CodeGenerator._find_refs(item))
        return refs

    def _generate_merged_openapi_file(
        self, openapi_filepath: str, include_models_dir: str | None
    ):
        """
        $refを用いて、別ファイルを参照しているopenapiファイルを、1つのファイルに統合する
        """

        # モデル内の$refを探索し、componentに置き換え
        def convert_ref_to_stem(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    if key == "$ref" and isinstance(value, str):
                        # stemに置き換え
                        new_dict[key] = (
                            f"#/components/schemas/{Path(value.split('#', 1)[0]).stem}"
                        )
                    else:
                        new_dict[key] = convert_ref_to_stem(value)
                return new_dict
            elif isinstance(data, list):
                return [convert_ref_to_stem(item) for item in data]
            else:
                return data

        with open(openapi_filepath, "r", encoding="utf-8") as f:
            openapi_spec = yaml.safe_load(f)

        # $refのパスを抽出
        refs = self._find_refs(openapi_spec)
        model_files = set(Path(os.path.dirname(openapi_filepath), ref) for ref in refs)

        if include_models_dir:
            # include_models_dir内のファイルパスを取得
            include_model_files = set(
                f for f in Path(include_models_dir).rglob("*") if f.is_file()
            )

            # $refファイルとモデルファイルを統合
            model_files |= include_model_files

        # 抽出した$refが指すファイルからschemaを移動し、$refの値も合わせて変更
        components_schemas = {}
        for model_file in model_files:
            schema_name = model_file.stem
            with open(model_file, "r", encoding="utf-8") as rf:
                ref_spec = yaml.safe_load(rf)
            ref_spec = convert_ref_to_stem(ref_spec)
            components_schemas.update({schema_name: ref_spec})

        # api_spec の components.schemas を置き換え
        openapi_spec["components"] = {"schemas": components_schemas}

        # paths 内の $ref を更新
        def update_refs(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "$ref" and isinstance(v, str):
                        ref_file = Path(v).stem
                        obj[k] = f"#/components/schemas/{ref_file}"
                    else:
                        update_refs(v)
            elif isinstance(obj, list):
                for item in obj:
                    update_refs(item)

        update_refs(openapi_spec["paths"])

        # 統合 YAML を書き出す
        with open(
            os.path.join(self.output_dir, TEMPORARY_API_FILE_NAME),
            "w",
            encoding="utf-8",
        ) as f:
            yaml.safe_dump(openapi_spec, f, sort_keys=False, encoding="utf-8")

    def _generate_temporary_model_file(
        self, temporary_model_filepath: str, parameters: list[str]
    ):
        """
        datamodel-codegenを使用して、一時モデルファイルを生成
        """
        openapi_file_path = Path(self.output_dir, TEMPORARY_API_FILE_NAME).resolve(
            strict=True
        )
        temporary_file_path = Path(temporary_model_filepath).resolve()
        subprocess.run(
            [
                "datamodel-codegen",
                "--input",
                str(openapi_file_path),
                "--input-file-type",
                "openapi",
                "--output",
                str(temporary_file_path),
                *parameters,
            ],
            check=True,
        )  # nosec B603, B607

    @staticmethod
    def _import_temporary_file(temporary_filename: str):
        with open(temporary_filename, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _extract_imports(source_code: str) -> List[ast.Import | ast.ImportFrom]:
        """ソースコードからimport文を抽出し、そのテキストリストを返す"""
        tree = ast.parse(source_code)
        return [
            node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

    @staticmethod
    def _extract_classes(source_code: str) -> List[ast.ClassDef]:
        """ソースコードからトップレベルのクラス定義のASTノードを抽出する"""
        tree = ast.parse(source_code)
        return [node for node in tree.body if isinstance(node, ast.ClassDef)]

    def _convert_to_snake_case(self, string: str):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()
