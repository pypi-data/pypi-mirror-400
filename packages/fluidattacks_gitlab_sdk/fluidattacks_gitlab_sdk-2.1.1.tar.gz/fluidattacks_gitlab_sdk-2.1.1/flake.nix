{
  description = "Singer target for fluidattacks warehouse";

  inputs = {
    observes_flake_builder = {
      url =
        "git+ssh://git@gitlab.com/fluidattacks/universe?shallow=1&rev=28bda83eeda56c9c4016f43c86aaf93a366446c3&dir=observes/common/std_flake_2";
    };
  };

  outputs = { self, ... }@inputs:
    let
      build_args = { system, python_version, nixpkgs, builders, scripts }:
        import ./build {
          inherit nixpkgs builders scripts;
          src = import ./build/filter.nix nixpkgs.nix-filter self;
        };
    in { packages = inputs.observes_flake_builder.outputs.build build_args; };
}
