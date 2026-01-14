from itertools import (
    dropwhile,
)

from blends.ctx import ctx
from blends.models import (
    LANGUAGE_TO_EXTENSIONS,
    NId,
)
from blends.syntax.models import (
    FileInstanceData,
    FileStructData,
    SyntaxGraphArgs,
)
from blends.utilities.strings import (
    split_on_last_dot as split_last,
)


def add_class_to_metadata(args: SyntaxGraphArgs, name: str) -> None:
    parent_class = args.syntax_graph.nodes["0"]["structure"]

    if args.metadata["class_path"]:
        for elem in args.metadata["class_path"]:
            parent_class = parent_class[elem]["data"]

        parent_class[name] = FileStructData(node=args.n_id, type="class", data={})

        args.metadata["class_path"].append(name)
    else:
        parent_class[name] = FileStructData(node=args.n_id, type="class", data={})
        args.metadata["class_path"] = [name]


def add_method_to_metadata(args: SyntaxGraphArgs, name: str) -> None:
    parent_class = args.syntax_graph.nodes["0"]["structure"]

    for elem in args.metadata["class_path"]:
        parent_class = parent_class[elem]["data"]

    parent_class[name] = FileStructData(node=args.n_id, type="method", data=name)


def add_node_range_to_method(args: SyntaxGraphArgs, name: str) -> None:
    parent_class = args.syntax_graph.nodes["0"]["structure"]
    for elem in args.metadata["class_path"]:
        parent_class = parent_class[elem]["data"]
    if method_dict := parent_class.get(name):
        method_dict["node_range"] = list(
            dropwhile(lambda x: x != args.n_id, list(args.syntax_graph.nodes)),
        )


def del_metadata_instance(args: SyntaxGraphArgs, var_id: NId, val_id: NId) -> None:
    val_attrs = args.syntax_graph.nodes[val_id]
    var_attrs = args.syntax_graph.nodes[var_id]

    var = var_attrs.get("symbol")

    current_class = args.metadata["class_path"][-1] if args.metadata["class_path"] else None
    class_instances = (
        args.syntax_graph.nodes["0"]["instances"][current_class]
        if current_class and args.syntax_graph.nodes["0"]["instances"]
        else None
    )

    if not (class_instances and var and class_instances.get(var)):
        return

    if not (
        val_attrs["label_type"] == "ObjectCreation"
        and val_attrs["name"] == class_instances[var]["object"]
    ):
        del class_instances[var]


def get_file_from_path(file_name: str) -> str | None:
    min_path_depth_for_file_search = 4
    if file_name.count("/") >= min_path_depth_for_file_search:
        for config_path in ctx.iterate_multi_paths():
            file_path = str(config_path)
            if file_name in file_path:
                return file_path
    return None


def add_instance_to_metadata(args: SyntaxGraphArgs, var_type: str, var_name: str) -> None:
    current_class = args.metadata["class_path"][-1]
    if current_class not in args.syntax_graph.nodes["0"]["instances"]:
        args.syntax_graph.nodes["0"]["instances"][current_class] = {}

    possible_path = var_type.replace(".", "/") + LANGUAGE_TO_EXTENSIONS[args.language][0]

    if path := get_file_from_path(possible_path):
        args.syntax_graph.nodes["0"]["instances"][current_class][var_name] = FileInstanceData(
            object=split_last(var_type)[1],
            source=path,
            source_type="file_path",
        )

    for imported_package in args.syntax_graph.nodes["0"]["imports"]:
        split_import = split_last(imported_package)
        split_var = split_last(var_type)
        match_names = {imported_package}
        if split_import[1] == "*":
            if split_import[0] == split_var[0]:
                match_names.add(var_type)
        else:
            match_names.add(split_import[1])
        if var_type in match_names:
            args.syntax_graph.nodes["0"]["instances"][current_class][var_name] = FileInstanceData(
                object=var_type,
                source=split_import[0],
                source_type="package",
            )
