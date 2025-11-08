{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.poetry
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.openssl
      pkgs.sqlite
    ];
    POETRY_VIRTUALENVS_IN_PROJECT = "true";
  };
}