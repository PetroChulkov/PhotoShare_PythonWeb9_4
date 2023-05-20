from sqlalchemy.orm import Session

from src.database.models import PhotoRating, Photo, User
from src.schemas import PhotoRatingModel


async def create_rating(photo: Photo, body: PhotoRatingModel, user: User, db: Session):
    rating = PhotoRating(**body.dict(), user=user)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    photo.rated_by.append(user.id)
    total_ratings = len(photo.ratings)
    total_rating_sum = sum([r.rating for r in photo.ratings])
    avg_rating = total_rating_sum / total_ratings if total_ratings > 0 else 0.0
    photo.average_rating = avg_rating
    db.commit()


async def get_rating_by_id(rating_id: int, db: Session):
    rating = db.query(PhotoRating).filter_by(id=rating_id).first()
    return rating


async def remove_rating(rating_id: int, db: Session):
    rating = await get_rating_by_id(rating_id, db)
    if rating:
        db.delete(rating)
        db.commit()
    return rating


async def get_rating(limit: int, offset: int, db: Session):
    ratings = db.query(PhotoRating).limit(limit).offset(offset).all()
    return ratings
