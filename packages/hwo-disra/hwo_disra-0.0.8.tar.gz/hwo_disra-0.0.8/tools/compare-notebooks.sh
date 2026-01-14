#!/bin/bash
# Compare two Jupyter notebooks by extracting their code cells and using bcomp or diff

set -e

# Parse options
DIFF_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --diff)
            DIFF_MODE=true
            shift
            ;;
        -*)
            echo "Unknown option $1"
            echo "Usage: $0 [--diff] notebook1.ipynb notebook2.ipynb"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 [--diff] notebook1.ipynb notebook2.ipynb"
    echo "  --diff    Output differences to a temporary file instead of launching bcomp"
    exit 1
fi

NOTEBOOK1="$1"
NOTEBOOK2="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate input files
if [ ! -f "$NOTEBOOK1" ]; then
    echo "Error: $NOTEBOOK1 does not exist"
    exit 1
fi

if [ ! -f "$NOTEBOOK2" ]; then
    echo "Error: $NOTEBOOK2 does not exist"
    exit 1
fi

# Extract notebook base names for temp file naming
NB1_NAME=$(basename "$NOTEBOOK1" .ipynb)
NB2_NAME=$(basename "$NOTEBOOK2" .ipynb)

# Create temporary files
TEMP1=$(mktemp -t "${NB1_NAME}_XXXXXX.py")
TEMP2=$(mktemp -t "${NB2_NAME}_XXXXXX.py")

# Create diff output file if in diff mode
if [ "$DIFF_MODE" = true ]; then
    DIFF_OUTPUT=$(mktemp -t "${NB1_NAME}_vs_${NB2_NAME}_XXXXXX.txt")
fi

# Cleanup function
cleanup() {
    rm -f "$TEMP1" "$TEMP2"
    if [ "$DIFF_MODE" = true ] && [ -f "$DIFF_OUTPUT" ]; then
        # Don't remove diff output file, user needs to access it
        :
    fi
}
trap cleanup EXIT

# Extract code cells from both notebooks
echo "Extracting code cells from $NOTEBOOK1..."
python "$SCRIPT_DIR/dump-notebook.py" "$NOTEBOOK1" "$TEMP1"

echo "Extracting code cells from $NOTEBOOK2..."
python "$SCRIPT_DIR/dump-notebook.py" "$NOTEBOOK2" "$TEMP2"

# Compare the files
if [ "$DIFF_MODE" = true ]; then
    echo "Generating diff output..."
    diff -u "$TEMP1" "$TEMP2" > "$DIFF_OUTPUT" || true
    echo "Diff output saved to: $DIFF_OUTPUT"
    
    # Show a summary
    if [ -s "$DIFF_OUTPUT" ]; then
        echo "Differences found between notebooks."
        echo "Lines added/removed/changed:"
        grep -E '^[\+\-]' "$DIFF_OUTPUT" | wc -l
    else
        echo "No differences found between notebooks."
    fi
else
    # Launch bcomp with the temporary files
    echo "Launching bcomp to compare notebooks..."
    bcomp "$TEMP1" "$TEMP2"
fi