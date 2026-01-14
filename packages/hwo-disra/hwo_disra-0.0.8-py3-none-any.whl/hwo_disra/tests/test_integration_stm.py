"""Integration tests for STM functionality with notebook evaluation."""

import pytest
import json
import tempfile
from pathlib import Path
import hwo_disra.environment  # noqa: F401

from hwo_disra.api.notebook_eval import DisraNBEvaluator
from hwo_disra.api.notebook_api import DisraNBApi
from hwo_disra.Types import STMData


class TestSTMIntegration:
    """Test cases for STM integration with notebook evaluation."""

    def test_stm_extractor_in_evaluator(self):
        DisraNBApi.reset_instance()  # Reset singleton for test
        """Test that STMExtractor works properly in the notebook evaluator context."""
        # Create a simple notebook with STM data
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Test Science Case\n",
                    "\n",
                    "**GOAL:** Test goal from evaluator\n",
                    "\n",
                    "**OBJECTIVE:** Test objective from evaluator"
                ]
            }
        ]

        notebook = {
            "cells": cells,
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False)
        json.dump(notebook, temp_file)
        temp_file.close()

        try:
            # Test extraction using the evaluator's STM extractor
            evaluator = DisraNBEvaluator()
            stm_data = evaluator._stm_extractor.extract_to_stm_data(Path(temp_file.name))

            assert stm_data.goal == "Test goal from evaluator"
            assert stm_data.objective == "Test objective from evaluator"

        finally:
            Path(temp_file.name).unlink()

    def create_test_notebook_with_stm(self):
        """Create a test notebook with STM data."""
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Test Science Case\n",
                    "\n",
                    "**GOAL:** How did the seeds of Solar System planets first come together?\n",
                    "\n",
                    "**OBJECTIVE:** Discover Kuiper Belt Objects (KBOs) down to sizes that distinguish between different planetesimal formation scenarios.\n",
                    "\n",
                    "**PHYSICAL_PARAMETERS:** KBO size distribution characterized by luminosity function parameters including broken power law slopes and exponential taper parameters.\n",
                    "\n",
                    "**OBSERVATIONS:** R band imaging survey with depth (R_lim) and sky coverage (Ω) sufficient to detect enough KBOs to distinguish between luminosity function models at 99.7% confidence.\n",
                    "\n",
                    "Analysis shows required parameters:\n",
                    "- Survey depth: 31.6 mag\n",
                    "- Sky coverage: 0.0033 sq. deg\n",
                    "- Total survey time: 2.0 days"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Setup API\n",
                    "from hwo_disra.api.notebook_api import DisraNBApi\n",
                    "\n",
                    "api = DisraNBApi.get_instance(show_plots=False)\n",
                    "\n",
                    "print(\"API setup complete\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Some analysis code that would normally create results\n",
                    "final_survey = {\n",
                    "    'Band': 'R',\n",
                    "    'depth': 31.6,\n",
                    "    'min_size': 3.8,\n",
                    "    'size_unit': 'km',\n",
                    "    'omega': 0.0033,\n",
                    "    'omega_unit': 'sq. deg',\n",
                    "    'time': 2.0,\n",
                    "    'time_unit': 'days'\n",
                    "}\n",
                    "\n",
                    "print(f\"Analysis complete. Final survey parameters: {final_survey}\")"
                ]
            }
        ]

        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False)
        json.dump(notebook, temp_file)
        temp_file.close()
        return temp_file.name

    @pytest.mark.slow
    def test_notebook_evaluation_with_stm_extraction(self):
        DisraNBApi.reset_instance()  # Reset singleton for test
        """Test full notebook evaluation with STM extraction."""
        notebook_path = self.create_test_notebook_with_stm()

        try:
            evaluator = DisraNBEvaluator(verbose=True)
            results = evaluator.evaluate_notebook(Path(notebook_path))

            # Check that STM data was extracted
            assert results.stm_data is not None
            assert isinstance(results.stm_data, STMData)

            # Check STM content
            assert results.stm_data.goal == "How did the seeds of Solar System planets first come together?"
            assert "Kuiper Belt Objects" in results.stm_data.objective
            assert "luminosity function parameters" in results.stm_data.physical_parameters
            assert "R band imaging survey" in results.stm_data.observations
            assert "99.7% confidence" in results.stm_data.observations

        finally:
            Path(notebook_path).unlink()

    def test_stm_data_in_api_results(self):
        DisraNBApi.reset_instance()  # Reset singleton for test
        """Test that STM data is properly included in evaluation results."""
        # Create a simple notebook
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "**GOAL:** Simple test goal\n",
                    "\n",
                    "**OBJECTIVE:** Simple test objective"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from hwo_disra.api.notebook_api import DisraNBApi\n",
                    "api = DisraNBApi.get_instance(show_plots=False)"
                ]
            }
        ]

        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False)
        json.dump(notebook, temp_file)
        temp_file.close()

        try:
            evaluator = DisraNBEvaluator()
            results = evaluator.evaluate_notebook(Path(temp_file.name))

            # Verify STM data is present and correct
            assert results.stm_data is not None
            assert results.stm_data.goal == "Simple test goal"
            assert results.stm_data.objective == "Simple test objective"

        finally:
            Path(temp_file.name).unlink()