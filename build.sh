#!/usr/bin/env bash
# Builds the documentation site into _site/.
#
#   ./build.sh          build
#   ./build.sh serve    build, then serve on http://localhost:8080
#
# The API reference is generated from the nite source. It is read from ./nite-src, which is
# cloned from github.com/nite-net/nite when missing. Set NITE_SRC to use an existing checkout.
set -euo pipefail
cd "$(dirname "$0")"

DOCFX_VERSION=2.81.0

if [[ -n "${NITE_SRC:-}" ]]; then
  ln -sfn "$NITE_SRC" nite-src
elif [[ ! -e nite-src ]]; then
  git clone --depth 1 https://github.com/nite-net/nite nite-src
fi

if ! command -v docfx >/dev/null 2>&1; then
  dotnet tool install --global docfx --version "$DOCFX_VERSION"
  export PATH="$PATH:$HOME/.dotnet/tools"
fi

docfx metadata docfx.json
docfx build docfx.json --warningsAsErrors

if [[ "${1:-}" == "serve" ]]; then
  docfx serve _site --port 8080
fi
