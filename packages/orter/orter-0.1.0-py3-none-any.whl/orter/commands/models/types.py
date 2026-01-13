from pydantic import BaseModel, ConfigDict, Field


class Pricing(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str | None = None
    completion: str | None = None


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str | None = None
    description: str | None = None
    context_length: int | None = None
    pricing: Pricing | None = None
    supported_parameters: list[str] | None = None


class ModelsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[ModelInfo] = Field(default_factory=list)
