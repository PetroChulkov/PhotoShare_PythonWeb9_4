from pydantic import BaseModel, Field


class PhotoRatingModel(BaseModel):
    photo_id: int
    rating: int = Field(ge=1, le=5)


class PhotoRatingResponseModel(BaseModel):
    photo_id: int
    user_id: int
    rating: int

    class Config:
        orm_mode = True


class AvgPhotoRatingResponse(BaseModel):
    photo_id: int
    avg_rating: float

    class Config:
        orm_mode = True
