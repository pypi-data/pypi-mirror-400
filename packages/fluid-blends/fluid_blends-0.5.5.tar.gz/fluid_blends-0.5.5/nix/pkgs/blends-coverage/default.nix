{ pkgs }:
pkgs.writeShellApplication {
  name = "blends-coverage";
  runtimeInputs = [ pkgs.python311Packages.coverage ];
  text = ''
    pushd blends
    coverage combine
    coverage report --fail-under='60.00' --precision=2
    popd

  '';
}
