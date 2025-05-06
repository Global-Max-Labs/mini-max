import typing as t
from pydantic import BaseModel, Field


class MultiEmbeddings(BaseModel):
    data_ids: t.Optional[list]
    data_type: str
    space: str
    model_name: str
    embeddings: t.Optional[list]
