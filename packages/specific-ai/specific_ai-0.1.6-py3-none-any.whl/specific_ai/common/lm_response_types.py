from typing import List, Optional
from pydantic import BaseModel, Field


class LMResponse(BaseModel):
    is_validated: bool = Field(default=False)


class ClassificationResponse(LMResponse):
    labels: List[str]
    extra_params: dict = Field(default={})

class EntityRecognitionResponse(LMResponse):
    class Entity(BaseModel):
        label: Optional[str] = None
        content: Optional[str] = None
        start_index: Optional[int] = None
        is_validated: bool = Field(default=False)

    class Relation(BaseModel):
        label: str
        source_start_index: int
        target_start_index: int
        is_validated: bool = Field(default=False)

    entities: list[Entity]
    relations: list[Relation] = Field(default_factory=list)
    extra_params: dict = Field(default={})


AnyLMResponse = ClassificationResponse | EntityRecognitionResponse
