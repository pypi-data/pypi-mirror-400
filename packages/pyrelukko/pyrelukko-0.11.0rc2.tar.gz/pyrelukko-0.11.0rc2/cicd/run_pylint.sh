#!/bin/bash

# Main script execution
main() {
    tox run -e pylint
}

# Execute the main function
main

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: