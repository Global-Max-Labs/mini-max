import typing as t
from pydantic import BaseModel, Field
from apps.nlp_router.src.models.base import MultiEmbeddings


class Text(BaseModel):
    id: t.Optional[str] = Field(..., alias="text_id")
    data_collection_id: str
    content: str
    annotations: t.Optional[str]
    metadata: t.Optional[str]

    class Config:
        allow_population_by_field_name = True


class DBText(BaseModel):
    id: t.Optional[str] = Field(..., alias="text_id")
    data_collection_id: str
    content: str

    class Config:
        allow_population_by_field_name = True


class QuestionAnswer(BaseModel):
    answer: t.Optional[str]


class TextUseCases(BaseModel):
    chatbot: t.Optional[QuestionAnswer]


class TextMetaData(BaseModel):
    classes: t.Optional[dict]
    spaces: t.Optional[dict]
    use_cases: t.Optional[TextUseCases]


class TextRequest(BaseModel):
    text_id: t.Optional[str]
    user_id: str
    data_collection_id: str
    content: str
    space: t.Optional[str] = "chatbot"
    model_name: t.Optional[str] = "use"
    annotations: t.Optional[dict]
    metadata: t.Optional[dict]
    cache: t.Optional[bool]


class TextSearchRequest(BaseModel):
    user_id: t.Optional[str]
    space: str
    content: str


class TextEmbeddings(MultiEmbeddings):
    data_type: str = "text"
    space: str = "chatbot"
    model_name: str = "use"
