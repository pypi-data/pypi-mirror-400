#!/bin/bash
set -e

# Usage: ./scripts/release.sh 0.2.0

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.2.0"
    exit 1
fi

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 0.2.0)"
    exit 1
fi

# Check for gh CLI
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    echo "  macOS: brew install gh"
    echo "  Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
fi

# Check gh auth status
if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated."
    echo "Run: gh auth login"
    exit 1
fi

echo "Releasing version $VERSION..."

# Update pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update __init__.py
sed -i '' "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" fast_llms_txt/__init__.py

# Show changes
echo ""
echo "Updated files:"
git diff --stat
echo ""
git diff

# Confirm
read -p "Commit and tag v$VERSION? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add pyproject.toml fast_llms_txt/__init__.py
    git commit -m "Bump version to $VERSION"

    echo ""
    echo "Created commit for v$VERSION"
    echo ""

    # Get release notes
    echo "Enter release notes (single line, or leave empty for auto-generated):"
    read -r NOTES

    echo ""
    read -p "Push and create GitHub release? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push

        if [ -z "$NOTES" ]; then
            gh release create "v$VERSION" --generate-notes
        else
            gh release create "v$VERSION" --notes "$NOTES"
        fi

        echo "Released! GitHub Actions will publish to PyPI."
    else
        echo "Commit pushed but no release created."
        echo "Run 'gh release create v$VERSION' when ready."
    fi
else
    echo "Aborted. Reverting changes..."
    git checkout pyproject.toml fast_llms_txt/__init__.py
fi
