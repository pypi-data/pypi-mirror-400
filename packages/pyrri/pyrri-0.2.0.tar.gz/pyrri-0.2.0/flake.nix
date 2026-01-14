{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs = { self, nixpkgs, ... }: {
    packages.x86_64-linux = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
    in {
      pyrri = pkgs.python3Packages.buildPythonPackage rec {
        pname = "pyrri";
        version = "0.2.0";

        src = ./.;

        format = "pyproject";

        buildInputs = [ pkgs.python3Packages.hatchling ];

        pythonImportsCheck = [ "rri" ];

        meta.mainProgram = "rri";
      };
      default = self.packages.x86_64-linux.pyrri;
    };

    devShells.x86_64-linux = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
    in {
      pyrri = pkgs.mkShell {
        packages = with pkgs; [ hatch ];
        inputsFrom = [
          self.packages.x86_64-linux.pyrri
        ];
      };
      default = self.devShells.x86_64-linux.pyrri;
    };

    hydraJobs = {
      inherit (self)
        packages;
    };
  };
}
