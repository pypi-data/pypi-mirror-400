#!/bin/bash
# Setup script to install the pre-commit hook for automatic version increment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/..")"
HOOK_SOURCE="$SCRIPT_DIR/pre-commit"
HOOK_TARGET="$PROJECT_ROOT/.git/hooks/pre-commit"

# Check if we're in a git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "Error: Not in a git repository. Please run this script from within the repository root."
    exit 1
fi

# Check if source hook exists
if [ ! -f "$HOOK_SOURCE" ]; then
    echo "Error: Pre-commit hook source not found at $HOOK_SOURCE"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p "$(dirname "$HOOK_TARGET")"

# Copy the hook
cp "$HOOK_SOURCE" "$HOOK_TARGET"
chmod +x "$HOOK_TARGET"

echo "✓ Pre-commit hook installed successfully!"
echo "  Source: $HOOK_SOURCE"
echo "  Target: $HOOK_TARGET"
echo ""
echo "The hook will now automatically increment the patch version on each commit."

