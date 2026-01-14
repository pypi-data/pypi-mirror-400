from pathlib import Path

import pytest

from blends.models import Content, Graph, Language
from blends.syntax.build_graph import generic, get_syntax_graph
from blends.syntax.models import SyntaxGraphArgs, SyntaxMetadata


@pytest.mark.blends_test_group("syntax_unittesting")
def test_get_syntax_graph_returns_graph_with_valid_input() -> None:
    content = Content(
        content_bytes=b"def hello():\n    return 'world'",
        content_str="def hello():\n    return 'world'",
        language=Language.PYTHON,
        path=Path("test.py"),
    )
    ast_graph = Graph()
    ast_graph.add_node("1", label_type="module")

    result = get_syntax_graph(ast_graph, content)

    assert result is not None
    assert isinstance(result, Graph)
    assert len(result.nodes) > 0


@pytest.mark.blends_test_group("syntax_unittesting")
def test_get_syntax_graph_with_metadata_flag() -> None:
    content = Content(
        content_bytes=b"x = 1",
        content_str="x = 1",
        language=Language.PYTHON,
        path=Path("test.py"),
    )
    ast_graph = Graph()
    ast_graph.add_node("1", label_type="module")

    result = get_syntax_graph(ast_graph, content, with_metadata=True)

    assert result is not None
    assert "0" in result.nodes
    assert result.nodes["0"]["label_type"] == "Metadata"
    assert result.nodes["0"]["path"] == "test.py"


@pytest.mark.blends_test_group("syntax_unittesting")
def test_get_syntax_graph_without_metadata_flag() -> None:
    content = Content(
        content_bytes=b"x = 1",
        content_str="x = 1",
        language=Language.PYTHON,
        path=Path("test.py"),
    )
    ast_graph = Graph()
    ast_graph.add_node("1", label_type="module")

    result = get_syntax_graph(ast_graph, content, with_metadata=False)

    assert result is not None
    assert "0" not in result.nodes or result.nodes.get("0", {}).get("label_type") != "Metadata"


@pytest.mark.blends_test_group("syntax_unittesting")
def test_generic_dispatches_to_reader() -> None:
    syntax_graph = Graph()
    ast_graph = Graph()
    ast_graph.add_node("1", label_type="module")

    metadata: SyntaxMetadata = {
        "class_path": [],
        "scope_stack": [],
    }

    args = SyntaxGraphArgs(
        generic=generic,
        path="test.py",
        language=Language.PYTHON,
        ast_graph=ast_graph,
        syntax_graph=syntax_graph,
        n_id="1",
        metadata=metadata,
    )

    result = generic(args)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.blends_test_group("syntax_unittesting")
def test_generic_handles_missing_dispatcher() -> None:
    syntax_graph = Graph()
    ast_graph = Graph()
    ast_graph.add_node("1", label_type="unknown_node_type_xyz")

    metadata: SyntaxMetadata = {
        "class_path": [],
        "scope_stack": [],
    }

    args = SyntaxGraphArgs(
        generic=generic,
        path="test.py",
        language=Language.PYTHON,
        ast_graph=ast_graph,
        syntax_graph=syntax_graph,
        n_id="1",
        metadata=metadata,
    )

    result = generic(args)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.blends_test_group("syntax_unittesting")
def test_get_syntax_graph_with_different_languages() -> None:
    languages_to_test = [
        Language.PYTHON,
        Language.JAVASCRIPT,
        Language.JAVA,
        Language.GO,
    ]

    for language in languages_to_test:
        content = Content(
            content_bytes=b"test",
            content_str="test",
            language=language,
            path=Path(f"test.{language.value}"),
        )
        ast_graph = Graph()
        ast_graph.add_node("1", label_type="module")

        result = get_syntax_graph(ast_graph, content)

        assert result is not None, f"Failed for language {language.value}"
        assert isinstance(result, Graph)
