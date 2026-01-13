#!/usr/bin/env bash
# Toolcase PyPI deployment script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"

cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[x]${NC} $1" >&2; exit 1; }

# Parse args
TESTPYPI=false
SKIP_BUILD=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --test) TESTPYPI=true; shift ;;
        --skip-build) SKIP_BUILD=true; shift ;;
        *) err "Unknown option: $1" ;;
    esac
done

# Ensure tools
command -v python3 &>/dev/null || err "python3 required"
python3 -c "import build" 2>/dev/null || { log "Installing build..."; pip install build; }
python3 -c "import twine" 2>/dev/null || { log "Installing twine..."; pip install twine; }

# Clean old builds
if [[ "$SKIP_BUILD" == false ]]; then
    log "Cleaning dist/"
    rm -rf "$DIST_DIR"
    
    log "Building package..."
    python3 -m build
fi

# Verify dist exists
[[ -d "$DIST_DIR" ]] || err "No dist/ directory found. Run without --skip-build"
WHEELS=($(ls "$DIST_DIR"/*.whl 2>/dev/null))
TARBALLS=($(ls "$DIST_DIR"/*.tar.gz 2>/dev/null))
[[ ${#WHEELS[@]} -gt 0 && ${#TARBALLS[@]} -gt 0 ]] || err "Missing wheel or tarball in dist/"

log "Built artifacts:"
ls -la "$DIST_DIR"

# Check twine
log "Validating with twine check..."
python3 -m twine check "$DIST_DIR"/*

# Upload
if [[ "$TESTPYPI" == true ]]; then
    log "Uploading to TestPyPI..."
    python3 -m twine upload --repository testpypi "$DIST_DIR"/*
    echo -e "\n${GREEN}Published to TestPyPI!${NC}"
    echo "Install: pip install -i https://test.pypi.org/simple/ toolcase"
else
    log "Uploading to PyPI..."
    python3 -m twine upload "$DIST_DIR"/*
    echo -e "\n${GREEN}Published to PyPI!${NC}"
    echo "Install: pip install toolcase"
fi
