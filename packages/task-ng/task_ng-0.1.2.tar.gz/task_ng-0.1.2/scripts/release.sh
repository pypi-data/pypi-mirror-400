#!/usr/bin/env bash
# Release script for task-ng
# Automatically bumps version, commits, tags, and pushes to trigger PyPI deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYPROJECT_FILE="$PROJECT_ROOT/pyproject.toml"

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <version>

Automate the release process for task-ng:
  1. Update version in pyproject.toml
  2. Commit the version change
  3. Create a git tag
  4. Push commit and tag (triggers GitLab CI → PyPI deployment)

Arguments:
  <version>     New version number (e.g., 0.1.2, 1.0.0)
                Can also use: major, minor, patch for auto-increment

Options:
  -h, --help    Show this help message
  -n, --dry-run Show what would be done without making changes
  -f, --force   Skip confirmation prompts

Examples:
  $0 0.2.0              # Set version to 0.2.0
  $0 patch              # Increment patch version (0.1.1 → 0.1.2)
  $0 minor              # Increment minor version (0.1.1 → 0.2.0)
  $0 major              # Increment major version (0.1.1 → 1.0.0)
  $0 --dry-run 0.2.0    # Preview changes without executing
EOF
}

# Parse current version from pyproject.toml
get_current_version() {
    grep -E '^version = ' "$PYPROJECT_FILE" | sed -E 's/version = "(.*)"/\1/'
}

# Validate version format (semantic versioning)
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Expected format: X.Y.Z (e.g., 0.1.2, 1.0.0)"
        return 1
    fi
    return 0
}

# Increment version based on bump type
increment_version() {
    local current=$1
    local bump_type=$2

    IFS='.' read -r major minor patch <<< "$current"

    case $bump_type in
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
            log_error "Invalid bump type: $bump_type"
            return 1
            ;;
    esac
}

# Update version in pyproject.toml
update_version() {
    local new_version=$1
    local temp_file="${PYPROJECT_FILE}.tmp"

    sed "s/^version = \".*\"/version = \"${new_version}\"/" "$PYPROJECT_FILE" > "$temp_file"
    mv "$temp_file" "$PYPROJECT_FILE"
}

# Check if working directory is clean
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        log_error "Working directory is not clean. Commit or stash changes first."
        git status --short
        return 1
    fi
    return 0
}

# Check if we're on main/master branch
check_git_branch() {
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD)

    if [[ "$branch" != "main" && "$branch" != "master" ]]; then
        log_warning "You're on branch '$branch', not 'main' or 'master'"
        if [[ "$FORCE" == "false" ]]; then
            read -rp "Continue anyway? [y/N] " response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                log_info "Release cancelled"
                exit 0
            fi
        fi
    fi
}

# Check if tag already exists
check_tag_exists() {
    local tag=$1
    if git rev-parse "$tag" >/dev/null 2>&1; then
        log_error "Tag '$tag' already exists"
        return 1
    fi
    return 0
}

# Main release function
do_release() {
    local new_version=$1
    local current_version
    local tag_name="v${new_version}"

    log_info "Starting release process..."
    echo

    # Get current version
    current_version=$(get_current_version)
    log_info "Current version: $current_version"
    log_info "New version: $new_version"
    echo

    # Validate new version
    if ! validate_version "$new_version"; then
        exit 1
    fi

    # Check if new version is greater than current
    if [[ "$new_version" == "$current_version" ]]; then
        log_error "New version ($new_version) is the same as current version"
        exit 1
    fi

    # Preflight checks (skip in dry-run mode)
    if [[ "$DRY_RUN" == "false" ]]; then
        check_git_status || exit 1
        check_git_branch
        check_tag_exists "$tag_name" || exit 1
    fi

    # Show what will be done
    log_info "The following changes will be made:"
    echo "  1. Update version in pyproject.toml: $current_version → $new_version"
    echo "  2. Commit: 'Bump version to $new_version'"
    echo "  3. Create tag: $tag_name"
    echo "  4. Push to remote (triggers GitLab CI → PyPI deployment)"
    echo

    # Confirm (unless forced)
    if [[ "$FORCE" == "false" && "$DRY_RUN" == "false" ]]; then
        read -rp "Proceed with release? [y/N] " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Release cancelled"
            exit 0
        fi
        echo
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
        exit 0
    fi

    # Execute release steps
    log_info "Step 1: Updating version in pyproject.toml..."
    update_version "$new_version"
    log_success "Updated pyproject.toml"

    log_info "Step 2: Committing changes..."
    git add "$PYPROJECT_FILE"
    # Use poetry run if available to ensure pre-commit hooks work
    if command -v poetry &> /dev/null && [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        poetry run git commit -m "Bump version to $new_version"
    else
        git commit -m "Bump version to $new_version"
    fi
    log_success "Created commit"

    log_info "Step 3: Creating tag $tag_name..."
    git tag -a "$tag_name" -m "Release $new_version"
    log_success "Created tag $tag_name"

    log_info "Step 4: Pushing to remote..."
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD)
    git push origin "$branch"
    git push origin "$tag_name"
    log_success "Pushed commit and tag to remote"

    echo
    log_success "Release $new_version complete!"
    echo
    log_info "GitLab CI will now:"
    echo "  1. Run tests and quality checks"
    echo "  2. Build the package"
    echo "  3. Publish to PyPI"
    echo
    log_info "Monitor the pipeline at:"
    log_info "https://gitlab.com/<your-project>/pipelines"
    echo
    log_info "Once published, install with:"
    echo "  pip install --upgrade task-ng"
}

# Parse arguments
DRY_RUN=false
FORCE=false
VERSION_ARG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            echo
            show_usage
            exit 1
            ;;
        *)
            VERSION_ARG=$1
            shift
            ;;
    esac
done

# Validate arguments
if [[ -z "$VERSION_ARG" ]]; then
    log_error "Missing version argument"
    echo
    show_usage
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    log_error "git is not installed or not in PATH"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
fi

# Check if pyproject.toml exists
if [[ ! -f "$PYPROJECT_FILE" ]]; then
    log_error "pyproject.toml not found at: $PYPROJECT_FILE"
    exit 1
fi

# Determine target version
case $VERSION_ARG in
    major|minor|patch)
        CURRENT_VERSION=$(get_current_version)
        NEW_VERSION=$(increment_version "$CURRENT_VERSION" "$VERSION_ARG")
        ;;
    *)
        NEW_VERSION=$VERSION_ARG
        ;;
esac

# Execute release
do_release "$NEW_VERSION"
