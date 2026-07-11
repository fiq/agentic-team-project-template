{
  description = "AI-first project template development shell and checks";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f:
        builtins.listToAttrs (map (system: {
          name = system;
          value = f system;
        }) systems);
    in {
      checks = forAllSystems (system: {
        repo-contract =
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
            pkgs.runCommand "repo-contract" {
              nativeBuildInputs = [ pkgs.bash pkgs.gnumake pkgs.python3 ];
            } ''
              cp -r ${self} source
              chmod -R u+w source
              cd source
              patchShebangs scripts
              make check
              touch $out
            '';
      });

      devShells = forAllSystems (system: {
        default =
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
          pkgs.mkShell {
            packages = [
              pkgs.git
              pkgs.gnumake
              pkgs.jq
              pkgs.python3
              pkgs.ripgrep
            ];

          shellHook = ''
            echo "AI-first template shell: use make help"
          '';
          };
      });
    };
}
