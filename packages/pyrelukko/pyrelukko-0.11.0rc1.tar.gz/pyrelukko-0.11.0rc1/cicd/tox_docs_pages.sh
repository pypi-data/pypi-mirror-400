#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
REPO_DIR="$(readlink -f "${SCRIPT_DIR}/..")"
PUBLIC_DIR="${REPO_DIR}/public"
DOCS_DIR="${REPO_DIR}/docs"

# Main script execution
main() {
    rm -rf "${PUBLIC_DIR}"
    mkdir -p "${PUBLIC_DIR}"
    sphinx-build --jobs auto --builder html --write-all "${DOCS_DIR}" "${PUBLIC_DIR}"
}

# Execute the main function
main

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: