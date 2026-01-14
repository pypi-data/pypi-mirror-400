#!/usr/bin/env bash

set -euo pipefail

# if ! git diff --quiet || ! git diff --cached --quiet; then
#     commit_msg="chore: auto-commit before tagging $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
#     git add -A
#     git commit -m "$commit_msg"
# fi

# bash delete_version_tag.sh 0.2.7

# bash local-ci.sh create-tag

# bash deploy_gitlab.sh

# PYPI_TOKEN="" bash local-ci.sh deploy
