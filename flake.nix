{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-23.11";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }: flake-utils.lib.eachSystem [
    "x86_64-linux" "x86_64-Darwin"
  ] (system:
      let

      pkgs = import nixpkgs {
        inherit system;
      };

      BuildInputs = [
        pkgs.poetry
        pkgs.python310
        pkgs.python310Packages.virtualenv
        pkgs.stdenv.cc.cc.lib
        pkgs.zlib
      ];

      in rec {

      devShell = pkgs.mkShell {
        name = "kmviz";
        buildInputs = BuildInputs;
        shellHook = ''
           export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath BuildInputs}:$LD_LIBRARY_PATH"
           export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH"
         '';
      };
    }
  );
}
