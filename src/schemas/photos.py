from typing import List
from datetime import datetime

from pydantic import BaseModel, Field


class TagModel(BaseModel):
    tag_name: str = Field(max_length=50)


class TagResponse(TagModel):
    id: int

    class Config:
        orm_mode = True


class PhotoModel(BaseModel):
    description: str


class PhotoDb(BaseModel):
    id: int
    photo: str
    description: str | None
    tags: List[TagResponse]
    qr_code: str | None

    class Config:
        orm_mode = True


class PhotoResponse(BaseModel):
    photo: PhotoDb
    detail: str = "Photo was created successfully"


class DescriptionUpdate(BaseModel):
    done: bool


class PhotoSearch(BaseModel):
    id: int
    photo: str
    qr_code: str | None
    description: str | None
    created_at: datetime
    tags: List[TagResponse]
    average_rating: float

    class Config:
        orm_mode = True
