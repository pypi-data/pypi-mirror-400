# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady — Development environment
# :Created:   gio 30 giu 2022, 8:29:40
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2022, 2023, 2024, 2025, 2026 Lele Gaifax
#

{
  description = "metapensiero.sqlalchemy.dbloady";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      # Use the same nixpkgs
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, gitignore }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (builtins) fromTOML listToAttrs map readFile;
        pkgs = import nixpkgs { inherit system; };
        inherit (pkgs.lib) flip;
        inherit (gitignore.lib) gitignoreFilterWith;

        pinfo = (fromTOML (readFile ./pyproject.toml)).project;

        getSource = name: path: pkgs.lib.cleanSourceWith {
          name = name;
          src = path;
          filter = gitignoreFilterWith { basePath = path; };
        };

        # List of supported Python versions, see also Makefile
        snakes = flip map [ "313" "314"]
          (ver: rec { name = "python${ver}"; value = builtins.getAttr name pkgs;});

        mkDBLoadyPkg = python: python.pkgs.buildPythonPackage {
          pname = pinfo.name;
          version = pinfo.version;

          src = getSource "dbloady" ./.;
          format = "pyproject";

          nativeBuildInputs = with python.pkgs; [
            pdm-backend
          ];

          propagatedBuildInputs = with python.pkgs; [
            progressbar2
            ruamel-yaml
            sqlalchemy
          ];
        };

        dbloadyPkgs = flip map snakes
          (py: {
            name = "dbloady-${py.name}";
            value = mkDBLoadyPkg py.value;
          });

        mkTestShell = python:
         let
           dbloady = mkDBLoadyPkg python;
           env = python.buildEnv.override {
             extraLibs = [
               dbloady
               python.pkgs.psycopg
             ];
           };
         in pkgs.mkShell {
           name = "Test Python ${python.version}";
           packages = with pkgs; [
             env
             just
             postgresql_18
             sqlite
           ];

           shellHook = ''
             TOP_DIR=$(pwd)
             export PYTHONPATH="$TOP_DIR/src''${PYTHONPATH:+:}$PYTHONPATH"
             trap "$TOP_DIR/tests/postgresql stop" EXIT
           '';
         };

        testShells = flip map snakes
          (py: {
            name = "test-${py.name}";
            value = mkTestShell py.value;
          });
      in {
        devShells = {
          default = pkgs.mkShell {
            name = "Dev shell";

            packages = (with pkgs; [
              bump-my-version
              just
              python3
              twine
            ]) ++ (with pkgs.python3Packages; [
              build
            ]);

            shellHook = ''
               TOP_DIR=$(pwd)
               export PYTHONPATH="$TOP_DIR/src''${PYTHONPATH:+:}$PYTHONPATH"
               trap "$TOP_DIR/tests/postgresql stop" EXIT
             '';
          };
        } // (listToAttrs testShells);

        lib = {
          inherit mkDBLoadyPkg;
        };

        packages = listToAttrs dbloadyPkgs;
      });
}
