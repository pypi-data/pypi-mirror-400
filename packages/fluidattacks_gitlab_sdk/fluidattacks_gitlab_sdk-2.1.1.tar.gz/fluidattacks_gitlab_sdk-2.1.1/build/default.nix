{ nixpkgs, builders, scripts, src, }: {
  inherit src;
  root_path = "observes/sdk/gitlab";
  module_name = "fluidattacks_gitlab_sdk";
  pypi_token_var = "GITLAB_SDK_TOKEN";
  override = b: b;
}
