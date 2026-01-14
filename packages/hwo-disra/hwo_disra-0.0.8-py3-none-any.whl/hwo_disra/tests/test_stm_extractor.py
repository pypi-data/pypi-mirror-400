"""Tests for STM data extraction functionality."""

import pytest
import json
import tempfile
from pathlib import Path

from hwo_disra.api.stm_extractor import STMExtractor
from hwo_disra.Types import STMData


class TestSTMExtractor:
    """Test cases for STMExtractor class."""

    def setup_method(self):
        """Set up test instance."""
        self.extractor = STMExtractor()

    def test_single_key_extraction(self):
        """Test extraction of a single STM key from cell content."""
        cell_source = """
**GOAL:** How did the seeds of Solar System planets first come together?

This is additional content that should be included.
"""
        result = self.extractor.extract_from_cell(cell_source)
        expected_goal = "How did the seeds of Solar System planets first come together?"

        assert result == {'goal': expected_goal}

    def test_multiple_keys_extraction(self):
        """Test extraction of multiple STM keys from single cell."""
        cell_source = """
**GOAL:** Study planetary formation

**OBJECTIVE:** Discover KBOs down to small sizes

**PHYSICAL_PARAMETERS:** KBO size distribution parameters
"""
        result = self.extractor.extract_from_cell(cell_source)

        assert len(result) == 3
        assert result['goal'] == 'Study planetary formation'
        assert result['objective'] == 'Discover KBOs down to small sizes'
        assert result['physical_parameters'] == 'KBO size distribution parameters'

    def test_key_with_empty_line_termination(self):
        """Test that content stops at empty line."""
        cell_source = """
**GOAL:** Study planetary formation

This should be included.

This should NOT be included because there's an empty line above.
"""
        result = self.extractor.extract_from_cell(cell_source)
        assert result['goal'] == 'Study planetary formation'

    def test_key_with_next_key_termination(self):
        """Test that content stops at next STM key."""
        cell_source = """
**GOAL:** Study planetary formation
This is goal content.
**OBJECTIVE:** Discover KBOs
This is objective content.
"""
        result = self.extractor.extract_from_cell(cell_source)

        assert result['goal'] == 'Study planetary formation\nThis is goal content.'
        assert result['objective'] == 'Discover KBOs\nThis is objective content.'

    def test_unrecognized_key_ignored(self):
        """Test that unrecognized keys are ignored."""
        cell_source = """
**UNKNOWN_KEY:** This should be ignored

**GOAL:** This should be extracted
"""
        result = self.extractor.extract_from_cell(cell_source)

        assert len(result) == 1
        assert result['goal'] == 'This should be extracted'
        assert 'unknown_key' not in result

    def test_no_keys_returns_empty(self):
        """Test that cells with no STM keys return empty dict."""
        cell_source = """
This is just regular markdown content with no STM keys.
Some **bold** text but not STM keys.
"""
        result = self.extractor.extract_from_cell(cell_source)
        assert result == {}

    def test_empty_cell_returns_empty(self):
        """Test that empty cells return empty dict."""
        result = self.extractor.extract_from_cell("")
        assert result == {}

    def test_malformed_key_ignored(self):
        """Test that malformed keys are ignored."""
        cell_source = """
*GOAL:* Single asterisk should be ignored
**GOAL** Missing colon should be ignored
** GOAL:** Space before key should be ignored
**goal:** Lowercase should be ignored
**GOAL:** This should work
"""
        result = self.extractor.extract_from_cell(cell_source)

        assert len(result) == 1
        assert result['goal'] == 'This should work'

    def test_validate_keys_recognized(self):
        """Test validation of recognized keys."""
        cell_source = """
**GOAL:** Valid key
**OBJECTIVE:** Another valid key
"""
        unrecognized = self.extractor.validate_keys(cell_source)
        assert unrecognized == []

    def test_validate_keys_unrecognized(self):
        """Test validation catches unrecognized keys."""
        cell_source = """
**GOAL:** Valid key
**INVALID_KEY:** This is not recognized
**ANOTHER_BAD_KEY:** Neither is this
"""
        unrecognized = self.extractor.validate_keys(cell_source)
        assert set(unrecognized) == {'INVALID_KEY', 'ANOTHER_BAD_KEY'}

    def create_test_notebook(self, cells_data):
        """Helper to create a temporary notebook file for testing."""
        notebook = {
            "cells": cells_data,
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False)
        json.dump(notebook, temp_file)
        temp_file.close()
        return temp_file.name

    def test_extract_from_notebook_single_cell(self):
        """Test extraction from notebook with single markdown cell."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**GOAL:** Test goal\n\n**OBJECTIVE:** Test objective"
            }
        ]

        notebook_path = self.create_test_notebook(cells)
        try:
            result = self.extractor.extract_from_notebook(Path(notebook_path))
            assert result['goal'] == 'Test goal'
            assert result['objective'] == 'Test objective'
        finally:
            Path(notebook_path).unlink()

    def test_extract_from_notebook_multiple_cells(self):
        """Test extraction from notebook with multiple cells."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**GOAL:** Test goal"
            },
            {
                "cell_type": "code",
                "metadata": {},
                "outputs": [],
                "execution_count": None,
                "source": "# This code cell should be ignored"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**OBJECTIVE:** Test objective"
            }
        ]

        notebook_path = self.create_test_notebook(cells)
        try:
            result = self.extractor.extract_from_notebook(Path(notebook_path))
            assert result['goal'] == 'Test goal'
            assert result['objective'] == 'Test objective'
        finally:
            Path(notebook_path).unlink()

    def test_extract_from_notebook_source_as_list(self):
        """Test extraction when notebook source is stored as list."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["**GOAL:** Test goal\n", "\n", "Additional content"]
            }
        ]

        notebook_path = self.create_test_notebook(cells)
        try:
            result = self.extractor.extract_from_notebook(Path(notebook_path))
            assert result['goal'] == 'Test goal'
        finally:
            Path(notebook_path).unlink()

    def test_extract_from_notebook_override_behavior(self):
        """Test that later cells override earlier ones for same key."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**GOAL:** First goal"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**GOAL:** Second goal (should override)"
            }
        ]

        notebook_path = self.create_test_notebook(cells)
        try:
            result = self.extractor.extract_from_notebook(Path(notebook_path))
            assert result['goal'] == 'Second goal (should override)'
        finally:
            Path(notebook_path).unlink()

    def test_extract_to_stm_data(self):
        """Test extraction directly to STMData object."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "**GOAL:** Test goal\n\n**OBJECTIVE:** Test objective"
            }
        ]

        notebook_path = self.create_test_notebook(cells)
        try:
            stm_data = self.extractor.extract_to_stm_data(Path(notebook_path))
            assert isinstance(stm_data, STMData)
            assert stm_data.goal == 'Test goal'
            assert stm_data.objective == 'Test objective'
            assert stm_data.physical_parameters is None
        finally:
            Path(notebook_path).unlink()

    def test_extract_from_nonexistent_file(self):
        """Test that missing file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_from_notebook(Path("/nonexistent/path.ipynb"))


class TestSTMData:
    """Test cases for STMData class."""

    def test_is_complete_all_required_fields(self):
        """Test is_complete returns True when all required fields are set."""
        stm_data = STMData(
            goal="Test goal",
            objective="Test objective",
            physical_parameters="Test params",
            observations="Test observations"
        )
        assert stm_data.is_complete()

    def test_is_complete_missing_required_field(self):
        """Test is_complete returns False when required field is missing."""
        stm_data = STMData(
            goal="Test goal",
            objective="Test objective",
            # missing physical_parameters
            observations="Test observations"
        )
        assert not stm_data.is_complete()

    def test_is_complete_empty_string_field(self):
        """Test is_complete returns False when required field is empty string."""
        stm_data = STMData(
            goal="Test goal",
            objective="",  # empty string
            physical_parameters="Test params",
            observations="Test observations"
        )
        assert not stm_data.is_complete()

    def test_get_missing_fields(self):
        """Test get_missing_fields returns correct missing field names."""
        stm_data = STMData(
            goal="Test goal",
            # missing objective
            physical_parameters="Test params"
            # missing observations
        )
        missing = stm_data.get_missing_fields()
        assert set(missing) == {'objective', 'observations'}

    def test_to_dict(self):
        """Test conversion to dictionary format."""
        stm_data = STMData(
            goal="Test goal",
            objective="Test objective"
        )
        result = stm_data.to_dict()

        expected = {
            'goal': 'Test goal',
            'objective': 'Test objective',
            'code_purpose': None,
            'physical_parameters': None,
            'observations': None,
            'instrument_requirements': None,
            'mission_requirements': None,
            'expected_performance': None
        }
        assert result == expected