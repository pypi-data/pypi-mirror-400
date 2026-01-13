from pydantic import BaseModel
from pydantic.config import ConfigDict


class FromAttributesBase(BaseModel):
    model_config: ConfigDict = {"from_attributes": True}
