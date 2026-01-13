import os
import time
import configparser
from pathlib import Path
from pydantic import ValidationError
from IPython.display import display, HTML
from topqad_sdk._utils import handle_keyboard_interrupt, is_notebook
from ._topqad_client import TopQADClient
from topqad_sdk.library import HardwareParameters
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADValueError,
    TopQADRuntimeError,
    TopQADSchemaError,
    TopQADTimeoutError,
)
from topqad_sdk.models import (
    FTQCResponse,
    FTQCSolutionResponse,
    FTQCCancelResponse,
    StatusEnum,
)

DEFAULT_NOISE_PROFILER_URL = "https://ftqc.portal.topqad.1qbit-dev.com"


class NoiseProfilerClient(TopQADClient):
    """NoiseProfilerClient provides methods for interacting with the Noise Profiler endpoints.

    This class facilitates the submission of circuit data and hardware parameters to the
    Noise Profiler. It manages authentication headers through the Auth Manager
    and ensures proper handling of responses and errors returned by the Noise Profiler.
    """

    def __init__(
        self,
        retries: int = 3,
        retry_delay: int = 10,
        polling_interval: int = 20,
        polling_max_attempts: int = 20,
    ):
        """Initialize NoiseProfilerClient with polling and retry config.

        Args:
            retries (int, optional): Number of retries. Default is 3.
            retry_delay (int, optional): Delay between retries (sec). Default is 10.
            polling_interval (int, optional): Polling interval (sec). Default is 20.
            polling_max_attempts (int, optional): Max polling attempts. Default is 20.

        Raises:
            TopQADValueError: If `polling_interval` or `polling_max_attempts` are
                negative integers.
        """
        service_url = os.environ.get("NOISE_PROFILER_URL", DEFAULT_NOISE_PROFILER_URL)
        super().__init__(
            service_url=service_url,
            retries=retries,
            retry_delay=retry_delay,
        )
        self._polling_interval = polling_interval
        self._polling_max_attempts = polling_max_attempts
        self._logger.debug(
            "Initializing NoiseProfilerClient with retries=%d, retry_delay=%d, "
            "polling_interval=%d, polling_max_attempts=%d",
            retries,
            retry_delay,
            polling_interval,
            polling_max_attempts,
        )
        if not isinstance(self._polling_interval, int) or self._polling_interval < 0:
            raise TopQADValueError("Polling interval must be a non-negative integer.")
        if (
            not isinstance(self._polling_max_attempts, int)
            or self._polling_max_attempts < 0
        ):
            raise TopQADValueError(
                "Polling max attempts must be a non-negative integer."
            )

    def run(self, hardware_params: HardwareParameters) -> FTQCResponse:
        """Run a new Noise Profiler.

        Args:
            hardware_params (HardwareParameters): The hardware parameters for the FTQC
                emulator.

        Returns:
            FTQCResponse: The response from Noise Profiler containing its request ID.

        Raises:
            TopQADSchemaError: If hardware_params is not an instance of HardwareParameters.
            TopQADSchemaError: If the response is not of type FTQCResponse.
            TopQADError: If the request to run the Noise Profiler fails.
        """
        self._logger.info("Submitting Noise Profiler job...")
        if not isinstance(hardware_params, HardwareParameters):
            raise TopQADSchemaError(
                "hardware_params must be an instance of HardwareParameters."
            )
        payload = hardware_params.as_dict
        try:
            response = self._post("/emulate", json=payload)
            self._logger.info("Noise Profiler job submitted successfully.")
            validated_response = FTQCResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error("Failed to run Noise Profiler.")
            raise TopQADError(f"Failed to run Noise Profiler. \n{e}") from e

    def get_result(self, request_id: str) -> FTQCSolutionResponse:
        """Get results for a specific FTQC solution by ID.

        Args:
            request_id (str): The ID of the Noise Profiler solution to retrieve.

        Returns:
            FTQCSolutionResponse: The response containing the result of the FTQC emulator job.

        Raises:
            TopQADValueError: If `request_id` is not provided.
            TopQADError: If the request to get the result fails.
            TopQADSchemaError: If the response is not of type FTQCSolutionResponse.
        """
        self._logger.info("Fetching result for request ID %s...", request_id)
        if not request_id:
            raise TopQADValueError("Request ID must be provided.")
        try:
            response = self._get(f"/emulate/{request_id}")
            validated_response = FTQCSolutionResponse.model_validate(response)
            return validated_response
        except Exception as e:
            self._logger.error("Failed to get result for request ID %s.", request_id)
            raise TopQADError(
                f"Failed to get result for request ID {request_id}. \n{e}"
            ) from e

    def list_results(self) -> list[FTQCSolutionResponse]:
        """List all Noise Profiler solutions for the authenticated user.

        Returns:
            list[FTQCSolutionResponse]: A list of Noise Profiler solutions for the user.

        Raises:
            TopQADSchemaError: If the response is not of type list[FTQCSolutionResponse].
            TopQADError: If the request to list results fails.
        """
        self._logger.info("Listing Noise Profiler results...")
        try:
            user_id = self._client._auth_manager.get_user_id()
            response = self._get(f"/emulate/user/{user_id}")
            validated_response = [
                FTQCSolutionResponse.model_validate(item) for item in response
            ]
            return validated_response
        except Exception as e:
            self._logger.error("Failed to list results for user ID %s.", user_id)
            raise TopQADError(
                f"Failed to get result for user ID {user_id}. \n{e}"
            ) from e

    def run_and_get_result(
        self, hardware_params: HardwareParameters
    ) -> FTQCSolutionResponse:
        """Submit a Noise Profiler job and poll for its result until completion.

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
            Default polling interval is 20 seconds, and maximum attempts is 20.
            In case of timeout, pass higher values for `polling_interval` and
            `polling_max_attempts` when initializing the NoiseProfilerClient
            using its constructor.

        Args:
            hardware_params (HardwareParameters): The hardware parameters for
                the Noise Profiler.

        Returns:
            FTQCSolutionResponse: Final result of the Noise Profiler job.

        Raises:
            TopQADValueError: If `hardware_params` is not an instance of HardwareParameters.
            TopQADTimeoutError: If the job submission or polling fails.
            TopQADRuntimeError: If the request to run the Noise Profiler fails.
        """
        self._logger.info("Starting run_and_get_result process...")
        try:
            # Submit the job
            response = self.run(hardware_params=hardware_params)
            request_id = getattr(response, "request_id", None)
            if is_notebook():
                display(
                    HTML(
                        '<span style="color: #04afef; font-weight: bold;">Warning: Interrupting the cell while Noise Profiler is running in synchronous mode will cancel the job on the server.</span>'
                    ),
                    display_id="cancel_msg",
                )
            else:
                self._logger.info(
                    "\033[1;38;5;208mPress Ctrl+C to cancel this Noise Profiler job if needed.\033[0m"
                )
            if not request_id:
                raise TopQADValueError("Request ID not found in response.")
            request_name = getattr(response, "name", None)
            # Poll for the result with retry logic
            self._logger.info("Polling for request %s result...", request_id)
            result = None
            attempts = 0
            while attempts < self._polling_max_attempts:
                try:
                    self._logger.warning(
                        "Polling for request %s: attempt %d/%d",
                        request_id,
                        attempts + 1,
                        self._polling_max_attempts,
                    )
                    result = self.get_result(request_id)
                    if getattr(result, "status") == "done":
                        return result
                    elif getattr(result, "status") == "failed":
                        raise TopQADRuntimeError(
                            f"Noise Profiler {request_id} failed: "
                            f"{getattr(result, 'message', None)}"
                        )
                    # Wait before the next attempt
                    time.sleep(self._polling_interval)
                    attempts += 1
                except KeyboardInterrupt:
                    if is_notebook():
                        self._logger.info(
                            "\033[1;36mJob interrupted in notebook. No interactive prompt available.\n"
                            "Sending cancellation request for '%s' (Job ID: %s) to the server.\033[0m",
                            request_name,
                            request_id,
                        )
                        self.cancel(request_id)
                        raise KeyboardInterrupt(
                            "Job interrupted in notebook. Cancellation request sent to server."
                        )
                    else:
                        action = handle_keyboard_interrupt(
                            "Noise Profiler",
                            request_id,
                            self._logger,
                            self,
                        )
                        if action == "resume":
                            continue  # Resume polling

            if result is None or getattr(result, "status", None) != "done":
                polling_timeout_message = (
                    f"The job with ID {request_id} timed out before the results"
                    f" were ready."
                )
                self._logger.error(polling_timeout_message)
                raise TopQADTimeoutError(polling_timeout_message)
        except KeyboardInterrupt:
            raise
        except TopQADTimeoutError as e:
            raise e
        except Exception as e:
            self._logger.error("Failed to run and get result for Noise Profiler.")
            raise TopQADRuntimeError(
                f"Failed to run and get result for Noise Profiler. \n{e}"
            ) from e

    def cancel(self, request_id: str) -> FTQCCancelResponse:
        """Cancel a running Noise Profiler job by its ID.

        Args:
            request_id (str): The ID of the Noise Profiler job to cancel.

        Returns:
            FTQCCancelResponse: The response from the Noise Profiler after attempting to cancel the job.

        Raises:
            TopQADValueError: If `request_id` is not provided.
            TopQADError: If the request to cancel the Noise Profiler job fails.
            TopQADSchemaError: If the response is not of type FTQCResponse.
        """
        if not request_id:
            raise TopQADValueError("Request ID must be provided.")
        self._logger.info("Cancelling a job for request ID %s...", request_id)
        try:
            response = self._post(f"/cancel/{request_id}")
            validated_response = FTQCCancelResponse.model_validate(response)
            if validated_response.status == StatusEnum.CANCEL_PENDING:
                self._logger.info(
                    f"Successfully requested to cancel a job for Request ID {request_id}. "
                )
            elif validated_response.status == StatusEnum.FAILED:
                self._logger.warning(
                    "Cancel request for Request ID '%s' was declined. Error message: %s",
                    request_id,
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
                "Exception during cancellation for request ID %s: %s", request_id, e
            )
            raise TopQADError(
                f"Failed to cancel job for request ID {request_id}. \n{e}"
            ) from e
