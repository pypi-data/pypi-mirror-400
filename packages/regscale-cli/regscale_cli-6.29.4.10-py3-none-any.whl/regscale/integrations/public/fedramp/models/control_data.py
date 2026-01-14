"""
Pydantic models for FedRAMP control data.

These models provide type-safe data structures for parsed control
implementation data from FedRAMP SSP and Appendix A documents.

Following SOLID principles:
- Single Responsibility: Each model represents one concept
- Open/Closed: Models can be extended without modification
- Liskov Substitution: Models inherit properly from BaseModel
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ControlPart(BaseModel):
    """
    Represents a single control implementation part (Part a, Part b, etc.).

    FedRAMP controls are often broken into multiple parts, each with
    its own implementation statement and responsibility assignments.
    """

    name: str = Field(..., description="Part identifier like 'Part a', 'Part b'")
    value: str = Field(..., description="Implementation statement content for this part")
    customer_responsibility: Optional[str] = Field(
        default=None, description="Customer/agency responsibility for this part"
    )
    cloud_responsibility: Optional[str] = Field(
        default=None, description="Cloud service provider responsibility for this part"
    )


class ControlParameter(BaseModel):
    """
    Represents a control parameter assignment.

    FedRAMP controls often have assignable parameters (e.g., frequency,
    number of days) that must be specified in the implementation.
    """

    name: str = Field(..., description="Parameter name like 'AC-1(a)', 'AC-1_prm_1'")
    value: str = Field(..., description="Assigned parameter value")


class ParsedControl(BaseModel):
    """
    Represents a fully parsed control implementation.

    This is the primary data structure returned by FedRAMP document parsers,
    containing all extracted information about a control's implementation.
    """

    control_id: str = Field(..., description="Control identifier like 'AC-1', 'AC-2(1)'")
    status: Optional[str] = Field(default=None, description="Implementation status (e.g., 'Implemented', 'Planned')")
    origination: Optional[str] = Field(
        default=None, description="Control origination (e.g., 'Service Provider Corporate')"
    )
    statement: Optional[str] = Field(default=None, description="Overall implementation statement")
    parts: List[ControlPart] = Field(default_factory=list, description="List of control parts (Part a, b, c, etc.)")
    parameters: List[ControlParameter] = Field(default_factory=list, description="List of parameter assignments")
    responsibility: Optional[str] = Field(default=None, description="Primary responsibility assignment")
    planned_implementation_date: Optional[str] = Field(
        default=None, description="Target date for planned implementations"
    )
    exclusion_justification: Optional[str] = Field(
        default=None, description="Justification for N/A or excluded controls"
    )
    alternative_implementation: Optional[str] = Field(
        default=None, description="Description of alternative/compensating controls"
    )

    # Pydantic V2 model configuration
    model_config = ConfigDict(populate_by_name=True)
