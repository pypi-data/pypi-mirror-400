{ inputs, pkgs, projectPath }:
let
  python = pkgs.python311;
  workspaceRoot = projectPath "/";

  pythonEnv = let
    commonOverlay = final: prev: {
      tree-sitter-dart-orchard = prev.tree-sitter-dart-orchard.overrideAttrs
        (old: {
          nativeBuildInputs = old.nativeBuildInputs
            ++ final.resolveBuildSystem { setuptools = [ ]; };
        });
    };
  in {
    default = inputs.python-env.lib.mkPythonEnv {
      inherit pkgs python workspaceRoot;
      extraOverlays = [ commonOverlay ];
    };

    editable = inputs.python-env.lib.mkPythonEnv {
      inherit pkgs python workspaceRoot;
      editableRoot = "$PWD";
      extraOverlays = [
        commonOverlay
        (final: prev: {
          blends = prev.blends.overrideAttrs (old: {
            src = pkgs.lib.fileset.toSource {
              root = old.src;
              fileset = pkgs.lib.fileset.unions [
                (old.src + "/blends")
                (old.src + "/pyproject.toml")
                (old.src + "/test")
              ];
            };
            nativeBuildInputs = old.nativeBuildInputs
              ++ prev.resolveBuildSystem { editables = [ ]; };
          });
        })
      ];
    };
  };
in {
  default = pythonEnv.default.mkVirtualEnv "blends"
    pythonEnv.default.workspace.deps.default;
  editable = pythonEnv.editable.mkVirtualEnv "blends"
    pythonEnv.editable.workspace.deps.all;
}
