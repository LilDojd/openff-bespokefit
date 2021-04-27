import abc
from typing import Any, Dict, Optional, Union

from openff.qcsubmit.results import (
    BasicResultCollection,
    OptimizationResultCollection,
    TorsionDriveResultCollection,
)
from pydantic import Field, PositiveFloat, validator
from typing_extensions import Literal

from openff.bespokefit.schema.data import BespokeQCData
from openff.bespokefit.utilities.pydantic import SchemaBase


class BaseTargetSchema(SchemaBase, abc.ABC):
    """The base class for models which store information about fitting targets."""

    weight: PositiveFloat = Field(
        1.0, description="The amount to weight the target by."
    )

    reference_data: Optional[Union[Any, BespokeQCData]]

    extras: Dict[str, str] = Field(
        {},
        description="Extra settings to use for the target. Optimizer specific settings "
        "(e.g. whether a target should be set to remote in ForceBalance) should be "
        "included here.",
    )

    @classmethod
    @abc.abstractmethod
    def bespoke_task_type(
        cls,
    ) -> Literal["torsion1d", "optimization", "hessian"]:
        """Returns the type of task which will be required to generate the reference
        data for this type of target.
        """
        raise NotImplementedError

    @validator("reference_data")
    def _check_reference_data(cls, value):

        if not isinstance(value, BespokeQCData):
            return value

        assert all(
            task.task_type == cls.bespoke_task_type() for task in value.tasks
        ), f"all tasks must be of {cls.bespoke_task_type()} type"

        return value


class TorsionProfileTargetSchema(BaseTargetSchema):
    """A model which stores information about a torsion profile fitting target."""

    type: Literal["TorsionProfile"] = "TorsionProfile"

    reference_data: Optional[
        Union[TorsionDriveResultCollection, BespokeQCData]
    ] = Field(
        None,
        description="The reference QC data (either existing or to be generated on the "
        "fly) to fit against.",
    )

    attenuate_weights: bool = Field(
        True, description="Whether to attenuate the weights as a function of energy."
    )

    energy_denominator: float = Field(
        1.0, description="The energy denominator in objective function contribution."
    )
    energy_cutoff: float = Field(10.0, description="The upper energy cutoff.")

    @classmethod
    def bespoke_task_type(cls) -> Literal["torsion1d"]:
        return "torsion1d"


class AbInitioTargetSchema(BaseTargetSchema):
    """A model which stores information about an ab initio fitting target."""

    type: Literal["AbInitio"] = "AbInitio"

    reference_data: Optional[
        Union[TorsionDriveResultCollection, BespokeQCData]
    ] = Field(
        None,
        description="The reference QC data (either existing or to be generated on the "
        "fly) to fit against.",
    )

    attenuate_weights: bool = Field(
        False, description="Whether to attenuate the weights as a function of energy."
    )

    energy_denominator: float = Field(
        1.0, description="The energy denominator in objective function contribution."
    )
    energy_cutoff: float = Field(10.0, description="The upper energy cutoff.")

    fit_energy: bool = Field(True, description="Whether to fit to the energy.")
    fit_force: bool = Field(False, description="Whether to fit to the force.")

    @classmethod
    def bespoke_task_type(cls) -> Literal["torsion1d"]:
        return "torsion1d"


class VibrationTargetSchema(BaseTargetSchema):
    """A model which stores information about a vibration fitting target."""

    type: Literal["Vibration"] = "Vibration"

    reference_data: Optional[Union[BasicResultCollection, BespokeQCData]] = Field(
        None,
        description="The reference QC data (either existing or to be generated on the "
        "fly) to fit against.",
    )

    mode_reassignment: Optional[Literal["permute", "overlap"]] = Field(
        None, description="The (optional) method by which to re-assign normal modes."
    )

    @classmethod
    def bespoke_task_type(cls) -> Literal["hessian"]:
        return "hessian"


class OptGeoTargetSchema(BaseTargetSchema):
    """A model which stores information about an optimized geometry fitting target."""

    type: Literal["OptGeo"] = "OptGeo"

    reference_data: Optional[
        Union[OptimizationResultCollection, BespokeQCData]
    ] = Field(
        None,
        description="The reference QC data (either existing or to be generated on the "
        "fly) to fit against.",
    )

    bond_denominator: float = Field(
        0.05,
        description="The denominator to scale the contributions of bonds to the "
        "objective function by.",
    )
    angle_denominator: float = Field(
        8.0,
        description="The denominator to scale the contributions of angles to the "
        "objective function by.",
    )
    dihedral_denominator: float = Field(
        0.0,
        description="The denominator to scale the contributions of dihedrals to the "
        "objective function by.",
    )
    improper_denominator: float = Field(
        20.0,
        description="The denominator to scale the contributions of impropers to the "
        "objective function by.",
    )

    @classmethod
    def bespoke_task_type(cls) -> Literal["optimization"]:
        return "optimization"


TargetSchema = Union[
    TorsionProfileTargetSchema,
    AbInitioTargetSchema,
    VibrationTargetSchema,
    OptGeoTargetSchema,
]
