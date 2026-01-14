import tempfile
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from tree_sitter import Node, Point

from blends.ast.build_graph import (
    _build_ast_graph,
    _has_content_node,
    _hash_node,
    _is_node_terminal,
    get_ast_graph_from_path,
)
from blends.models import Content, Graph, Language

if TYPE_CHECKING:
    from collections.abc import Iterator


EXPECTED_NODES_WITH_CHILDREN = 3
EXPECTED_EDGES_WITH_CHILDREN = 2
EXPECTED_LABEL_L_OFFSET = "6"
EXPECTED_LABEL_C_OFFSET = "11"


def create_mock_node(  # noqa: PLR0913
    node_type: str,
    *,
    start_point: tuple[int, int] = (0, 0),
    end_point: tuple[int, int] = (1, 0),
    start_byte: int = 0,
    end_byte: int = 10,
    children: list[Node] | None = None,
    has_error: bool = False,
) -> Node:
    node = Mock(spec=Node)
    node.type = node_type
    node.start_point = Point(*start_point)
    node.end_point = Point(*end_point)
    node.start_byte = start_byte
    node.end_byte = end_byte
    node.children = children or []
    node.has_error = has_error
    node.child_by_field_name = Mock(return_value=None)
    return node


@pytest.mark.blends_test_group("ast_unittesting")
def test_hash_node_consistency() -> None:
    node1 = create_mock_node("function_definition", start_point=(0, 0), end_point=(5, 10))
    node2 = create_mock_node("function_definition", start_point=(0, 0), end_point=(5, 10))

    hash1 = _hash_node(node1)
    hash2 = _hash_node(node2)

    assert hash1 == hash2

    node1 = create_mock_node("function_definition", start_point=(0, 0), end_point=(5, 10))
    node2 = create_mock_node("class_definition", start_point=(0, 0), end_point=(5, 10))

    hash1 = _hash_node(node1)
    hash2 = _hash_node(node2)

    assert hash1 != hash2

    node1 = create_mock_node("function_definition", start_point=(0, 0), end_point=(5, 10))
    node2 = create_mock_node("function_definition", start_point=(1, 0), end_point=(5, 10))

    hash1 = _hash_node(node1)
    hash2 = _hash_node(node2)

    assert hash1 != hash2

    node1 = create_mock_node("function_definition", start_point=(0, 0), end_point=(5, 10))
    node2 = create_mock_node("function_definition", start_point=(0, 0), end_point=(6, 10))

    hash1 = _hash_node(node1)
    hash2 = _hash_node(node2)

    assert hash1 != hash2


@pytest.mark.blends_test_group("ast_unittesting")
def test_is_node_terminal_consistency() -> None:
    node = create_mock_node("flow_mapping")
    assert _is_node_terminal(node, Language.YAML) is True

    node = create_mock_node("single_quote_scalar")
    assert _is_node_terminal(node, Language.YAML) is True

    node = create_mock_node("double_quote_scalar")
    assert _is_node_terminal(node, Language.YAML) is True

    node = create_mock_node("bang")
    assert _is_node_terminal(node, Language.SWIFT) is True

    node = create_mock_node("function_definition")
    assert _is_node_terminal(node, Language.PYTHON) is False
    assert _is_node_terminal(node, Language.JAVASCRIPT) is False
    assert _is_node_terminal(node, Language.JAVA) is False
    assert _is_node_terminal(node, Language.CSHARP) is False
    assert _is_node_terminal(node, Language.GO) is False

    node = create_mock_node("mapping")
    assert _is_node_terminal(node, Language.YAML) is False


@pytest.mark.blends_test_group("ast_unittesting")
def test_has_content_node_consistency() -> None:
    true_cases = [
        (Language.CSHARP, "character_literal"),
        (Language.CSHARP, "predefined_type"),
        (Language.CSHARP, "string_literal"),
        (Language.CSHARP, "verbatim_string_literal"),
        (Language.DART, "list_literal"),
        (Language.DART, "set_or_map_literal"),
        (Language.DART, "string_literal"),
        (Language.GO, "interpreted_string_literal"),
        (Language.JAVASCRIPT, "template_string"),
        (Language.JAVASCRIPT, "regex"),
        (Language.TYPESCRIPT, "template_string"),
        (Language.TYPESCRIPT, "regex"),
        (Language.KOTLIN, "string_literal"),
        (Language.SWIFT, "bang"),
        (Language.YAML, "single_quote_scalar"),
        (Language.YAML, "double_quote_scalar"),
        (Language.YAML, "flow_mapping"),
    ]

    false_cases = [
        (Language.CSHARP, "function_definition"),
        (Language.CSHARP, "class_declaration"),
        (Language.CSHARP, "template_string"),
        (Language.DART, "function_declaration"),
        (Language.DART, "class_definition"),
        (Language.DART, "character_literal"),
        (Language.GO, "function_declaration"),
        (Language.GO, "string_literal"),
        (Language.GO, "template_string"),
        (Language.JAVASCRIPT, "function_declaration"),
        (Language.JAVASCRIPT, "string_literal"),
        (Language.JAVASCRIPT, "class_declaration"),
        (Language.TYPESCRIPT, "function_declaration"),
        (Language.TYPESCRIPT, "string_literal"),
        (Language.TYPESCRIPT, "class_declaration"),
        (Language.KOTLIN, "function_declaration"),
        (Language.KOTLIN, "class_declaration"),
        (Language.KOTLIN, "template_string"),
        (Language.SWIFT, "function_declaration"),
        (Language.SWIFT, "string_literal"),
        (Language.SWIFT, "class_declaration"),
        (Language.YAML, "mapping"),
        (Language.YAML, "sequence"),
        (Language.YAML, "function_definition"),
        (Language.PYTHON, "string_literal"),
        (Language.PYTHON, "function_definition"),
        (Language.PYTHON, "template_string"),
        (Language.JAVA, "string_literal"),
        (Language.JAVA, "function_definition"),
        (Language.JAVA, "class_declaration"),
        (Language.PHP, "string_literal"),
        (Language.PHP, "function_definition"),
        (Language.RUBY, "string_literal"),
        (Language.RUBY, "function_definition"),
        (Language.SCALA, "string_literal"),
        (Language.SCALA, "function_definition"),
        (Language.HCL, "string_literal"),
        (Language.HCL, "function_definition"),
        (Language.JSON, "string_literal"),
        (Language.JSON, "function_definition"),
    ]

    for language, node_type in true_cases:
        node = create_mock_node(node_type)
        assert _has_content_node(node, language) is True, (
            f"Expected True for {language.value} with node type {node_type}"
        )

    for language, node_type in false_cases:
        node = create_mock_node(node_type)
        assert _has_content_node(node, language) is False, (
            f"Expected False for {language.value} with node type {node_type}"
        )


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_single_node() -> None:
    content = Content(b"test", "test", Language.PYTHON, Path("test.py"))
    node = create_mock_node("module", start_byte=0, end_byte=4)
    counter = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, node, counter, graph)

    assert len(result.nodes) == 1
    assert "1" in result.nodes
    assert result.nodes["1"]["label_type"] == "module"
    assert result.nodes["1"]["label_l"] == "1"
    assert result.nodes["1"]["label_c"] == "1"


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_with_children() -> None:
    child1 = create_mock_node(
        "child1", start_byte=0, end_byte=2, start_point=(0, 0), end_point=(0, 2)
    )
    child2 = create_mock_node(
        "child2", start_byte=3, end_byte=5, start_point=(0, 3), end_point=(0, 5)
    )
    parent = create_mock_node("parent", children=[child1, child2], start_byte=0, end_byte=5)

    content = Content(b"test", "test", Language.PYTHON, Path("test.py"))
    counter = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, parent, counter, graph)

    assert len(result.nodes) == EXPECTED_NODES_WITH_CHILDREN
    assert len(result.edges) == EXPECTED_EDGES_WITH_CHILDREN


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_terminal_node_has_text() -> None:
    content = Content(b"hello", "hello", Language.PYTHON, Path("test.py"))
    node = create_mock_node("string", start_byte=0, end_byte=5, children=[])
    counter: Iterator[str] = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, node, counter, graph)

    assert "label_text" in result.nodes["1"]
    assert result.nodes["1"]["label_text"] == "hello"


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_non_terminal_node_no_text() -> None:
    child = create_mock_node("child", start_byte=0, end_byte=2, children=[])
    parent = create_mock_node("parent", children=[child], start_byte=0, end_byte=2)

    content = Content(b"ab", "ab", Language.PYTHON, Path("test.py"))
    counter = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, parent, counter, graph)

    assert "label_text" not in result.nodes["1"]


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_edges_have_correct_labels() -> None:
    child = create_mock_node("child", start_byte=0, end_byte=2, children=[])
    parent = create_mock_node("parent", children=[child], start_byte=0, end_byte=2)

    content = Content(b"ab", "ab", Language.PYTHON, Path("test.py"))
    counter = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, parent, counter, graph)

    edges = list(result.edges(data=True))
    assert len(edges) == 1
    edge_data = edges[0][2]
    assert edge_data["label_ast"] == "AST"
    assert edge_data["label_index"] == "0"


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_node_attributes() -> None:
    content = Content(b"test", "test", Language.PYTHON, Path("test.py"))
    node = create_mock_node(
        "function_definition", start_point=(5, 10), end_point=(10, 20), start_byte=0, end_byte=4
    )
    counter: Iterator[str] = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, node, counter, graph)

    assert result.nodes["1"]["label_l"] == EXPECTED_LABEL_L_OFFSET
    assert result.nodes["1"]["label_c"] == EXPECTED_LABEL_C_OFFSET
    assert result.nodes["1"]["label_type"] == "function_definition"


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_not_implemented_error() -> None:
    content = Content(b"test", "test", Language.PYTHON, Path("test.py"))
    invalid_node = "not a node"
    counter = map(str, count(1))
    graph = Graph()

    with pytest.raises(NotImplementedError):
        _build_ast_graph(content, invalid_node, counter, graph)  # type: ignore[arg-type]


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_yaml_terminal_node() -> None:
    content = Content(b"value", "value", Language.YAML, Path("test.yaml"))
    node = create_mock_node("single_quote_scalar", start_byte=0, end_byte=5, children=[])
    counter: Iterator[str] = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, node, counter, graph)

    assert "label_text" in result.nodes["1"]
    assert result.nodes["1"]["label_text"] == "value"


@pytest.mark.blends_test_group("ast_unittesting")
def test_build_ast_graph_has_content_node_includes_text() -> None:
    content = Content(b"hello", "hello", Language.JAVASCRIPT, Path("test.js"))
    child = create_mock_node("child_node", start_byte=0, end_byte=2, children=[])
    node = create_mock_node("template_string", start_byte=0, end_byte=5, children=[child])
    counter = map(str, count(1))
    graph = Graph()

    result = _build_ast_graph(content, node, counter, graph)

    assert "label_text" in result.nodes["1"]
    assert result.nodes["1"]["label_text"] == "hello"


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_python_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.py"
        test_content = "def hello():\n    return 'world'"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_javascript_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.js"
        test_content = "function test() { return true; }"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_go_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.go"
        test_content = "package main\n\nfunc main() {}"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_yaml_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.yaml"
        test_content = "key: value\nother: data"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_nonexistent_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_file = Path(temp_dir) / "nonexistent.py"

        result = get_ast_graph_from_path(non_existent_file)

        assert result is None


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_unsupported_language() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.unknown"
        test_file.write_text("some content", encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is None


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_empty_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "empty.py"
        test_file.touch()

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_java_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "Test.java"
        test_content = "public class Test { }"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_typescript_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.ts"
        test_content = "const x: number = 42;"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0


@pytest.mark.blends_test_group("ast_unittesting")
def test_get_ast_graph_from_path_valid_csharp_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "Test.cs"
        test_content = "public class Test { }"
        test_file.write_text(test_content, encoding="utf-8")

        result = get_ast_graph_from_path(test_file)

        assert result is not None
        assert isinstance(result, Graph)
        assert len(result.nodes) > 0
