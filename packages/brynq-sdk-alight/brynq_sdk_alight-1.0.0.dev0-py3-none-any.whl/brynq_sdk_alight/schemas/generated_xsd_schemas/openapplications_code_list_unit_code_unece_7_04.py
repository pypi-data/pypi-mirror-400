from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

__NAMESPACE__ = "http://www.openapplications.org/oagis/9/unitcode/66411:2001"


class UnitCodeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
