#!/bin/bash
# TypeFast One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/typefast/main/install.sh | bash

set -e

echo "🎹 Installing TypeFast..."

# Download typefast.py
curl -sSL -O https://raw.githubusercontent.com/YOUR_USERNAME/typefast/main/typefast.py

# Make executable
chmod +x typefast.py

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install asciichartpy --break-system-packages 2>/dev/null || pip3 install asciichartpy 2>/dev/null || echo "Note: Could not install asciichartpy (optional)"
else
    echo "Note: pip3 not found. Install manually: pip3 install asciichartpy --break-system-packages"
fi

echo "✓ TypeFast installed successfully!"
echo ""
echo "To start practicing:"
echo "  python3 typefast.py"
echo ""
echo "Or move to your PATH:"
echo "  sudo mv typefast.py /usr/local/bin/typefast"
echo "  typefast"
