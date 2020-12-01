#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

function doCompile {
  echo "Running script..."
  python3 -m magic_spoiler
}

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [[ ! -d $OUTPUT_PATH ]]; then
  mkdir "$OUTPUT_PATH"
  echo "Skipping deploy; just doing a build."
  # Run our compile script and let user know in logs
  doCompile
  exit 0
fi

# Run our compile script and exit gracefully if there are no updates
if ! doCompile; then
  echo "::warning::No updates found... skipping file upload!"
  exit 0
fi

cd "$OUTPUT_PATH"
git config user.name github-actions
git config user.email github-actions@github.com

# We don't want the AllSets... waste of space
git add -A .
git commit -m "Deploy: ${GITHUB_SHA}"

# push using built-in token
git push
