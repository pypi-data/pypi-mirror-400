from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

__NAMESPACE__ = (
    "http://www.openapplications.org/oagis/9/IANAMIMEMediaTypes:2003"
)


class BinaryObjectMimeCodeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
