import os
import time
import configparser
from pydantic import ValidationError
from IPython.display import display, HTML
from topqad_sdk._utils import handle_keyboard_interrupt, is_notebook
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADValueError,
    TopQADRuntimeError,
    TopQADTimeoutError,
    TopQADSchemaError,
)
from topqad_sdk.models import (
    Circuit,
    CompilerPipelineRequest,
    CompilerPipelineResponse,
    CompilerPipelineSolutionResponse,
    CompilerPipelineCancelResponse,
    StatusEnum,
)
from topqad_sdk.clients._topqad_client import TopQADClient

DEFAULT_COMPILER_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class CompilerClient(TopQADClient):
    """
    CompilerClient provides methods for interacting with the Compiler pipeline endpoint.

    This class facilitates the submission of quantum circuit data and hardware parameters to the
    Compiler pipeline. It manages authentication headers through the AuthManager and ensures
    proper handling of responses and errors returned by the Compiler pipeline.
    """

    def __init__(
        self,
        retries: int = 3,
        retry_delay: int = 10,
        polling_interval: int = 10,
        polling_max_attempts: int = 10,
    ):
        """Initialize CompilerClient with polling and retry configuration.

        Args:
            retries (int, optional): Number of retries. Default is 3.
            retry_delay (int, optional): Delay between retries (sec). Default is 10.
            polling_interval (int, optional): Polling interval (sec). Default is 10.
            polling_max_attempts (int, optional): Max polling attempts. Default is 20.

        Raises:
            TopQADValueError: If polling_interval or polling_max_attempts are
                negative integers.
        """
        service_url = os.environ.get("COMPILER_URL", DEFAULT_COMPILER_URL)
        super().__init__(
            service_url=service_url, retries=retries, retry_delay=retry_delay
        )

        if polling_interval <= 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")

        if polling_max_attempts <= 0:
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )

        self._polling_interval = polling_interval
        self._polling_max_attempts = polling_max_attempts

        self._logger.debug(
            "Initializing CompilerClient with retries=%d, retry_delay=%d, "
            "polling_interval=%d, polling_max_attempts=%d",
            retries,
            retry_delay,
            polling_interval,
            polling_max_attempts,
        )

    def run(
        self,
        circuit: Circuit,
        error_budget: float,
        remove_clifford_gates: bool = False,
        insights_only: bool = False,
    ) -> CompilerPipelineResponse:
        """Run the Compiler pipeline.

        Args:
            circuit: The quantum circuit to be processed.

            error_budget: Allowed synthesis error to be used.

            remove_clifford_gates: Flag to determine whether or not to bypass
                the optimization stage.

            insights_only: Flag to determine if the output of the
                scheduler is produced.

        Returns:
            CompilerPipelineResponse: Compiler pipeline response object contains the compiler pipeline ID and status.

        Raises:
            TopQADValueError: If there are missing or incorrect fields.
            TopQADError: If the request to run the Compiler pipeline fails.

        """
        if not circuit or not isinstance(circuit, Circuit):
            raise TopQADValueError("Invalid circuit provided.")
        if not error_budget:
            raise TopQADValueError("Error budget must be provided.")

        payload = {
            "circuit_id": circuit.id,
            "global_error_budget": error_budget,
            "remove_clifford_gates": remove_clifford_gates,
            "insights_only": insights_only,
        }
        try:
            payload_model = CompilerPipelineRequest.model_validate(payload)
        except ValidationError as e:
            raise TopQADValueError(
                f"Some fields are missing or incorrect: \n{e.errors()}"
            ) from e

        request_payload = payload_model.model_dump()
        try:
            response = self._post("/compiler", json=request_payload)
            self._logger.info("Compiler job submitted successfully.")
            response_model = CompilerPipelineResponse.model_validate(response)
            return response_model
        except ValidationError as e:
            self._logger.error("Error in server response")
            raise TopQADError(f"Error on server response\n{e}")
        except Exception as e:
            self._logger.error("Failed to run compilation pipeline.")
            raise TopQADError(f"Failed to run compilation pipeline. \n{e}") from e

    def get_result(self, compiler_pipeline_id: str) -> CompilerPipelineSolutionResponse:
        """Get results of a compilation pipeline run.

        Args:
            compiler_pipeline_id: The ID of the Compiler pipeline solution to retrieve.

        Returns:
            CompilerPipelineSolutionResponse: The response containing the result of the Compiler pipeline job.

        Raises:
            TopQADValueError: If `compiler_pipeline_id` is not provided.
            TopQADError: If the request to get the result fails.
        """
        if not compiler_pipeline_id:
            raise TopQADValueError("Request ID must be provided")

        self._logger.info(
            "Fetching result for compilation pipeline ID {compiler_pipeline_id}..."
        )
        try:
            response = self._get(f"/compiler/{compiler_pipeline_id}")
            response_model = CompilerPipelineSolutionResponse.model_validate(response)
            return response_model
        except ValidationError as e:
            raise TopQADError(f"Invalid response from server:\n{e.errors()}") from e
        except Exception as e:
            self._logger.error(
                "Failed to get result for compiler pipeline ID %s.",
                compiler_pipeline_id,
            )
            raise TopQADError(
                f"Failed to get result for compiler pipeline ID {compiler_pipeline_id}.\n{e}"
            ) from e

    def run_and_get_results(
        self,
        circuit: Circuit,
        error_budget: float,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> CompilerPipelineSolutionResponse:
        """Run the Compiler pipeline and poll the server for a result.

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

        Note:
            Default polling interval is 10 seconds, and maximum attempts is 20.
            In case of timeout, pass higher values for `polling_interval` and
            `polling_max_attempts` when initializing the CompilerClient
            using its constructor.

        Args:
            circuit: The circuit to be compiled.

            error_budget: Allowed synthesis error to be used.

            remove_clifford_gates: Flag to determine whether or not to bypass
                the optimization stage.

            insights_only: Flag to determine if the output of the
                scheduler is produced.

        Returns:
            CompilerPipelineSolutionResponse: The response containing the result of the Compiler pipeline job.

        Raises:
            TopQADValueError: If the request has missing or incorrect fields,
                or if the server response is missing a request id
            TopQADTimeoutError: If the job submission or polling fails.
            TopQADRuntimeError: If the request to run the Compiler pipeline fails.

        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            response = self.run(
                circuit,
                error_budget,
                remove_clifford_gates,
                insights_only,
            )
        except TopQADError as e:
            raise e from None
        except Exception as e:
            raise TopQADError(f"Server error while submitting job\n{e}") from e

        try:
            if is_notebook():
                display(
                    HTML(
                        '<span style="color: #04afef; font-weight: bold;">Warning: Interrupting the cell while Compiler is running in synchronous mode will cancel the job on the server.</span>'
                    ),
                    display_id="cancel_msg",
                )
            else:
                self._logger.info(
                    "\033[1;38;5;208mPress Ctrl+C to cancel this Compiler job if needed.\033[0m"
                )
            compiler_pipeline_id = getattr(response, "compiler_pipeline_id", None)
            if not compiler_pipeline_id:
                raise TopQADValueError("Request ID not found in response.")
            compiler_pipeline_name = getattr(response, "name", None)
            self._logger.info("Polling results for request %s...", compiler_pipeline_id)
            result = None
            attempts = 0
            while attempts < self._polling_max_attempts:
                try:
                    self._logger.warning(
                        "Polling for request %s: attempt %d/%d",
                        compiler_pipeline_id,
                        attempts + 1,
                        self._polling_max_attempts,
                    )
                    result = self.get_result(compiler_pipeline_id)
                    status = getattr(result, "status")
                    if status == "done":
                        return result
                    elif status == "failed":
                        # throw failed run error
                        raise TopQADRuntimeError(
                            f"Compilation pipeline {compiler_pipeline_id} failed: "
                        )

                    time.sleep(self._polling_interval)
                    attempts += 1
                except KeyboardInterrupt:
                    if is_notebook():
                        self._logger.info(
                            "\033[1;36mJob interrupted in notebook. No interactive prompt available.\n"
                            "Sending cancellation request for '%s' (Job ID: %s) to the server.\033[0m",
                            compiler_pipeline_name,
                            compiler_pipeline_id,
                        )
                        self.cancel(compiler_pipeline_id)
                        raise KeyboardInterrupt(
                            "Job interrupted in notebook. Cancellation request sent to server."
                        )
                    else:
                        action = handle_keyboard_interrupt(
                            compiler_pipeline_name,
                            compiler_pipeline_id,
                            self._logger,
                            self,
                        )
                        if action == "resume":
                            continue  # Resume polling

            if result is None or getattr(result, "status", None) != "done":
                polling_timeout_message = (
                    f"The job with ID {compiler_pipeline_id} timed out before the results"
                    f" were ready."
                )
                self._logger.error(polling_timeout_message)
                raise TopQADTimeoutError(polling_timeout_message)
        except KeyboardInterrupt:
            raise
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for the Compiler.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for compilation pipeline. \n{e}"
            ) from e

    def cancel(self, compiler_pipeline_id: str) -> CompilerPipelineCancelResponse:
        """Cancel a running Compiler pipeline by its ID.

        Args:
            compiler_pipeline_id: The ID of the Compiler pipeline job to cancel.

        Returns:
            CompilerPipelineCancelResponse: The response from the Compiler pipeline after attempting to cancel the job.

        Raises:
            TopQADValueError: If `compiler_pipeline_id` is not provided.
            TopQADError: If the request to cancel the Compiler pipeline fails.
            TopQADSchemaError: If the response is not of type CompilerPipelineResponse.
        """
        if not compiler_pipeline_id:
            raise TopQADValueError("Compiler Pipeline ID must be provided.")
        self._logger.info(
            "Cancelling a job for Compiler Pipeline ID %s...", compiler_pipeline_id
        )
        try:
            response = self._post(f"/compiler/cancel/{compiler_pipeline_id}")
            validated_response = CompilerPipelineCancelResponse.model_validate(response)
            if validated_response.status == StatusEnum.CANCEL_PENDING:
                self._logger.info(
                    f"Successfully requested to cancel a job for Compiler Pipeline ID {compiler_pipeline_id}. "
                )
            elif validated_response.status == StatusEnum.FAILED:
                self._logger.warning(
                    "Cancel request for Compiler Pipeline ID '%s' was declined. Error message: %s",
                    compiler_pipeline_id,
                    validated_response.message,
                )
            return validated_response
        except ValidationError as e:
            self._logger.error("Invalid response from server:\n%s", e.errors())
            raise TopQADSchemaError(
                f"Invalid response from server:\n{e.errors()}"
            ) from e
        except Exception as e:
            self._logger.error(
                "Exception during cancellation for Compiler Pipeline ID %s: %s",
                compiler_pipeline_id,
                e,
            )
            raise TopQADError(
                f"Failed to cancel job for Compiler Pipeline ID {compiler_pipeline_id}. \n{e}"
            ) from e
