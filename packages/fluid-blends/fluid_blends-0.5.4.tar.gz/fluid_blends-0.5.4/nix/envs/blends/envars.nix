{ pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ ];
  name = "blends-envars";
  text = ''
    export PRODUCT_ID="blends"
  '';
}
