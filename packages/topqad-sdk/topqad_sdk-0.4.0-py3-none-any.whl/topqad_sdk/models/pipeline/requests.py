from enum import Enum
from typing import Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from ..noise_profiler.requests import FTQCRequest


class DemoNoiseProfilerSpecs(str, Enum):
    """Noise Profiler specifications for demo."""

    BASE = "baseline"
    DESIRED = "desired"
    TARGET = "target"


class Fit(BaseModel):
    """Fit model."""

    functional_form: Optional[str] = Field(description="Functional form.")
    fitting_parameters: Optional[Dict[str, float]] = Field(
        description="Fitting Parameters."
    )


class NoiseProfilerAdjustmentsParameters(BaseModel):
    """Parameters to adjust Noise profile."""

    ler: Optional[Fit] = Field(description="The ler")
    reaction_time: Optional[Fit] = Field(description="The reaction time")


class NoiseProfilerAdjustments(BaseModel):
    """Noise Profiler adjustments for demo specs."""

    memory: Optional[NoiseProfilerAdjustmentsParameters] = Field(
        default=None, description="Memory"
    )
    lattice_surgery: Optional[NoiseProfilerAdjustmentsParameters] = Field(
        default=None, description="Lattice surgery"
    )
    magic_state_preparation_unit: Optional[NoiseProfilerAdjustmentsParameters] = Field(
        default=None, description="Magic state preparation"
    )


class SimplifiedCircuit(BaseModel):
    num_qubits: int = Field(description="The number of qubits")
    num_operations: int = Field(description="The number of operations")


class PipelineRequest(BaseModel):
    """Pipeline request model."""

    circuit_path: Optional[str] = Field(
        default=None,
        description=(
            "Deprecated — use `circuit_id` instead.\n"
            "The file path of the circuit to be compiled; the contents of the file "
            "should be in OpenQASM 2.0 format.\n"
        ),
        deprecated=True,
    )
    circuit_id: Optional[str] = Field(
        default=None, description=("The unique identifier of the circuit.")
    )
    simplified_circuit: Optional[SimplifiedCircuit] = Field(
        default=None,
        description=(
            "Alternatively to a circuit id, a simplified circuit dict may be passed containing just "
            "the num_qubits and num_operations."
        ),
    )
    start_step: str = Field(
        description="Starting step of the circuit", default="decomposer"
    )
    global_error_budget: float = Field(
        description="Global error budget (must be > 0 and < 1)",
        gt=0.0,
        lt=1.0,
    )
    timeout: str = Field(description="Timeout.", default="0")
    number_of_repetitions: int = Field(description="Number of repetitions", default=1)
    cost: float = Field(
        default=0,
        description="The price to execute the circuit per qubit for some unit of time.",
    )
    bypass_optimization: Optional[bool] = Field(
        description="When true, optimization is not performed, "
        "only the basis conversion will occur",
        default=False,
    )
    generate_schedule: Optional[bool] = Field(
        description="When true, generates the schedule file "
        "and returns the path to this file in the output",
        default=False,
    )
    ftqc_params: Union[FTQCRequest, DemoNoiseProfilerSpecs] = Field(
        description="The FTQC parameters, which can either be a full request object "
        "or a demo spec enum."
    )
    ftqc_params_adjustments: Optional[NoiseProfilerAdjustments] = Field(
        description="Optional modifications to the demo noise profiler specifications",
        default=None,
    )
    name: Optional[str] = Field(
        description="Name of the pipeline request", default=None
    )
    description: Optional[str] = Field(
        description="Description of the pipeline request", default=None
    )

    @model_validator(mode="after")
    def check_exactly_one_circuit_field(self):
        """Ensure exactly one of circuit_id, circuit_path, or simplified_circuit is provided."""
        provided_fields = [
            bool(self.circuit_id),
            bool(self.circuit_path),
            bool(self.simplified_circuit),
        ]
        if sum(provided_fields) != 1:
            raise ValueError(
                "You must provide exactly one of `circuit_id` or `simplified_circuit`."
            )
        return self

    @field_validator("timeout")
    def timeout_must_be_numeric(cls, v):
        """Validate that timeout is a numeric string."""
        try:
            float(v)
            return v
        except (ValueError, TypeError):
            raise ValueError("timeout must be a numeric string")

    @model_validator(mode="after")
    def check_adjustments_with_demo_spec(self):
        """Check adjustments with demo spec."""
        ftqc_params = self.ftqc_params
        adjustments = self.ftqc_params_adjustments

        if adjustments is not None and not isinstance(
            ftqc_params, DemoNoiseProfilerSpecs
        ):
            raise ValueError(
                "ftqc_params_adjustments can only be used "
                "when ftqc_params is a DemoNoiseProfilerSpecs value."
            )
        return self
