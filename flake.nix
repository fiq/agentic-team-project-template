{
  description = "AI-first project template development shell and checks";

  outputs = { self }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f:
        builtins.listToAttrs (map (system: {
          name = system;
          value = f system;
        }) systems);
    in {
      checks = forAllSystems (system: {
        repo-contract = builtins.derivation {
          name = "repo-contract";
          inherit system;
          builder = "/bin/sh";
          args = [ "-c" "mkdir -p $out" ];
        };
      });

      devShells = forAllSystems (system: {
        default = builtins.derivation {
          name = "agentic-template-shell";
          inherit system;
          builder = "/bin/sh";
          args = [ "-c" "mkdir -p $out" ];
          shellHook = ''
            echo "AI-first template shell: use make help"
          '';
        };
      });
    };
}
