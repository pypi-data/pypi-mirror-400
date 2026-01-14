from typing import List, Union, Optional

from pydantic.main import BaseModel


class TokenDetails(BaseModel):
    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None


class EmbeddingData(BaseModel):
    index: int
    embedding: Union[List[float], str]
    object: str


class UsageInfo(BaseModel):
    prompt_tokens: int
    total_cost: float
    total_tokens: int
    currency: str
    prompt_cost: float
    completion_tokens_details: Optional[TokenDetails] = None
    prompt_tokens_details: Optional[TokenDetails] = None


class EmbeddingResponse(BaseModel):
    data: List[EmbeddingData]
    usage: UsageInfo
    model: str
    object: str
