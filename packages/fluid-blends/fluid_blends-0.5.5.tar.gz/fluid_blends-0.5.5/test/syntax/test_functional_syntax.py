import json
from pathlib import Path

import pytest

from blends.graph import get_graphs_from_path
from blends.models import Graph


def export_graph_as_json(graph: Graph) -> dict[str, dict[str, dict[str, dict[str, str]]]]:
    data: dict[str, dict[str, dict[str, dict[str, str]]]] = {}
    data["nodes"] = {}
    data["edges"] = {}

    for n_id, n_attrs in graph.nodes.items():
        data["nodes"][n_id] = n_attrs.copy()

    for n_id_from, n_id_to in graph.edges:
        data["edges"].setdefault(n_id_from, {})
        data["edges"][n_id_from][n_id_to] = graph[n_id_from][n_id_to].copy()

    return data


@pytest.mark.blends_test_group("functional")
@pytest.mark.parametrize(  # type: ignore[misc,attr-defined]
    ("test_file", "expected_suffix"),
    [
        ("c_sharp.cs", "c_sharp"),
        ("dart.dart", "dart"),
        ("go.go", "go"),
        ("terraform.tf", "hcl"),
        ("java.java", "java"),
        ("javascript.js", "javascript"),
        ("json.json", "json"),
        ("kotlin.kt", "kotlin"),
        ("php.php", "php"),
        ("python.py", "python"),
        ("ruby.rb", "ruby"),
        ("scala.scala", "scala"),
        ("swift.swift", "swift"),
        ("syntax_cfg.ts", "typescript"),
        ("yaml.yaml", "yaml"),
    ],
)
def test_syntax_graph_generation(test_file: str, expected_suffix: str) -> None:  # type: ignore[misc]
    test_data_dir = Path(__file__).parent.parent / "data"
    test_file_path = test_data_dir / "test_files" / test_file

    graphs = get_graphs_from_path(test_file_path)

    assert graphs.ast_graph is not None, f"AST graph is None for {test_file}"
    assert graphs.syntax_graph is not None, f"Syntax graph is None for {test_file}"

    relative_test_path = f"test/data/test_files/{test_file}"

    graph_db: dict[str, dict[str, dict[str, Graph]]] = {
        "graphs": {
            relative_test_path: {
                "graph": graphs.ast_graph,
                "syntax_graph": graphs.syntax_graph,
            },
        },
    }

    graph_db_as_json_str = json.dumps(
        graph_db,
        indent=2,
        sort_keys=True,
        default=export_graph_as_json,
    )

    expected_path = test_data_dir / "results" / f"root-graph_{expected_suffix}.json"

    if expected_path.exists():
        with expected_path.open(encoding="utf-8") as handle:
            expected_graph = handle.read()

        if expected_graph != graph_db_as_json_str:
            with expected_path.open("w", encoding="utf-8") as handle_w:
                handle_w.write(graph_db_as_json_str)
            pytest.fail(f"Graph DB mismatch for suffix: {expected_suffix}")  # type: ignore[attr-defined]
    else:
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        with expected_path.open("w", encoding="utf-8") as handle:
            handle.write(graph_db_as_json_str)
        pytest.fail(  # type: ignore[attr-defined]
            f"Expected file did not exist, created it: {expected_path}. "
            "Please review and commit if correct."
        )
