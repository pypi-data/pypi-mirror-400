#!/usr/bin/env python3
"""
Extract code cells from a Jupyter notebook and save them as a Python file.

Usage: python dump-notebook.py input.ipynb output.py
"""

import sys
import nbformat
from pathlib import Path


def dump_notebook_to_python(notebook_path, output_path):
    """Extract code cells from notebook and write to Python file."""
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Extract code cells
    code_cells = []
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            # Add cell separator comment for clarity
            code_cells.append(f"# Cell {len(code_cells) + 1}")
            code_cells.append(cell.source)
            code_cells.append("")  # Empty line between cells
    
    # Write to Python file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(code_cells))
    
    print(f"Extracted {len([c for c in notebook.cells if c.cell_type == 'code'])} code cells from {notebook_path} to {output_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python dump-notebook.py input.ipynb output.py")
        sys.exit(1)
    
    notebook_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not notebook_path.exists():
        print(f"Error: Notebook file {notebook_path} does not exist")
        sys.exit(1)
    
    if not notebook_path.suffix == '.ipynb':
        print(f"Warning: {notebook_path} does not have .ipynb extension")
    
    try:
        dump_notebook_to_python(notebook_path, output_path)
    except Exception as e:
        print(f"Error processing notebook: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()