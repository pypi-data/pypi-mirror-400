import enum
from multiprocessing import current_process, Queue, set_start_method
from multiprocessing.managers import BaseManager
from pathlib import Path
from typing import Mapping, Callable

# Set multiprocessing start method to spawn to avoid fork() issues in Python 3.13
try:
    set_start_method('spawn', force=True)
except RuntimeError:
    # Start method was already set
    pass

from jupyter_client.blocking.client import BlockingKernelClient
import nbformat
from jupyter_client.manager import KernelManager
from hwo_disra.api.notebook_api import ApiResults
from hwo_disra.api.stm_extractor import STMExtractor
from hwo_disra.Types import STMData

class KernelEvaluationStatus(enum.Enum):
    Success = 1
    Error = 2

class DisraNBEvaluator:
    """
    This class supports evaluating a notebook using DisraNBApi and extracting
    the outputs registered with the API instance used in the notebook.
    The basic use of this class is ~:py:meth:`notebook_eval.DisraNBEvaluator.evaluate_notebook`
    ```python
    from hwo_disra.api.notebook_eval import DisraNBEvaluator
    eac3 = create_syo_eac('EAC3')
    results = DisraNBEvaluator.evaluate_notebook(notebook_path, telescopes = [eac3])
    ```
    """
    def __init__(self, verbose=False):
        self._outputs = {}
        self.verbose = verbose
        self._stm_extractor = STMExtractor()

    def evaluate(self, nb_path: Path,
                 notebook_parameters = None,
                 telescopes = None) -> None:
        """
        This method is the entry point for the evaluator.
        - nb_path : The file system path to the notebook
        - notebook_parameters: optional parameters that can be looked up
          within the notebook using the DisraNBApi.get_parameter method during
          evaluation.
        - telescopes : Optional telescope instances. If this is provided it
          will override the default list of telescopes used by DisraNBApi.
        """
        # Start a kernel
        km: KernelManager = KernelManager()
        km.start_kernel()
        kc: BlockingKernelClient = km.client()
        kc.start_channels()
        kc.wait_for_ready()

        try:
            result = self._set_notebook_parameters(kc, notebook_parameters)
            if result == KernelEvaluationStatus.Error:
                return
            result = self._set_telescopes(kc, telescopes)
            if result == KernelEvaluationStatus.Error:
                return
            self._execute_notebook(kc, nb_path)
        finally:
            kc.stop_channels()
            km.shutdown_kernel()

    def _set_telescopes(self, kc, telescopes):
        """
        This is the internal method used to send the telescopes list to
        the notebook if it is provided as a parameter to evaluate.
        """
        if telescopes is not None:
            return self._send_data(kc, telescopes, lambda address, key: f"""
                from hwo_disra.api.notebook_api import DisraNBApi
                k = {key}
                addr = "{address}"
                DisraNBApi.set_eacs(DisraNBApi.receive_data(addr, k))
                """)
        return KernelEvaluationStatus.Success

    def _set_notebook_parameters(self, kc, notebook_parameters) -> KernelEvaluationStatus:
        """
        This is the internal method used to send the notebook parameters to
        the notebook if it is provided as a parameter to evaluate.
        """
        if notebook_parameters is not None:
            msg_id = kc.execute(f"""
                from hwo_disra.api.notebook_api import DisraNBApi
                DisraNBApi.set_parameters({notebook_parameters})
                """)
            return self._handle_execution_status(kc, msg_id)
        return KernelEvaluationStatus.Success

    def _execute_notebook(self, kc: BlockingKernelClient, nb_path: Path) -> None:
        """
        Internal method to execute the notebook and capture outputs
        registered using the DisraNBApi methods within the notebook.
        """
        with open(nb_path) as f:
            nb = nbformat.read(f, as_version=4)
            if self.verbose:
                print(f"Starting notebook execution for {nb_path}")
            self._eval_cells(kc, nb)
            if self.verbose:
                print("Cell execution completed. Extracting STM data...")
            extracted_stm_data = self._extract_stm_data(nb_path)
            if self.verbose:
                print("STM extraction completed. Attempting to capture outputs...")
            self._capture_outputs(kc, nb_path, extracted_stm_data)

    def _eval_cells(self, kc: BlockingKernelClient, nb) -> None:
        """
        Internal method to evaluate all cells in the notebook.
        """
        # Execute each code cell
        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type == "code":
                if self.verbose:
                    print(f"Executing cell {cell_idx + 1}:")
                    print(f"Source: {cell.source[:100]}{'...' if len(cell.source) > 100 else ''}")
                msg_id= kc.execute(cell.source)
                self._handle_execution_status(kc, msg_id, cell_idx)

    def _handle_execution_status(self, kc, msg_id, cell_idx = -999) -> KernelEvaluationStatus:
        """
        This method handles waiting for the execution of code in the notebook
        to complete. It also collects and displays output from the kernel
        execution.
        After each execution command sent to the kernel context we need to
        wait for a success or error event from the kernel context reporting
        the result of the execution.
        """
        timeout_seconds = 260
        # Collect outputs
        import time
        from queue import Empty
        start_time = time.time()
        while True:
            try:
                # Use the channel directly to avoid event loop issues in Python 3.13
                msg = kc.iopub_channel.get_msg(timeout=1)
            except Empty:
                # Check if we've exceeded the overall timeout
                if time.time() - start_time > timeout_seconds:
                    raise RuntimeError(f"Timeout waiting for message from cell {cell_idx + 1}")
                continue
            if msg['parent_header'].get('msg_id') == msg_id:
                msg_type = msg['msg_type']
                if self.verbose:
                    print(f"Message type: {msg_type}")
                if msg_type == 'execute_result':
                    print("Output:", msg['content']['data'].get('text/plain', ''))
                elif msg_type == 'stream':
                    print(f"Stream: {msg['content']['text']}")
                elif msg_type == 'error':
                    print(f"Error in cell {cell_idx + 1}:", msg['content']['evalue'])
                    if self.verbose:
                        print("Traceback:", '\n'.join(msg['content']['traceback']))
                    return KernelEvaluationStatus.Error # Stop execution on error
                elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                    return KernelEvaluationStatus.Success

    def get_outputs(self) -> Mapping[Path, ApiResults]:
        """
        Returns the mapping from notebook paths that have bene evaluated to
        the results of that evaluation.
        """
        if self.verbose:
            print(f"get_outputs called. _outputs is: {self._outputs}")
            if self._outputs:
                print(f"Available paths: {list(self._outputs.keys())}")
        return self._outputs

    def get_notebook_outputs(self, nb_path: Path) -> ApiResults:
        """
        Returns the ApiResults for the evaluation of the notebook path.
        """
        if self.verbose:
            print(f"get_notebook_outputs called for {nb_path}")
            if self._outputs:
                print(f"Available paths: {list(self._outputs.keys())}")
        return self._outputs.get(nb_path) if self._outputs else None

    def _capture_outputs(self, kc: BlockingKernelClient, nb_path: Path, stm_data: STMData) -> None:
        """
        Internal method to capture all outputs registered via DisraNBApi
        within the notebook and combine with extracted STM data.
        """
        outputs = self._receive_data(kc, lambda address, key: f"""
            from hwo_disra.api.notebook_api import DisraNBApi
            DisraNBApi.write_outputs("{address}", {key})
            """)

        # Update the outputs with the extracted STM data
        outputs.stm_data = stm_data
        self._outputs[nb_path] = outputs

    def _extract_stm_data(self, nb_path: Path) -> STMData:
        """
        Internal method to extract STM data directly from the notebook file.
        """
        if self.verbose:
            print("Extracting STM data from notebook file...")

        # Extract STM data directly from the notebook file
        stm_data = self._stm_extractor.extract_to_stm_data(nb_path)

        if self.verbose:
            required_fields = ['goal', 'objective', 'physical_parameters', 'observations']
            found_count = len([f for f in required_fields if getattr(stm_data, f)])
            print(f"STM extraction completed. Found {found_count} out of {len(required_fields)} required fields.")

        return stm_data


    class QueueManager(BaseManager):
        """
        Wrapper around BaseManager so we have a place to put this queue and
        a distinct class to register the get_queue method on.
        """
        queue = Queue()

    # This cannot be marked @staticmethod because static methods cannot
    # be pickled. When the queue manager is started this method will
    # be pickled because it is registered as the `get_queue` method
    # on the manager.
    def get_queue():
        return DisraNBEvaluator.QueueManager.queue

    QueueManager.register('get_queue', callable=get_queue)

    def _send_data(self, kc: BlockingKernelClient, data, receiving_code: Callable[[str, bytes], str]) -> KernelEvaluationStatus:
        """
        Use to send data to the notebook.
        - `data` is the object to send, via multiprocessing queue, to the notebook. It
          must be pickle compatible for this.
        - `receiving_code` is a function generating the code block to execute in the notebook to receive the
          data. The input parameters are the address and authentication key needed to
          connect to the queue.
        """
        manager = DisraNBEvaluator.QueueManager()
        manager.start()
        queue = manager.get_queue()
        queue.put(data, block=False)
        code = receiving_code(manager.address, current_process().authkey)
        if self.verbose:
          print(f"Sending code: {code}")
        msg_id = kc.execute(code)
        if self.verbose:
          print(f"Executed write_outputs command with msg_id: {msg_id}")
        return self._handle_execution_status(kc, msg_id)

    def _receive_data(self, kc: BlockingKernelClient, notebook_code: Callable[[str, bytes], str]) -> ApiResults:
        """
        Receive data from the notebook by executing the given notebook code
        and waiting for a result on the queue.
        - notebook_code is a function generating the code block to execute in
          the notebook to put the data into the queue. It should take the
          address, which will need to be quoted with `"`, and the key,
          which will not, and return the code to evaluate to put data into that
          queue.
        """
        manager = DisraNBEvaluator.QueueManager()
        manager.start()
        queue = manager.get_queue()

        # Execute the write_outputs command and get the message ID
        msg_id = kc.execute(notebook_code(manager.address, current_process().authkey))

        if self.verbose:
          print(f"Executed write_outputs command with msg_id: {msg_id}")

        outputs = queue.get(timeout=60)
        if isinstance(outputs, Exception):
          print(outputs)
          raise outputs

        return outputs

    @staticmethod
    def evaluate_notebook(notebook_path: Path, verbose = False, notebook_parameters = None, telescopes = None) -> ApiResults:
        evaluator = DisraNBEvaluator(verbose=verbose)
        evaluator.evaluate(notebook_path, notebook_parameters = notebook_parameters,
                           telescopes = telescopes)
        outputs: ApiResults = evaluator.get_notebook_outputs(notebook_path)
        assert isinstance(outputs, ApiResults)
        return outputs