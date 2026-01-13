import os
import time
import configparser
from typing import overload
from pydantic import ValidationError
from IPython.display import display, HTML

from topqad_sdk._utils import handle_keyboard_interrupt, is_notebook
from topqad_sdk.library import HardwareParameters
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADValueError,
    TopQADRuntimeError,
    TopQADSchemaError,
    TopQADTimeoutError,
)
from topqad_sdk.models import (
    Circuit,
    LiteCircuit,
    PipelineRequest,
    PipelineResponse,
    PipelineSolutionResponse,
    PipelineCancelResponse,
    DemoNoiseProfilerSpecs,
    StatusEnum,
)
from topqad_sdk.models.circuit_library.circuit import LiteCircuit
from ._topqad_client import TopQADClient


DEFAULT_QRE_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class QREClient(TopQADClient):
    """QREClient provides methods for interacting with the QRE pipeline endpoints.

    This class facilitates the submission of circuit data and hardware parameters to the
    QRE pipeline. It manages authentication headers through the Auth Manager
    and ensures proper handling of responses and errors returned by the QRE
    pipeline.
    """

    def __init__(
        self,
        retries: int = 3,
        retry_delay: int = 10,
        polling_interval: int = 10,
        polling_max_attempts: int = 20,
    ):
        """Initialize QREClient with polling and retry configuration.

        Args:
            retries (int, optional): Number of retries. Default is 3.
            retry_delay (int, optional): Delay between retries (sec). Default is 10.
            polling_interval (int, optional): Polling interval (sec). Default is 10.
            polling_max_attempts (int, optional): Max polling attempts. Default is 20.

        Raises:
            TopQADValueError: If polling_interval or polling_max_attempts are
                negative integers.
        """
        service_url = os.environ.get("QRE_URL", DEFAULT_QRE_URL)
        super().__init__(
            service_url=service_url,
            retries=retries,
            retry_delay=retry_delay,
        )
        self._polling_interval = polling_interval
        self._polling_max_attempts = polling_max_attempts
        if not isinstance(self._polling_interval, int) or self._polling_interval < 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")
        if (
            not isinstance(self._polling_max_attempts, int)
            or self._polling_max_attempts < 0
        ):
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )
        self._logger.debug(
            "Initializing QREClient with retries=%d, retry_delay=%d, "
            "polling_interval=%d, polling_max_attempts=%d",
            retries,
            retry_delay,
            polling_interval,
            polling_max_attempts,
        )

    @overload
    def run(
        self,
        circuit: LiteCircuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        cost: float = 0,
    ) -> PipelineResponse: ...

    @overload
    def run(
        self,
        circuit: Circuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineResponse: ...

    def run(
        self,
        circuit: Circuit | LiteCircuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineResponse:
        """Run a new QRE pipeline.

        Args:
            circuit (Circuit): Either a Circuit object or a LiteCircuit object.
            hardware_params (HardwareParameters | DemoNoiseProfilerSpecs):
                Hardware parameters or demo spec.
            global_error_budget (float): The global error budget for the pipeline.
            timeout (str, optional): Timeout for pipeline execution.
                Defaults to "0".
            number_of_repetitions (int, optional): Number of repetitions.
                Defaults to 1.
            cost (float, optional): Cost for the pipeline.
                Defaults to 0.
            remove_clifford_gates (bool, optional): Whether to remove Clifford gates.
                Defaults to True.
            insights_only (bool, optional): Whether to generate a schedule only.
                Defaults to False.

        Returns:
            PipelineResponse: The response from the QRE pipeline containing the pipeline ID.

        Raises:
            TopQADSchemaError: If `hardware_params` or `circuit` are invalid.
            TopQADValueError: If `circuit` or `global_error_budget` is not provided.
            TopQADSchemaError: If the response is not of type PipelineResponse.
            TopQADError: If the request to run the QRE pipeline fails.
        """
        if not hardware_params or not isinstance(
            hardware_params, (HardwareParameters, DemoNoiseProfilerSpecs)
        ):
            raise TopQADSchemaError("Invalid hardware parameters provided.")
        if not global_error_budget:
            raise TopQADValueError("Global error budget must be provided.")
        if not isinstance(circuit, (Circuit, LiteCircuit)):
            raise TopQADValueError(
                "Invalid circuit type provided. Must be Circuit or LiteCircuit."
            )
        if isinstance(hardware_params, HardwareParameters):
            ftqc_params = hardware_params.as_dict
        else:
            ftqc_params = hardware_params.value  # DemoNoiseProfilerSpecs

        self._logger.info("Submitting QRE pipeline job...")

        try:
            if isinstance(circuit, LiteCircuit):
                self._logger.info("Building payload for lite mode job...")
                payload = {
                    "simplified_circuit": {
                        "num_qubits": circuit.num_qubits,
                        "num_operations": circuit.num_operations,
                    },
                    "start_step": "lite",
                    "ftqc_params": ftqc_params,
                    "global_error_budget": global_error_budget,
                    "timeout": timeout,
                    "cost": cost,
                }
                response = self._post("/pipeline", json=payload)

            else:
                self._logger.info("Building and sending payload for full mode job...")
                payload = {
                    "circuit_id": circuit.id,
                    "ftqc_params": ftqc_params,
                    "global_error_budget": global_error_budget,
                    "timeout": timeout,
                    "number_of_repetitions": number_of_repetitions,
                    "cost": cost,
                    "bypass_optimization": not remove_clifford_gates,
                    "generate_schedule": insights_only,
                }
                # We will use Pydantic validation only for the full mode.
                validated_request = PipelineRequest.model_validate(payload)
                request_as_dict = validated_request.model_dump(exclude_none=True)
                response = self._post("/pipeline", json=request_as_dict)

            self._logger.info("QRE job submitted successfully.")
            validated_response = PipelineResponse.model_validate(response)
            return validated_response

        except Exception as e:
            self._logger.error("Failed to run QRE job.")
            raise TopQADError(f"Failed to run QRE job. \n{e}") from e

    def get_result(self, pipeline_id: str) -> PipelineSolutionResponse:
        """Get results for a specific QRE pipeline solution by ID.

        Args:
            request_id (str): The ID of the QRE pipeline solution to retrieve.

        Returns:
            PipelineSolutionResponse: The response containing the result of the QRE pipeline job.

        Raises:
            TopQADValueError: If `request_id` is not provided.
            TopQADError: If the request to get the result fails.
            TopQADSchemaError: If the response is not of type PipelineSolutionResponse.
        """
        if not pipeline_id:
            raise TopQADValueError("Request ID must be provided.")
        self._logger.info("Fetching result for pipeline ID %s...", pipeline_id)
        try:
            response = self._get(f"/pipeline/{pipeline_id}")
            self._logger.info(
                "Result fetched successfully for pipeline ID %s.", pipeline_id
            )
            validated_response = PipelineSolutionResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error(
                "Failed to fetch result for pipeline ID %s.", pipeline_id
            )
            raise TopQADError(
                f"Failed to get result for pipeline ID {pipeline_id}. \n{e}"
            ) from e

    def list_results(self) -> list[PipelineSolutionResponse]:
        """List all QRE pipeline solutions for the authenticated user.

        Returns:
            list[PipelineSolutionResponse]: A list of QRE pipeline solutions
            for the user.

        Raises:
            TopQADSchemaError: If the response is not of type list[PipelineSolutionResponse].
            TopQADError: If the request to list results fails.
        """
        self._logger.info("Listing QRE pipeline results...")
        try:
            user_id = self._client._auth_manager.get_user_id()
            response = self._get(f"/pipeline/user/{user_id}")
            validated_response = [
                PipelineSolutionResponse.model_validate(item) for item in response
            ]
            return validated_response
        except Exception as e:
            self._logger.error("Failed to list results for user ID %s.", user_id)
            raise TopQADError(
                f"Failed to get result for user ID {user_id}. \n{e}"
            ) from e

    @overload
    def run_and_get_result(
        self,
        circuit: LiteCircuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
    ) -> PipelineSolutionResponse: ...

    @overload
    def run_and_get_result(
        self,
        circuit: Circuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineSolutionResponse: ...

    def run_and_get_result(
        self,
        circuit: Circuit | LiteCircuit,
        hardware_params: HardwareParameters | DemoNoiseProfilerSpecs,
        global_error_budget: float,
        timeout: str = "0",
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
    ) -> PipelineSolutionResponse:
        """Submit a QRE pipeline job and poll for its result until completion.

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
            `polling_max_attempts` when initializing the QREClient
            using its constructor.

        Args:
            circuit (Circuit): The quantum circuit to be processed.
            hardware_params (HardwareParameters | DemoNoiseProfilerSpecs):
                Hardware parameters or demo spec.
            global_error_budget (float): The global error budget for the pipeline.
            timeout (str): The timeout for the pipeline execution.
                Defaults to "0".
            number_of_repetitions (int): The number of repetitions for the pipeline.
                Defaults to 1.
            cost (float): The cost for the pipeline.
                Defaults to 0.
            remove_clifford_gates (bool): Whether to remove clifford gates.
                Defaults to True.
            insights_only (bool): Whether to generate a schedule.
                Defaults to False.

        Returns:
            PipelineSolutionResponse: Final result of the QRE pipeline job.

        Raises:
            TopQADSchemaError: If `hardware_params` or `circuit` are invalid.
            TopQADValueError: If `circuit` or `global_error_budget` is not provided.
            TopQADRuntimeError: If the request to run the QRE pipeline fails.
        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            # Submit the job
            response = self.run(
                circuit=circuit,
                hardware_params=hardware_params,
                global_error_budget=global_error_budget,
                timeout=timeout,
                number_of_repetitions=number_of_repetitions,
                cost=cost,
                remove_clifford_gates=remove_clifford_gates,
                insights_only=insights_only,
            )
            if is_notebook():
                display(
                    HTML(
                        '<span style="color: #04afef; font-weight: bold;">Warning: Interrupting the cell while QRE is running in synchronous mode will cancel the job on the server.</span>'
                    ),
                    display_id="cancel_msg",
                )
            else:
                self._logger.info(
                    "\033[1;38;5;208mPress Ctrl+C to cancel this QRE job if needed.\033[0m"
                )
            pipeline_id = getattr(response, "pipeline_id", None)
            if not pipeline_id:
                raise TopQADValueError("Pipeline ID not found in response.")
            pipeline_name = getattr(response, "name", None)
            self._logger.info("Polling for pipeline ID %s result...", pipeline_id)
            # Poll for the result with retry logic
            result = None
            attempts = 0
            while attempts < self._polling_max_attempts:
                try:
                    polling_attempt_message = (
                        f"Polling for pipeline ID {pipeline_id}: attempt {attempts + 1}/"
                        f"{self._polling_max_attempts}."
                    )
                    self._logger.warning(polling_attempt_message)
                    result = self.get_result(pipeline_id)
                    if getattr(result, "status") == "done":
                        self._logger.info(
                            "Pipeline ID %s completed successfully.", pipeline_id
                        )
                        return result
                    elif getattr(result, "status") == "failed":
                        pipeline_failure_message = getattr(result, "message", None)
                        message = (
                            f"Pipeline {pipeline_id} failed: "
                            f"{pipeline_failure_message}."
                        )
                        self._logger.error(message)
                        raise TopQADRuntimeError(message)
                    # Wait before the next attempt
                    time.sleep(self._polling_interval)
                    attempts += 1
                except KeyboardInterrupt:
                    if is_notebook():
                        self._logger.info(
                            "\033[1;36mJob interrupted in notebook. No interactive prompt available.\n"
                            "Sending cancellation request for '%s' (Job ID: %s) to the server.\033[0m",
                            pipeline_name,
                            pipeline_id,
                        )
                        self.cancel(pipeline_id)
                        raise KeyboardInterrupt(
                            "Job interrupted in notebook. Cancellation request sent to server."
                        )
                    else:
                        action = handle_keyboard_interrupt(
                            pipeline_name,
                            pipeline_id,
                            self._logger,
                            self,
                        )
                        if action == "resume":
                            continue  # Resume polling
            if result is None or getattr(result, "status", None) != "done":
                polling_timeout_message = (
                    f"The job with ID {pipeline_id} timed out before the results"
                    f" were ready."
                )
                self._logger.error(polling_timeout_message)
                raise TopQADTimeoutError(polling_timeout_message)
        except KeyboardInterrupt:
            raise
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for QRE pipeline.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for QRE pipeline. \n{e}"
            ) from e

    def cancel(self, pipeline_id: str) -> PipelineCancelResponse:
        """Cancel a running QRE pipeline by its ID.

        Args:
            pipeline_id (str): The ID of the QRE pipeline to cancel.

        Returns:
            PipelineCancelResponse: The response from the QRE pipeline after attempting to cancel the job.

        Raises:
            TopQADValueError: If `pipeline_id` is not provided.
            TopQADError: If the request to cancel the pipeline fails.
            TopQADSchemaError: If the response is not of type PipelineResponse.
        """
        if not pipeline_id:
            raise TopQADValueError("Pipeline ID must be provided.")
        self._logger.info("Cancelling a job for pipeline ID %s...", pipeline_id)
        try:
            response = self._post(f"/pipeline/cancel/{pipeline_id}")
            validated_response = PipelineCancelResponse.model_validate(response)
            if validated_response.status == StatusEnum.CANCEL_PENDING:
                self._logger.info(
                    f"Successfully requested to cancel a job for Pipeline ID {pipeline_id}. "
                )
            elif validated_response.status == StatusEnum.FAILED:
                self._logger.warning(
                    "Cancel request for Pipeline ID '%s' was declined. Error message: %s",
                    pipeline_id,
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
                "Exception during cancellation for pipeline ID %s: %s", pipeline_id, e
            )
            raise TopQADError(
                f"Failed to cancel job for pipeline ID {pipeline_id}. \n{e}"
            ) from e
