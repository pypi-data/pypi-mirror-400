from blends.models import (
    Language,
)
from blends.syntax.dispatchers.c_sharp import (
    C_SHARP_DISPATCHERS,
)
from blends.syntax.dispatchers.dart import (
    DART_DISPATCHERS,
)
from blends.syntax.dispatchers.go import (
    GO_DISPATCHERS,
)
from blends.syntax.dispatchers.hcl import (
    HCL_DISPATCHERS,
)
from blends.syntax.dispatchers.java import (
    JAVA_DISPATCHERS,
)
from blends.syntax.dispatchers.javascript import (
    JAVASCRIPT_DISPATCHERS,
)
from blends.syntax.dispatchers.json_dispatchers import (
    JSON_DISPATCHERS,
)
from blends.syntax.dispatchers.kotlin import (
    KOTLIN_DISPATCHERS,
)
from blends.syntax.dispatchers.php import (
    PHP_DISPATCHERS,
)
from blends.syntax.dispatchers.python import (
    PYTHON_DISPATCHERS,
)
from blends.syntax.dispatchers.ruby import (
    RUBY_DISPATCHERS,
)
from blends.syntax.dispatchers.scala import (
    SCALA_DISPATCHERS,
)
from blends.syntax.dispatchers.swift import (
    SWIFT_DISPATCHERS,
)
from blends.syntax.dispatchers.typescript import (
    TYPESCRIPT_DISPATCHERS,
)
from blends.syntax.dispatchers.yaml import (
    YAML_DISPATCHERS,
)
from blends.syntax.models import (
    Dispatcher,
)

DISPATCHERS_BY_LANG: dict[Language, Dispatcher] = {
    Language.CSHARP: C_SHARP_DISPATCHERS,
    Language.DART: DART_DISPATCHERS,
    Language.GO: GO_DISPATCHERS,
    Language.HCL: HCL_DISPATCHERS,
    Language.JAVA: JAVA_DISPATCHERS,
    Language.JAVASCRIPT: JAVASCRIPT_DISPATCHERS,
    Language.JSON: JSON_DISPATCHERS,
    Language.KOTLIN: KOTLIN_DISPATCHERS,
    Language.PYTHON: PYTHON_DISPATCHERS,
    Language.PHP: PHP_DISPATCHERS,
    Language.RUBY: RUBY_DISPATCHERS,
    Language.SCALA: SCALA_DISPATCHERS,
    Language.SWIFT: SWIFT_DISPATCHERS,
    Language.TYPESCRIPT: TYPESCRIPT_DISPATCHERS,
    Language.YAML: YAML_DISPATCHERS,
}
