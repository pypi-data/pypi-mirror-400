#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
REPO_DIR="$(readlink -f "${SCRIPT_DIR}/..")"
PUBLIC_DIR="${REPO_DIR}/public"

# Main script execution
main() {
    mkdir -p "${PUBLIC_DIR}"
    libdoc --pythonpath ./src  Relukko  "${PUBLIC_DIR}/index.html"
}

# Execute the main function
main

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: