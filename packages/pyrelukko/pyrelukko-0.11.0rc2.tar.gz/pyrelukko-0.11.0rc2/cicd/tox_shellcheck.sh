#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
REPO_DIR="$(readlink -f "${SCRIPT_DIR}/..")"

# Main script execution
main() {
    shellcheck "${REPO_DIR}"/cicd/*.sh   
}

# Execute the main function
main

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: