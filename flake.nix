{
  description = "Flake using pyproject.toml metadata with uv for development";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    { nixpkgs, pyproject-nix, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      project = pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };

      pythonAttr = "python310";
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.${pythonAttr};
        in
        {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.uv
              pkgs.chromium
              pkgs.chromedriver
            ];

            shellHook = ''
              export UV_PYTHON=${python.interpreter}
              export UV_PROJECT_ENVIRONMENT=.venv
              export CHROME_BINARY=${pkgs.chromium}/bin/chromium
              export CHROMEDRIVER_PATH=${pkgs.chromedriver}/bin/chromedriver
              export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH
              echo "Environment ready. Run 'uv sync' to set up the virtualenv."
              if [ -d .venv ]; then
                .venv/bin/python -m ipykernel install --user \
                  --name guion-dashboard \
                  --display-name "Guion Dashboard (Python 3.10)"
              fi
            '';
          };
        }
      );

      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.${pythonAttr};
        in
        {
          default =
            python.pkgs.buildPythonPackage (
              project.renderers.buildPythonPackage {
                inherit python;
              }
            );
        }
      );
    };
}
