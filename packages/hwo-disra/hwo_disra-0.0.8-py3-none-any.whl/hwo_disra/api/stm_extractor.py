"""STM (Science Traceability Matrix) data extraction from Jupyter notebooks.

This module implements extraction of STM data using markdown bold formatting
(`**KEY:**`) to identify and extract content sections from notebook cells.
"""

import re
import logging
from typing import Dict, List
from pathlib import Path

import nbformat
from ..Types import STMData

logger = logging.getLogger(__name__)


class STMExtractor:
    """Extracts STM data from Jupyter notebook cells using bolded key markers."""

    # Standard STM keys mapping from markdown format to dataclass fields
    STM_KEYS = {
        'GOAL': 'goal',
        'CODE PURPOSE': 'code_purpose',
        'OBJECTIVE': 'objective',
        'PHYSICAL_PARAMETERS': 'physical_parameters',
        'OBSERVATIONS': 'observations',
        'INSTRUMENT_REQUIREMENTS': 'instrument_requirements',
        'MISSION_REQUIREMENTS': 'mission_requirements',
        'EXPECTED_PERFORMANCE': 'expected_performance'
    }

    # Class-level compiled regex pattern for better performance
    # Matches **KEY:** followed by content until next key or end
    # Updated to support spaces in keys like "CODE PURPOSE"
    _PATTERN = re.compile(
        r'\*\*([A-Z_ ]+):\*\*\s*(.*?)(?=\*\*[A-Z_ ]+:\*\*|\Z)',
        re.DOTALL | re.MULTILINE
    )

    _ALL_KEYS_PATTERN = re.compile(r'\*\*([A-Z_ ]+):\*\*')

    def __init__(self):
        """Initialize STMExtractor."""
        pass

    def _clean_content(self, content: str) -> str:
        """Clean and normalize extracted content.

        Args:
            content: Raw extracted content

        Returns:
            Cleaned and normalized content
        """
        # Strip whitespace and normalize line endings
        cleaned = content.strip().replace('\r\n', '\n').replace('\r', '\n')

        # Handle empty line termination
        return self._handle_empty_line_termination(cleaned)

    def _handle_empty_line_termination(self, content: str) -> str:
        """Handle content termination at empty lines.

        Take only the first paragraph (content up to the first empty line).

        Args:
            content: Content to process

        Returns:
            Content truncated at the first empty line boundary
        """
        parts = content.split('\n\n')
        return parts[0]

    def extract_from_cell(self, cell_source: str) -> Dict[str, str]:
        """Extract STM data from a single notebook cell.

        Unrecognized bolded keys are skipped to prevent their content from
        being included in recognized STM fields.

        Args:
            cell_source: The source content of a notebook cell

        Returns:
            Dictionary mapping STM field names to extracted content
        """
        if not isinstance(cell_source, str):
            logger.warning(f"Invalid cell source type: {type(cell_source)}")
            return {}

        try:
            # Find all bolded keys in order
            all_key_matches = list(self._ALL_KEYS_PATTERN.finditer(cell_source))
        except Exception as e:
            logger.error(f"Failed to find keys in cell content: {e}")
            return {}

        extracted = {}

        # Process each key in order, skipping unrecognized keys
        for i, match in enumerate(all_key_matches):
            key = match.group(1)

            if key not in self.STM_KEYS:
                logger.debug(f"Skipping unrecognized key: {key}")
                continue

            # Find content between this key and the next key (or end)
            start = match.end()
            if i + 1 < len(all_key_matches):
                end = all_key_matches[i + 1].start()
                content = cell_source[start:end]
            else:
                content = cell_source[start:]

            # Extract and clean the content
            field_name = self.STM_KEYS[key]
            cleaned_content = self._clean_content(content)
            extracted[field_name] = cleaned_content
            logger.debug(f"Extracted {field_name}: {len(cleaned_content)} chars")

        return extracted

    def _load_notebook(self, notebook_path: Path):
        """Load and parse notebook using nbformat.

        Args:
            notebook_path: Path to notebook file

        Returns:
            Parsed notebook object

        Raises:
            nbformat.ValidationError: If notebook format is invalid
            UnicodeDecodeError: If notebook has encoding issues
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                return nbformat.read(f, as_version=nbformat.NO_CONVERT)
        except nbformat.ValidationError as e:
            logger.error(f"Invalid notebook format in {notebook_path}: {e}")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in notebook {notebook_path}: {e}")
            raise

    def extract_from_notebook(self, notebook_path: Path) -> Dict[str, str]:
        """Extract STM data from all cells in a Jupyter notebook.

        Args:
            notebook_path: Path to the .ipynb file

        Returns:
            Dictionary mapping STM field names to extracted content

        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If notebook file is too large
            nbformat.ValidationError: If notebook format is invalid
        """
        if not notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")

        # Load notebook with error handling
        notebook = self._load_notebook(notebook_path)

        all_extracted = {}
        cells_processed = 0

        # Process all cells, looking for markdown cells with STM keys
        for cell_idx, cell in enumerate(notebook.cells):
            if cell.cell_type == 'markdown':
                if cell.source:  # Only process non-empty cells
                    cell_extracted = self.extract_from_cell(cell.source)

                    if cell_extracted:
                        # Log which fields are being overridden
                        overridden = set(all_extracted.keys()) & set(cell_extracted.keys())
                        if overridden:
                            logger.info(
                                f"Cell {cell_idx} overriding fields: {overridden}"
                            )

                        all_extracted.update(cell_extracted)
                        cells_processed += 1

        logger.info(
            f"Processed {cells_processed} markdown cells, "
            f"extracted {len(all_extracted)} STM fields"
        )

        return all_extracted

    def extract_to_stm_data(self, notebook_path: Path) -> STMData:
        """Extract STM data from notebook and return as STMData object.

        Args:
            notebook_path: Path to the .ipynb file

        Returns:
            STMData object populated with extracted content

        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If notebook file is too large
            nbformat.ValidationError: If notebook format is invalid
        """
        extracted = self.extract_from_notebook(notebook_path)
        stm_data = STMData(**extracted)

        if not stm_data.is_complete():
            missing = stm_data.get_missing_fields()
            logger.warning(f"STM data incomplete. Missing fields: {missing}")

        return stm_data

    def validate_keys(self, cell_source: str) -> List[str]:
        """Validate that all bolded keys in a cell are recognized STM keys.

        Args:
            cell_source: The source content of a notebook cell

        Returns:
            List of unrecognized keys found in the cell
        """
        if not isinstance(cell_source, str):
            return []

        try:
            all_matches = self._ALL_KEYS_PATTERN.findall(cell_source)
        except Exception as e:
            logger.error(f"Failed to validate keys: {e}")
            return []

        unrecognized = [
            key for key in all_matches
            if key not in self.STM_KEYS
        ]

        if unrecognized:
            logger.debug(f"Found unrecognized keys: {unrecognized}")

        return unrecognized

    def get_supported_keys(self) -> List[str]:
        """Get list of supported STM keys.

        Returns:
            List of supported markdown key names (e.g., ['GOAL', 'OBJECTIVE', ...])
        """
        return list(self.STM_KEYS.keys())