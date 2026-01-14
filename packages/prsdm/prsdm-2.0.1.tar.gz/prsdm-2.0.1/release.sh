#!/bin/bash

# Release script: Bump version, create annotated tag, commit, and push
# Usage: ./release.sh [patch|minor|major]

set -e  # Exit on error

# Get bump type (default: patch)
BUMP_TYPE="${1:-patch}"

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Error: Bump type must be 'patch', 'minor', or 'major'"
    echo "Usage: ./release.sh [patch|minor|major]"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Get current version
OLD_VERSION=$(grep '^version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')

# Bump version
uv version --bump "$BUMP_TYPE"

# Get new version
NEW_VERSION=$(grep '^version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')

echo "Version bumped: $OLD_VERSION → $NEW_VERSION"

# Stage version change
git add pyproject.toml

# Create tag name (use same as commit message, like OpenAI)
TAG_NAME="v${NEW_VERSION}"

# Commit with tag name as message (like OpenAI: just "v0.0.4")
git commit -m "$TAG_NAME"

# Create annotated tag with same message
git tag -a "$TAG_NAME" -m "$TAG_NAME"

# Push commit and tag
git push --follow-tags

echo "✅ Released $TAG_NAME"
echo "📦 Next step: Create GitHub Release at https://github.com/hypertic-ai/test/releases/new?tag=$TAG_NAME"

