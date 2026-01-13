#!/bin/bash

export FLIT_INDEX_URL="https://upload.pypi.org/legacy/"
export FLIT_USERNAME="__token__"

# Main script execution
main() {
    echo "CI: ${CI}"
    if [[ "${CI}" == "true" ]]; then
        echo "Push to PyPi!"
        # Retrieve the OIDC token from GitLab CI/CD,
        # and exchange it for a PyPI API token
        oidc_token=$(python -m id PYPI)
        resp=$(curl -X POST https://pypi.org/_/oidc/mint-token \
               -d "{\"token\":\"${oidc_token}\"}")
        api_token=$(jq --raw-output '.token' <<< "${resp}")

        FLIT_PASSWORD="${api_token}" flit publish
    else
        echo "Running local, will not push to PyPi!"
    fi
}

# Execute the main function
main

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: