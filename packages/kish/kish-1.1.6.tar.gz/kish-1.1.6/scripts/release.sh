#!/usr/bin/env bash
#
# Release script for kish-py
#
# Usage:
#   ./scripts/release.sh 1.0.1        # Release version 1.0.1
#   ./scripts/release.sh patch        # Bump patch: 1.0.0 -> 1.0.1
#   ./scripts/release.sh minor        # Bump minor: 1.0.0 -> 1.1.0
#   ./scripts/release.sh major        # Bump major: 1.0.0 -> 2.0.0
#   ./scripts/release.sh 1.0.1 --dry-run  # Preview without making changes
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Files to update
ROOT_CARGO_TOML="Cargo.toml"
KISH_PY_CARGO_TOML="kish-py/Cargo.toml"
PYPROJECT_TOML="kish-py/pyproject.toml"

# Get current version from root Cargo.toml
get_current_version() {
    grep -m1 '^version' "$ROOT_CARGO_TOML" | sed 's/version = "\(.*\)"/\1/'
}

# Bump version based on type
bump_version() {
    local current="$1"
    local bump_type="$2"

    IFS='.' read -r major minor patch <<< "$current"

    case "$bump_type" in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "${major}.$((minor + 1)).0"
            ;;
        patch)
            echo "${major}.${minor}.$((patch + 1))"
            ;;
        *)
            # Assume it's an explicit version
            echo "$bump_type"
            ;;
    esac
}

# Validate semver format
validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid version format '$version'. Expected: X.Y.Z${NC}"
        exit 1
    fi
}

# Update version in a file
update_version_in_file() {
    local file="$1"
    local old_version="$2"
    local new_version="$3"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/version = \"$old_version\"/version = \"$new_version\"/" "$file"
    else
        sed -i "s/version = \"$old_version\"/version = \"$new_version\"/" "$file"
    fi
}

# Main
main() {
    local dry_run=false
    local version_arg=""

    # Parse arguments
    for arg in "$@"; do
        case "$arg" in
            --dry-run)
                dry_run=true
                ;;
            -h|--help)
                version_arg=""
                break
                ;;
            *)
                version_arg="$arg"
                ;;
        esac
    done

    if [[ -z "$version_arg" ]]; then
        echo "Usage: $0 <version|patch|minor|major> [--dry-run]"
        echo ""
        echo "Examples:"
        echo "  $0 1.2.3       # Set version to 1.2.3"
        echo "  $0 patch       # Bump patch version"
        echo "  $0 minor       # Bump minor version"
        echo "  $0 major       # Bump major version"
        exit 1
    fi

    # Get current and new version
    local current_version
    current_version=$(get_current_version)
    local new_version
    new_version=$(bump_version "$current_version" "$version_arg")

    validate_version "$new_version"

    echo -e "${YELLOW}Current version:${NC} $current_version"
    echo -e "${GREEN}New version:${NC}     $new_version"
    echo ""

    if $dry_run; then
        echo -e "${YELLOW}[DRY RUN] Would update:${NC}"
        echo "  - $ROOT_CARGO_TOML"
        echo "  - $KISH_PY_CARGO_TOML"
        echo "  - $PYPROJECT_TOML"
        echo "  - Create commit: \"Release v$new_version\""
        echo "  - Create tag: v$new_version"
        echo "  - Push to origin with tags"
        exit 0
    fi

    # Check for uncommitted changes
    if ! git diff --quiet HEAD 2>/dev/null; then
        echo -e "${RED}Error: You have uncommitted changes. Please commit or stash them first.${NC}"
        exit 1
    fi

    # Update version in files
    echo "Updating $ROOT_CARGO_TOML..."
    update_version_in_file "$ROOT_CARGO_TOML" "$current_version" "$new_version"

    echo "Updating $KISH_PY_CARGO_TOML..."
    update_version_in_file "$KISH_PY_CARGO_TOML" "$current_version" "$new_version"

    echo "Updating $PYPROJECT_TOML..."
    update_version_in_file "$PYPROJECT_TOML" "$current_version" "$new_version"

    # Git operations
    echo "Creating commit..."
    git add "$ROOT_CARGO_TOML" "$KISH_PY_CARGO_TOML" "$PYPROJECT_TOML"
    git commit -m "Release v$new_version"

    echo "Creating tag v$new_version..."
    git tag "v$new_version"

    echo ""
    echo -e "${GREEN}Release v$new_version prepared!${NC}"
    echo ""
    echo "To publish, run:"
    echo -e "  ${YELLOW}git push origin master --tags${NC}"
    echo ""
    echo "Or to undo:"
    echo -e "  ${YELLOW}git reset --hard HEAD~1 && git tag -d v$new_version${NC}"
}

main "$@"
