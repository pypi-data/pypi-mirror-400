from pathlib import Path

import hwo_disra.environment  # noqa: F401
from hwo_disra.EAC import create_syo_eac
from hwo_disra.Types import ScienceValue, Range

from hwo_disra.api.notebook_api import ApiResults, InatorInfo, DisraNBApi
from hwo_disra.api.notebook_eval import DisraNBEvaluator

def test_eval_cells():
  notebook_path = Path(__file__).parent / "resources" / "hwo_disra-api-test.ipynb"
  outputs = evaluate_notebook(notebook_path)
  # Check that we got yieldinator metadata
  assert all(isinstance(o, InatorInfo) for o in outputs.yieldinators)
  assert all(isinstance(o.name, str) and isinstance(o.type, str) for o in outputs.yieldinators)
  # Check the specific yieldinator from the test notebook
  assert outputs.yieldinators[0].name == 'test'
  assert outputs.yieldinators[0].type == 'TheYieldinator'

  assert len(outputs.evaluations) == 3

  eac3 = create_syo_eac('EAC3')
  outputs = DisraNBEvaluator.evaluate_notebook(notebook_path, verbose=True,
                                     notebook_parameters={'tests': 5},
                                     telescopes = [eac3])
  assert len(outputs.evaluations) == 1
  assert outputs.evaluations[0].eac == eac3.name

def test_eval_kbo():
  notebook_path = Path(__file__).parent.parent / "disra_notebooks" / "KBO_survey_hwo_disra.ipynb"
  outputs:ApiResults = evaluate_notebook(notebook_path)
  assert len(outputs.evaluations) == 4
  assert all(len(o.sample_points) > 0 for o in outputs.evaluations)

def test_eval_readme():
  notebook_path = Path(__file__).parent / "resources" / "hwo_disra_readme.ipynb"
  outputs:ApiResults = evaluate_notebook(notebook_path)
  assert len(outputs.evaluations) > 0
  assert all(len(o.sample_points) > 0 for o in outputs.evaluations)

def evaluate_notebook(notebook_path):
  return DisraNBEvaluator.evaluate_notebook(notebook_path, verbose=True,
                                            notebook_parameters={'tests': 5})

def test_yield_results_pickle():
  import pickle
  DisraNBApi.reset_instance()  # Reset singleton for test
  api = DisraNBApi.get_instance()
  def compute_yield(x, y):
    return x + y

  def compute_time(eac, yield_value, x, y):
    return  yield_value + x

  yieldinator = api.yieldinator("test",
                                thresholds = {ScienceValue.ENABLING: 25},
                                variables = {'x': Range(0,  10), 'y': Range(5,  15)},
                                yield_function=compute_yield)
  timeinator = api.timeinator(yieldinator, timeinate=compute_time)
  results = api.evaluate(timeinator)

  result = ApiResults(results, [api.prepare_for_pickle(timeinator)])
  pickled = pickle.dumps(result)
  assert pickle.loads(pickled) == result

def test_telescope_pickle():
  import pickle
  telescope = create_syo_eac("EAC1")
  tele2 = pickle.loads(pickle.dumps(telescope))
  assert telescope.name == tele2.name