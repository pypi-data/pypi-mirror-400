#!/bin/bash
# Build script for all ANNS algorithms

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Building SAGE ANNS algorithms..."
echo ""

# Check for required tools
command -v cmake >/dev/null 2>&1 || { echo "❌ CMake not found. Please install CMake >= 3.10"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found."; exit 1; }

# Parse arguments
SKIP_FAISS=false
SKIP_DISKANN=false
SKIP_CANDY=false
INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-faiss)
            SKIP_FAISS=true
            shift
            ;;
        --skip-diskann)
            SKIP_DISKANN=true
            shift
            ;;
        --skip-candy)
            SKIP_CANDY=true
            shift
            ;;
        --install)
            INSTALL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-faiss      Skip FAISS build"
            echo "  --skip-diskann    Skip DiskANN build"
            echo "  --skip-candy      Skip CANDY build"
            echo "  --install         Install after build"
            echo "  --help            Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build algorithms
BUILD_COUNT=0

if [ "$SKIP_FAISS" = false ]; then
    echo "📦 Building FAISS..."
    cd implementations/faiss
    if [ -f "build.sh" ]; then
        ./build.sh
        ((BUILD_COUNT++))
    fi
    cd "$SCRIPT_DIR"
fi

if [ "$SKIP_DISKANN" = false ]; then
    echo "📦 Building DiskANN..."
    cd implementations/diskann-ms
    if [ -f "build.sh" ]; then
        ./build.sh
        ((BUILD_COUNT++))
    fi
    cd "$SCRIPT_DIR"
fi

if [ "$SKIP_CANDY" = false ]; then
    echo "📦 Building CANDY..."
    cd implementations/candy
    if [ -f "build.sh" ]; then
        ./build.sh
        ((BUILD_COUNT++))
    fi
    cd "$SCRIPT_DIR"
fi

echo ""
echo "✅ Built $BUILD_COUNT algorithm(s)"

# Install if requested
if [ "$INSTALL" = true ]; then
    echo ""
    echo "📦 Installing sage-anns..."
    pip install -e .
    echo "✅ Installation complete"
fi

echo ""
echo "🎉 Build complete!"
