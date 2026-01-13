import logging


class Circuit:
    """Represents a quantum circuit."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        id: str,
        status: str,
        circuit_name: str,
        client=None,
    ):
        """Initialize Circuit.

        Args:
            id (str): Circuit ID.
            status (str): Status of the circuit.
            circuit_name (str): Name of the circuit.
            client (CircuitLibrary, optional): Client to fetch circuit details.
                Defaults to None.
        """
        self.id = id
        self.circuit_name = circuit_name
        self.status = status
        self._client = client  # Pass CircuitLibrary instance here
        self._circuit_path = None

    def __repr__(self):
        return f"Circuit(id={self.id}, status={self.status}, circuit_name={self.circuit_name})"

    @property
    def circuit_path(self) -> str:
        """Fetch and return the circuit_path for this circuit.

        Returns:
            str: The circuit file path.

        Raises:
            TopQADError: If the circuit cannot be retrieved.
        """
        if not self._client:
            self._logger.error("No client set for Circuit object.")
            raise RuntimeError(
                "Unable to retrieve circuit path: no client set for Circuit object."
            )
        self._logger.info(f"Fetching circuit path for circuit ID: {self.id}")
        circuit = self._client.get_example_by_id(self.id)
        self._circuit_path = getattr(circuit, "_circuit_path", "")
        return self._circuit_path or ""

    @property
    def as_dict(self) -> dict:
        """Return a dictionary representation of the Circuit object.

        Returns:
            dict: Dictionary with circuit fields.
        """
        return {
            "id": self.id,
            "status": self.status,
            "circuit_name": self.circuit_name,
        }


class LiteCircuit:
    """A lite circuit class.

    The LiteCircuit class provides a basic structure for representing quantum circuits
    with only two parameters for just resource estimation.

    Args:
        num_qubits (int): The number of qubits in the circuit. Must be between 1 and 1,000,000,000.
        num_operations (int): The number of operations in the circuit. Must be between 1 and 1e20.

    Raises:
        ValueError: If num_qubits or num_operations are not within their valid ranges or are not integers.

    Attributes:
        num_qubits (int): The number of qubits in the circuit.
        num_operations (int): The number of operations in the circuit.
    """

    def __init__(
        self,
        num_qubits: int,
        num_operations: int,
        circuit_name: str = None,
    ):
        if not isinstance(num_qubits, int) or not (0 < num_qubits < 1e9):
            raise ValueError(
                f"num_qubits: {num_qubits} must be an integer between 1 and 1,000,000,000."
            )
        if not isinstance(num_operations, int) and not (0 < num_operations < 1e20):
            raise ValueError(
                f"num_operations:{num_operations} must be an integer between 1 and 1e20."
            )
        self.circuit_name = circuit_name
        self.num_qubits = num_qubits
        self.num_operations = num_operations
