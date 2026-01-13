import logging
from pathlib import Path
from typing import overload, Union

from topqad_sdk.clients.qre_client import QREClient
from topqad_sdk.models import (
    Circuit,
    LiteCircuit,
    DemoNoiseProfilerSpecs,
    FINISHED_STATUSES,
    StatusEnum,
    QREMode,
)
from topqad_sdk.library import HardwareParameters
from topqad_sdk.quantum_resource_estimator.qre_output import (
    QREOutputs,
    build_report_views,
    determine_mode,
    download_reports,
)
from topqad_sdk._exceptions import (
    TopQADError,
    TopQADTimeoutError,
)


class QuantumResourceEstimator:
    """
    Wrapper class for TopQAD's Quantum Resource Estimator (QRE) API.

    Provides a simple interface to estimate quantum resources for a circuit
    on specified hardware parameters.
    """

    def __init__(self):
        """
        Initialize the QRE client and logger.

        """
        self._client = QREClient()
        self._logger = logging.getLogger(__name__)
        self._reports = None
        self._reports_download = None
        self._status = None
        self._pipeline_id = None
        self._mode = None

    def _clear_cache(self):
        """
        Clear cached data in the QuantumResourceEstimator instance.
        """
        self._reports = None
        self._reports_download = None
        self._status = None
        self._pipeline_id = None
        self._mode = None

    @overload
    def run(
        self,
        circuit: LiteCircuit,
        hardware_parameters: HardwareParameters | str,
        global_error_budget: float,
        timeout: str = "0",
        async_mode: bool = False,
        *,
        download_reports_flag: bool = False,
        cost: float = 0,
        reports_output_file: str | Path = "reports.json",
        overwrite_reports: bool = False,
    ) -> Union[QREOutputs, dict]: ...

    @overload
    def run(
        self,
        circuit: Circuit,
        hardware_parameters: HardwareParameters | str,
        global_error_budget: float,
        async_mode: bool = False,
        *,
        download_reports_flag: bool = False,
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
        reports_output_file: str | Path = "reports.json",
        overwrite_reports: bool = False,
    ) -> Union[QREOutputs, dict]: ...

    def run(
        self,
        circuit: Circuit | LiteCircuit,
        hardware_parameters: HardwareParameters | str,
        global_error_budget: float,
        async_mode: bool = False,
        *,
        download_reports_flag: bool = False,
        number_of_repetitions: int = 1,
        cost: float = 0,
        remove_clifford_gates: bool = True,
        insights_only: bool = False,
        reports_output_file: str | Path = "reports.json",
        overwrite_reports: bool = False,
    ) -> Union[QREOutputs, dict]:
        """
        Estimate quantum resources for a given circuit.

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
            circuit (Circuit | LiteCircuit): The quantum circuit to estimate. Use LiteCircuit for streamlined estimation.
            hardware_parameters (HardwareParameters | str):
                A HardwareParameters object or one of the strings: "baseline", "desired",
                or "target".
            global_error_budget (float): Maximum allowable error for the circuit.
            async_mode (bool, optional): When enabled, allows asynchronous execution.
                Defaults to False. This feature is not available in the Beta version.
            download_reports_flag (bool, optional): When enabled, download detailed reports to
                the path specified in the `reports_output_file`. Defaults to False.
            number_of_repetitions (int, optional): Number of repetitions. Defaults to 1.
            cost (float, optional): Cost for QRE execution. Defaults to 0.
            remove_clifford_gates (bool, optional): Whether to remove Clifford gates. Defaults to True.
            insights_only (bool, optional): Whether to only generate insights (skip scheduling). Defaults to False.
            reports_output_file (str | Path, optional): Output file for downloaded reports. Only applicable if `download_reports_flag` is True. Defaults to "reports.json".
            overwrite_reports (bool): Flag to overwrite existing reports if they exists. Defaults to False.

        Returns:
            QREOutputs|dict: Contains the generated reports, viewable as an HTML table in Jupyter or as the raw dictionary.
            Returns dict of `pipeline_id` and `status` if `async_mode` set to True.

        Raises:
            KeyboardInterrupt: If the job is interrupted by the user.
            ValueError: If hardware_parameters is not a valid HardwareParameters object
                or an accepted string.
            ValueError: If the pipeline ID is not found in the response.
            TopQADTimeoutError: If polling for the QRE job times out.
            RuntimeError: If the QRE job fails or polling times out.
        """

        # Check reports for overwriting results
        if not overwrite_reports and (
            self._reports is not None or self._pipeline_id is not None
        ):
            raise ValueError(
                "Existing reports will be overwritten. Please set overwrite_reports to True to continue"
            )
        # Reset cached data
        self._clear_cache()

        # Check if hardware_parameters is a valid type
        valid_specs = [spec.value for spec in DemoNoiseProfilerSpecs]
        if not isinstance(hardware_parameters, (HardwareParameters, str)):
            raise TypeError(
                f"Invalid hardware_parameters type. Expected HardwareParameters or one of the strings: {', '.join(valid_specs)}."
            )
        # If a string is provided, validate and convert to DemoNoiseProfilerSpecs
        if isinstance(hardware_parameters, str):
            if hardware_parameters not in valid_specs:
                raise ValueError(
                    f"Invalid hardware_parameters string '{hardware_parameters}'. "
                    f"Expected one of: {', '.join(valid_specs)}."
                )
            # Convert string to DemoNoiseProfilerSpecs enum
            hardware_parameters = DemoNoiseProfilerSpecs(hardware_parameters)

        mode = QREMode.LITE if isinstance(circuit, LiteCircuit) else QREMode.FULL

        # Temporary fix to make pipeline run with LiteCircuit
        circuit_name = circuit.circuit_name or f"lite-job-{circuit.num_qubits}-qubits"
        self._logger.info(
            "Starting quantum resource estimation for circuit '%s'...", circuit_name
        )
        if async_mode:
            # Submit request asyncronously
            try:
                response = self._client.run(
                    circuit=circuit,
                    hardware_params=hardware_parameters,
                    global_error_budget=global_error_budget,
                    number_of_repetitions=number_of_repetitions,
                    cost=cost,
                    remove_clifford_gates=remove_clifford_gates,
                    insights_only=insights_only,
                )

                pipeline_id = response.pipeline_id
                self._pipeline_id = pipeline_id
                self._status = StatusEnum.WAITING
                self._mode = mode

                self._logger.info(
                    f"QRE request with pipeline_id {pipeline_id} has been submitted. Please come back later and call get_reports"
                )
            except Exception as e:
                self._logger.error(
                    f"QuantumResourceEstimator failed for circuit '{circuit_name}': {e}"
                )
                raise RuntimeError(
                    f"QuantumResourceEstimator failed for circuit '{circuit_name}'."
                ) from e

            return {"pipeline_id": self._pipeline_id, "status": self._status.value}

        else:
            # Submit request syncronously
            try:
                response = self._client.run_and_get_result(
                    circuit=circuit,
                    hardware_params=hardware_parameters,
                    global_error_budget=global_error_budget,
                    number_of_repetitions=number_of_repetitions,
                    cost=cost,
                    remove_clifford_gates=remove_clifford_gates,
                    insights_only=insights_only,
                )

                pipeline_id = response.pipeline_id
                self._pipeline_id = pipeline_id
                self._status = StatusEnum(response.status)
                self._mode = mode

                summary_view, full_reports = build_report_views(response, mode)

                if download_reports_flag:
                    download_reports(full_reports, reports_output_file)

                # Store reports
                self._reports_download = full_reports
                self._reports = summary_view
            except KeyboardInterrupt:
                raise
            except TopQADTimeoutError as e:
                timeout_message = (
                    f" Please check the portal or call get_reports() to"
                    f" see the status of this job and, upon completion, to obtain"
                    f" your results."
                )
                self._logger.error(timeout_message)
                raise TopQADTimeoutError(f"{e} {timeout_message}")
            except Exception as e:
                self._logger.error(
                    f"QuantumResourceEstimator failed for circuit '{circuit_name}': {e}"
                )
                raise RuntimeError(
                    f"QuantumResourceEstimator failed for circuit '{circuit_name}'."
                ) from e

            self._logger.info(
                f"QuantumResourceEstimator completed for circuit '{circuit_name}'."
            )

            return self._reports

    def load(self, pipeline_id):
        """
        Retrieves and loads pipeline information from server using given `pipeline_id`.
        This will overwrite existing information.

        Args:
            pipeline_id (str): The ID of the QRE pipeline.

        Returns:
            dict: Status and pipeline ID of the request.
        """
        # Reset cached data
        self._clear_cache()

        try:
            response = self._client.get_result(pipeline_id)
        except Exception as e:
            err_msg = f"Failed to load from pipeline_id {self._pipeline_id}"
            self._logger.error(err_msg)
            raise TopQADError(err_msg) from e

        # update information
        self._status = StatusEnum(response.status)
        self._pipeline_id = pipeline_id
        self._mode = determine_mode(response)

        if self._status == StatusEnum.DONE:
            # Populate reports if request is finished
            summary_view, full_reports = build_report_views(response, self._mode)

            # Store reports
            self._reports_download = full_reports
            self._reports = summary_view

        return {"pipeline_id": self._pipeline_id, "status": self._status.value}

    def get_reports(
        self,
        download_reports_flag: bool = False,
        reports_output_file: str | Path = "reports.json",
    ) -> Union[QREOutputs, dict]:
        """
        Retrieve the QRE reports from the request.

        Args:
            download_reports_flag (bool, optional):
                When enabled, saves the reports to the path specified by
                `reports_output_file`. Defaults to False.
            reports_output_file (str | Path, optional):
                Path to the output file for saving downloaded reports.
                Only used if `download_reports_flag` is True. Defaults to "reports.json".

        Returns:
            QREOutputs|dict: The generated reports for the QRE request.
            If `download_reports_flag` is enabled, the reports are also saved locally.
            If the reports have not finished then the current status and pipeline ID of job will be returned.
        """

        # Return reports if it is already populated
        if self._reports:
            self._logger.info(
                f"Existing reports for pipeline ID {self._pipeline_id} found. Returning..."
            )

            if download_reports_flag:
                download_reports(self._reports_download, reports_output_file)

            return self._reports

        elif self._pipeline_id:
            self._logger.info(
                f"Existing pipeline ID {self._pipeline_id} found. Requesting reports from server..."
            )
            # Try to get reports from server if pipeline_id is populated
            try:
                response = self._client.get_result(self._pipeline_id)
            except Exception as e:
                err_msg = f"Failed to get result from pipeline_id {self._pipeline_id}"
                self._logger.error(err_msg)
                raise TopQADError(err_msg) from e

            # update status
            self._status = StatusEnum(response.status)

            if self._status in FINISHED_STATUSES:
                # Populate reports if request is finished
                if response.assembler_reports:
                    summary_view, full_reports = build_report_views(
                        response, self._mode
                    )

                    if download_reports_flag:
                        download_reports(full_reports, reports_output_file)

                    # Store reports
                    self._reports_download = full_reports
                    self._reports = summary_view

                    return self._reports
                else:
                    self._logger.error(
                        f"The request has not been completed due to the status being: {response.status}. Please resubmit another request."
                    )
                    return {
                        "pipeline_id": self._pipeline_id,
                        "status": self._status.value,
                        "message": response.message,
                    }

            else:
                msg = f"Pipeline request with pipeline_id {self._pipeline_id} is still in progress. Please check back later"
                self._logger.info(msg)
                return {"pipeline_id": self._pipeline_id, "status": self._status.value}

        else:
            err_msg = "No QRE request has been made. Please submit a request to obtain reports"
            self._logger.error(err_msg)
            raise ValueError(err_msg)

    def cancel(self) -> dict:
        """
        Cancel a running QRE job.

        This method allows the user to cancel the currently running job associated with this instance
        (i.e., the most recent job submitted).

        Returns:
            dict:
                - pipeline_id (str): The pipeline ID of the request to be cancelled.
                - status (str): The status of the job after the cancel request, with possible values including "cancel_pending" (the cancel request was successful, and the job is being cancelled) or the current status of the job (e.g., "done", "failed", etc.) if the cancel request was declined or the job cannot be cancelled.
                - message (str): Information about the cancellation request.

        Raises:
            TopQADError: If the cancellation fails due to an internal error.
            ValueError: If no pipeline ID is found.
        """
        if self._pipeline_id is None:
            self._logger.info(
                "No existing pipeline_id found to cancel. Please submit a QRE job first."
            )
            raise ValueError("No existing pipeline_id found to cancel.")
        try:
            response = self._client.cancel(self._pipeline_id)
            self._logger.info(
                "Cancel request for pipeline_id %s has been submitted.",
                self._pipeline_id,
            )
            self._reports = None
            self._reports_download = None
            # if cancel is successful, update status.
            # if cancel request is declined, status remains unchanged.
            if response.status == StatusEnum.CANCEL_PENDING:
                self._status = response.status

            return {
                "pipeline_id": self._pipeline_id,
                "status": self._status,
                "message": response.message,
            }
        except Exception as e:
            err_msg = (
                f"Failed to cancel QRE request with pipeline_id {self._pipeline_id}"
            )
            self._logger.error(err_msg)
            raise TopQADError(err_msg) from e
