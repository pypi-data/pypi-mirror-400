#!/bin/bash
# Setup script for automated changelog generation

set -e

echo "🚀 Setting up automated changelog generation..."
echo ""

# Check if git-cliff is installed
if ! command -v git-cliff &>/dev/null; then
    echo "⚠️  git-cliff not found. Installing..."

    # Try cargo first
    if command -v cargo &>/dev/null; then
        cargo install git-cliff
    # Try homebrew on macOS
    elif command -v brew &>/dev/null; then
        brew install git-cliff
    else
        echo "❌ Please install git-cliff manually:"
        echo "   - Via cargo: cargo install git-cliff"
        echo "   - Via brew: brew install git-cliff"
        echo "   - Download binary: https://github.com/orhun/git-cliff/releases"
        exit 1
    fi
fi

echo "✅ git-cliff is installed"
echo ""

# Generate initial changelog
echo "📝 Generating initial changelog..."
cd "$(dirname "$0")/.."
git-cliff --config cliff.toml --output docs/changelog.md

echo ""
echo "✅ Changelog generated at docs/changelog.md"
echo ""

# Optional: Install commitizen for Python
read -p "Do you want to install commitizen (Python tool for conventional commits)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install commitizen
    echo "✅ Commitizen installed"
    echo ""
    echo "📚 Usage:"
    echo "   cz commit          - Interactive commit"
    echo "   cz bump --changelog - Bump version and update changelog"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Read CHANGELOG_AUTOMATION_GUIDE.md for detailed instructions"
echo "   2. Use conventional commits: git commit -m 'feat(api): add new feature'"
echo "   3. Generate changelog: git-cliff --config cliff.toml --output docs/changelog.md"
echo "   4. Or push a new tag for automatic generation via GitHub Actions"
echo ""
