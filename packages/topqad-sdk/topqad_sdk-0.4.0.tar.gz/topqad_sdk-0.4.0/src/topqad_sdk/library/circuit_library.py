import logging
import os
import configparser
from pathlib import Path
from urllib.parse import urlparse

from topqad_sdk._http_request import HTTPClient
from topqad_sdk._exceptions import TopQADError, TopQADValueError
from topqad_sdk.models import (
    Circuit,
    UploadCircuitResponse,
    RetrieveCircuitByIdResponse,
    RetrieveCircuitResponse,
)

DEFAULT_CIRCUIT_LIBRARY_URL = "https://pipeline.portal.topqad.1qbit-dev.com"


class CircuitLibrary:
    """Base class for managing circuits in the TopQAD pipeline.

    Provides methods to access example circuits, retrieve and list circuits
    for persistent reuse and lookup.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Initializes the CircuitLibrary instance."""
        service_url = os.environ.get("TOPQAD_DOMAIN_URL", DEFAULT_CIRCUIT_LIBRARY_URL)
        self._client = HTTPClient(service_url=service_url)
        self._logger.debug(f"Initializing CircuitLibrary with URL={service_url}")
        self._example_circuits = []
        self._uploaded_circuits = []

    def _set_service_url(self, url: str):
        """Set the URL for the CircuitLibrary.

        Args:
            url (str): The new URL.

        Raises:
            TopQADValueError: If the provided URL is invalid.
        """
        self._client._set_service_url(url)

    def upload(
        self, file_path: str, name: str = None, description: str = None
    ) -> UploadCircuitResponse:
        """Uploads a circuit file.

        Args:
            file_path (str): Path to the .qasm file.
                The filename must only contain alpha-numeric characters, underscores (_), dashes (-), and periods (.).
                Other characters in the filename are not allowed.
            name (str, optional): Name of the circuit.
                Defaults to the file name without extension.
            description (str, optional): Description of the circuit.

        Returns:
            UploadCircuitResponse: The response containing the uploaded circuit's details.

        Raises:
            TopQADError: If the upload fails or no ID is returned.
        """
        try:
            if name is None:
                name = os.path.splitext(os.path.basename(urlparse(file_path).path))[0]
            if description is None:
                description = "Circuit uploaded from TopQAD SDK."
            with open(file_path, "rb") as f:
                file = {"file": (file_path, f, "application/octet-stream")}
                payload = {
                    "name": name,
                    "description": description,
                }
                self._logger.info(f"Uploading circuit from file: {file_path}")
                response = self._client._request(
                    "post", "/circuit_library/upload", files=file, data=payload
                )
            self._logger.info("Circuit uploaded successfully.")
            validated_response = UploadCircuitResponse.model_validate(response)
            uploaded_circuit = Circuit(
                id=validated_response.circuit_id,
                circuit_name=validated_response.circuit_name,
                status=validated_response.status,
                client=self,
            )
            self._uploaded_circuits.append(uploaded_circuit)
            return validated_response
        except Exception as e:
            self._logger.error(f"Failed to upload circuit from {file_path}.")
            raise TopQADError(
                f"Failed to upload circuit from {file_path}. \n{e}"
            ) from e

    def get_uploaded_by_id(self, circuit_id: str) -> Circuit:
        """Retrieves a uploaded circuit by its ID.

        Args:
            circuit_id (str): The ID of the circuit.

        Returns:
            Circuit: The response containing circuit details.

        Raises:
            TopQADError: If the retrieval fails.
        """
        self._logger.info(f"Retrieving circuit with ID: {circuit_id}")
        if not circuit_id:
            raise TopQADValueError("Circuit ID must be provided.")
        try:
            response = self._client._request(
                "get", f"/circuit_library/uploads/{circuit_id}"
            )
            self._logger.debug(f"Received response: {response}")
            retrieved_response = RetrieveCircuitByIdResponse.model_validate(response)
            circuit_info = retrieved_response.circuit
            circuit = Circuit(
                id=circuit_info.id,
                status=retrieved_response.status,
                circuit_name=circuit_info.circuit_name,
                client=self,
            )
            circuit._circuit_path = getattr(circuit_info, "circuit_path", "")
            self._logger.info(f"Circuit with ID {circuit_id} retrieved successfully.")
            return circuit
        except Exception as e:
            self._logger.error(f"Failed to retrieve circuit by ID {circuit_id}.")
            raise TopQADError(
                f"Failed to retrieve circuit by ID {circuit_id}. \n{e}"
                f"Check 'uploaded_circuits' to see your uploaded circuits."
            ) from e

    def get_uploaded_by_name(self, circuit_name: str) -> Circuit:
        """Retrieve uploaded circuit by its name.

        Args:
            circuit_name (str): The name of the circuit.

        Returns:
            Circuit: The response containing circuit details.

        Raises:
            ValueError: If no circuit with the given name is found.

        """
        uploaded_circuits = (
            self.uploaded_circuits
        )  # ensure list is initialized via property

        for circuit in uploaded_circuits:
            if circuit.circuit_name == circuit_name:
                return circuit

        raise TopQADValueError(
            f"Circuit with name '{circuit_name}' not found. "
            f"Check 'uploaded_circuits' to see your uploaded circuits."
        )

    def list_all_uploads(self) -> list:
        """Fetches and updates the list of all uploaded circuits.

        Returns:
            list: A list of uploaded circuits.

        Raises:
            TopQADError: If the request to list circuits fails.
        """
        self._logger.info("Listing all uploaded circuits.")
        try:
            response = self._client._request("get", "/circuit_library/uploads")
            self._logger.debug(f"Received response: {response}")
            validated_response = RetrieveCircuitResponse.model_validate(response)
            circuits = getattr(validated_response, "circuits", [])
            if not circuits:
                self._logger.warning("No uploaded circuits found.")
                self._uploaded_circuits = []
                return []
            circuit_objs = [
                Circuit(
                    id=circuit.id,
                    circuit_name=circuit.circuit_name,
                    status=validated_response.status,
                    client=self,
                )
                for circuit in circuits
            ]
            self._uploaded_circuits = circuit_objs
            self._logger.info("Uploaded circuits listed successfully.")
            return circuits
        except Exception as e:
            self._logger.error("Failed to list circuits.")
            raise TopQADError(f"Failed to list circuits. \n{e}") from e

    def get_example_by_id(self, circuit_id: str) -> Circuit:
        """Retrieves an example circuit by its ID.

        Args:
            circuit_id (str): The ID of the circuit.

        Returns:
            Circuit: The response containing circuit details.

        Raises:
            TopQADError: If the retrieval fails.
        """
        self._logger.info(f"Retrieving circuit with ID: {circuit_id}")
        if not circuit_id:
            raise TopQADValueError("Circuit ID must be provided.")
        try:
            response = self._client._request(
                "get", f"/circuit_library/example/{circuit_id}"
            )
            self._logger.debug(f"Received response: {response}")
            retrieved_response = RetrieveCircuitByIdResponse.model_validate(response)
            circuit_info = retrieved_response.circuit
            circuit = Circuit(
                id=circuit_info.id,
                status=retrieved_response.status,
                circuit_name=circuit_info.circuit_name,
                client=self,
            )
            circuit._circuit_path = getattr(circuit_info, "circuit_path", "")
            self._logger.info(f"Circuit with ID {circuit_id} retrieved successfully.")
            return circuit
        except Exception as e:
            self._logger.error(f"Failed to retrieve circuit by ID {circuit_id}.")
            raise TopQADError(
                f"Failed to retrieve circuit by ID {circuit_id}. \n{e}"
            ) from e

    def list_all_examples(self) -> list:
        """Fetches and updates the list of all available example circuits.

        Returns:
            list: A list of example circuits.

        Raises:
            TopQADError: If the request to list examples fails.
        """
        self._logger.info("Listing all example circuits.")
        try:
            response = self._client._request("get", "/circuit_library/examples")
            self._logger.debug(f"Received response: {response}")
            validated_response = RetrieveCircuitResponse.model_validate(response)
            circuits = getattr(validated_response, "circuits", [])
            if not circuits:
                self._logger.warning("No example circuits found.")
                self._example_circuits = []
                return []
            circuit_objs = [
                Circuit(
                    id=circuit.id,
                    circuit_name=circuit.circuit_name,
                    status=validated_response.status,
                    client=self,
                )
                for circuit in circuits
            ]
            self._example_circuits = circuit_objs
            self._logger.info("Example circuits listed successfully.")
            return circuits
        except Exception as e:
            self._logger.error("Failed to list example circuits.")
            raise TopQADError(f"Failed to list example circuits. \n{e}") from e

    def get_example_by_name(self, circuit_name: str) -> Circuit:
        """Retrieve example circuit by its name.

        Args:
            circuit_name (str): The name of the circuit.

        Returns:
            Circuit: The response containing circuit details.

        Raises:
            ValueError: If no circuit with the given name is found.

        """
        example_circuits = (
            self.example_circuits
        )  # ensure list is initialized via property

        for circuit in example_circuits:
            if circuit.circuit_name == circuit_name:
                return circuit

        raise TopQADValueError(f"Circuit with name '{circuit_name}' not found.")

    @property
    def uploaded_circuits(self) -> list[Circuit]:
        """Returns a list of uploaded circuits.

        Returns:
            list[Circuit]: A list of uploaded circuits.
        """
        if not self._uploaded_circuits:
            self.list_all_uploads()
        return self._uploaded_circuits

    @property
    def example_circuits(self) -> list[Circuit]:
        """Returns a list of example circuits.

        Returns:
            list[Circuit]: A list of example circuits.
        """
        if not self._example_circuits:
            self.list_all_examples()
        return self._example_circuits
