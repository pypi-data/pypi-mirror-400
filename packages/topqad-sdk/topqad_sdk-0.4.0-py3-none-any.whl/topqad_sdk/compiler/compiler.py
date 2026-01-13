import logging
from enum import Enum
from typing import Union
from topqad_sdk.models import (
    CompilerPipelineSolutionResponse,
    Circuit,
    FINISHED_STATUSES,
    StatusEnum,
)
from topqad_sdk.clients.compiler_client import CompilerClient
from topqad_sdk._exceptions import TopQADError, TopQADTimeoutError

# TODO: Uncomment and use if needed in future
# class FiletypeEnum(str, Enum):
#     decomposed_qasm = "decomposed_qasm"
#     rotations_circuit = "rotations_circuit"
#     scheduled_file = "scheduled_file"


class CompilationResult:
    """Result of the Compilation service run."""

    def __init__(self, response: CompilerPipelineSolutionResponse):
        steps = getattr(response, "steps")
        decomposer = steps.decomposer
        optimizer = steps.optimizer
        scheduler = steps.scheduler

        self._decomposed_circuit_path = decomposer.sk_circuit_path
        self._sk_accumulated_error = decomposer.accumulated_error
        self._num_clifford_operations = optimizer.num_clifford_operations
        self._num_non_clifford_operations = optimizer.num_non_clifford_operations
        self._total_num_operations = optimizer.total_num_operations
        self._rotations_circuit_path = optimizer.optimized_circuit_path
        self._num_logical_measurements = optimizer.num_logical_measurements
        self._scheduled_output_filepath = scheduler.schedule_filepath

    def __repr__(self):
        return (
            f"<CompilationResult>\n"
            f"  Decomposed circuit path: {self.decomposed_circuit_path}\n"
            f"  Accumulated error: {self.sk_accumulated_error}\n"
            f"  Non-Clifford operations: {self.num_non_clifford_operations}\n"
            f"  Total operations: {self.total_num_operations}\n"
            f"  Rotations circuit path: {self.rotations_circuit_path}\n"
            f"  Logical measurements: {self.num_logical_measurements}\n"
            f"  Scheduled output filepath: {self.scheduled_output_filepath}\n"
        )

    @property
    def decomposed_circuit_path(self):
        """Path to the decomposed circuit."""
        return self._decomposed_circuit_path

    @property
    def sk_accumulated_error(self):
        """Error induced by decomposition of gates."""
        return self._sk_accumulated_error

    @property
    def num_non_clifford_operations(self):
        """Number of non clifford gates."""
        return self._num_non_clifford_operations

    @property
    def total_num_operations(self):
        """Total number of gates."""
        return self._total_num_operations

    @property
    def rotations_circuit_path(self):
        """Path to the circuit decomposed into Pauli rotations."""
        return self._rotations_circuit_path

    @property
    def num_logical_measurements(self):
        """Number of logical measurements."""
        return self._num_logical_measurements

    @property
    def scheduled_output_filepath(self):
        """Path to the assembled schedule file."""
        return self._scheduled_output_filepath


class Compiler:
    """Wrapper class for interacting with the Compiler service.

    Provides a simple interface to compile quantum circuits using the CompilerClient.
    """

    def __init__(self):
        """
        Initialize the Compiler client and logger.
        """
        self._client = CompilerClient()
        self._logger = logging.getLogger(__name__)
        self._compilation_result = None
        self._status = None
        self._compiler_pipeline_id = None

    def _clear_cache(self):
        """
        Clear cached data in the Compiler instance.
        """
        self._compilation_result = None
        self._status = None
        self._compiler_pipeline_id = None

    def compile(
        self,
        circuit: Circuit,
        error_budget: float,
        remove_clifford_gates: bool = False,
        insights_only: bool = False,
        async_mode: bool = False,
        overwrite_result: bool = False,
    ) -> Union[CompilationResult, dict]:
        """Run the Compilation Pipeline.

        This method supports interactive interruption:

        **In a terminal:** While waiting for the job to complete,
        you can press Ctrl+C to interrupt polling.

        When interrupted, you will be prompted to choose one of the following options:

            1. Stop tracking the job (exit, job continues on server).
            2. Send a cancellation request to the server and exit.
            3. Resume waiting for the job to complete.

        **In a Jupyter notebook:** Interrupting the cell
        (by pressing the stop button `■` in the notebook interface)
        while the job is running in synchronous mode will cancel the job on the server.


        Args:
            circuit (Circuit): The quantum circuit to be processed.

            error_budget (float): Allowed synthesis error to be used.

            remove_clifford_gates (bool): Flag to determine whether or not to bypass
                the optimization stage.

            insights_only (bool): Flag to determine if the output of the
                scheduler is produced.
            async_mode (bool): Flag to determine whether to use async mode or not.
            overwrite_result (bool): Flag to overwrite existing results if they exists. Defaults to False.

        Returns:
            CompilationResult|dict: Result of the compilation run execution.
            Returns dict of `compiler_pipeline_id` and `status` if `async_mode` set to True.

        Raises:
            KeyboardInterrupt: If the job is interrupted by the user.
            ValueError: If existing results are present and overwrite_result is False.
            TopQADTimeoutError: If polling for the Compiler job times out.
            RuntimeError: If the Compiler job fails or polling times out.
        """
        # Check results for overwriting
        if not overwrite_result and (
            self._compilation_result is not None
            or self._compiler_pipeline_id is not None
        ):
            raise ValueError(
                "Existing results will be overwritten. Please set overwrite_result to True to continue"
            )
        # Reset cached data
        self._clear_cache()

        circuit_name = circuit.circuit_name
        self._logger.info(f"Starting compilation for circuit '{circuit_name}'...")

        if async_mode:
            # Submit request asyncronously
            try:
                response = self._client.run(
                    circuit=circuit,
                    error_budget=error_budget,
                    remove_clifford_gates=remove_clifford_gates,
                    insights_only=insights_only,
                )

                compiler_pipeline_id = response.compiler_pipeline_id
                self._compiler_pipeline_id = compiler_pipeline_id
                self._status = StatusEnum.WAITING

                self._logger.info(
                    f"Compiler request with compiler pipeline_id {compiler_pipeline_id} has been submitted. Please come back later and call get_results"
                )
            except Exception as e:
                self._logger.error(f"Compiler failed for circuit '{circuit_name}': {e}")
                raise RuntimeError(
                    f"Compiler failed for circuit '{circuit_name}'."
                ) from e

            return {
                "compiler_pipeline_id": self._compiler_pipeline_id,
                "status": self._status.value,
            }

        else:
            try:
                # Submit request syncronously
                result = self._client.run_and_get_results(
                    circuit=circuit,
                    error_budget=error_budget,
                    remove_clifford_gates=remove_clifford_gates,
                    insights_only=insights_only,
                )

                # update status and pipeline_id
                self.compiler_pipeline_id = result.compiler_pipeline_id
                self._status = StatusEnum(result.status)

            except KeyboardInterrupt:
                raise
            except TopQADTimeoutError as e:
                timeout_message = (
                    f" Please check the portal or call get_results() to"
                    f" see the status of this job and, upon completion, to obtain"
                    f" your results."
                )
                self._logger.error(timeout_message)
                raise TopQADTimeoutError(f"{e} {timeout_message}")
            except Exception as e:
                self._logger.error(
                    f"Compilation failed for circuit '{circuit_name}': {e}"
                )
                raise RuntimeError(
                    f"Compilation failed for circuit '{circuit_name}'."
                ) from e

            # Store results
            self._compilation_result = CompilationResult(result)

            return self._compilation_result

    def load(self, compiler_pipeline_id):
        """
        Retrieves and loads compiler pipeline information from server using given `compiler_pipeline_id`.
        This will overwrite existing information.

        Args:
            compiler_pipeline_id (str): The ID of the Compiler pipeline.

        Returns:
            dict: Status and compiler pipeline ID of request.
        """
        # Reset cached data
        self._clear_cache()

        try:
            response = self._client.get_result(compiler_pipeline_id)
        except Exception as e:
            err_msg = (
                f"Failed to load from compiler_pipeline_id {self._compiler_pipeline_id}"
            )
            self._logger.error(err_msg)
            raise TopQADError(err_msg) from e

        # update information
        self._status = StatusEnum(response.status)
        self._compiler_pipeline_id = compiler_pipeline_id

        if self._status == StatusEnum.DONE:
            # Store results
            self._compilation_result = CompilationResult(response)

        return {
            "compiler_pipeline_id": self._compiler_pipeline_id,
            "status": self._status.value,
        }

    def get_results(
        self,
    ):
        """
        Retrieve the Compiler results from the request if it has finished.

        Returns:
            CompilationResult: Result of the compilation run execution.
        """

        # Return results if it is already populated
        if self._compilation_result:
            self._logger.info(
                f"Existing results found for compiler pipeline ID {self._compiler_pipeline_id}. Returning..."
            )
            return self._compilation_result

        elif self._compiler_pipeline_id:
            self._logger.info(
                f"Existing compiler pipeline ID {self._compiler_pipeline_id} found. Requesting result from server..."
            )
            # Try to get result from server if compiler_pipeline_id is populated
            try:
                response = self._client.get_result(self._compiler_pipeline_id)
            except Exception as e:
                err_msg = f"Failed to get result from compiler_pipeline_id {self._compiler_pipeline_id}"
                self._logger.error(err_msg)
                raise TopQADError(err_msg)

            # update status
            self._status = StatusEnum(response.status)

            if self._status in FINISHED_STATUSES:
                # Retrieve result if request is finished
                if response.status == StatusEnum.DONE:

                    # Store results
                    self._compilation_result = CompilationResult(response)

                    return self._compilation_result
                else:
                    self._logger.error(
                        f"The request has not been completed due to the status being: {response.status}. Please resubmit another request."
                    )
                    return {
                        "compiler_pipeline_id": self._compiler_pipeline_id,
                        "status": self._status.value,
                        "message": response.message,
                    }

            else:
                msg = f"Pipeline request with compiler_pipeline_id {self._compiler_pipeline_id} is still in progress. Please check back later"
                self._logger.info(msg)
                return {
                    "compiler_pipeline_id": self._compiler_pipeline_id,
                    "status": self._status.value,
                }

        else:
            err_msg = "No Compiler request has been made. Please submit a request to obtain result"
            self._logger.error(err_msg)
            raise ValueError(err_msg)

    def cancel(self) -> dict:
        """
        Cancel a running Compiler job.

        This method allows the user to cancel the currently running job associated with this instance
        (i.e., the most recent job submitted).

        Returns:
            dict:
                - compiler_pipeline_id (str): The compiler pipeline ID of the request to be cancelled.
                - status (str): The status of the job after the cancel request, with possible values including "cancel_pending" (the cancel request was successful, and the job is being cancelled) or the current status of the job (e.g., "done", "failed", etc.) if the cancel request was declined or the job cannot be cancelled.
                - message (str): Information about the cancellation request.

        Raises:
            TopQADError: If the cancellation fails due to an internal error.
            ValueError: If no compiler pipeline ID is found.
        """
        if self._compiler_pipeline_id is None:
            self._logger.info(
                "No existing compiler_pipeline_id found to cancel. Please submit a Compiler job first."
            )
            raise ValueError("No existing compiler_pipeline_id found to cancel.")
        try:
            response = self._client.cancel(self._compiler_pipeline_id)
            self._logger.info(
                "Cancel request for compiler_pipeline_id %s has been submitted.",
                self._compiler_pipeline_id,
            )
            self._compilation_result = None
            # if cancel is successful, update status.
            # if cancel request is declined, status remains unchanged.
            if response.status == StatusEnum.CANCEL_PENDING:
                self._status = response.status

            return {
                "compiler_pipeline_id": self._compiler_pipeline_id,
                "status": self._status,
                "message": response.message,
            }
        except Exception as e:
            err_msg = f"Failed to cancel Compiler request with compiler_pipeline_id {self._compiler_pipeline_id}"
            self._logger.error(err_msg)
            raise TopQADError(err_msg) from e
