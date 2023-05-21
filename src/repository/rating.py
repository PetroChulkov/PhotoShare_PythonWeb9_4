from sqlalchemy.orm import Session

from src.database.models import PhotoRating, Photo, User
from src.schemas import PhotoRatingModel
from src.repository import photos as repository_photos


async def create_rating(photo: Photo, body: PhotoRatingModel, user: User, db: Session):
    rating = PhotoRating(**body.dict(), user=user)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    photo = await update_avg_photo_rating(photo, db)
    photo.rated_by = photo.rated_by + [user.id]
    db.commit()


async def update_avg_photo_rating(photo: Photo, db: Session):
    total_ratings = len(photo.ratings)
    total_rating_sum = sum([r.rating for r in photo.ratings])
    avg_rating = total_rating_sum / total_ratings if total_ratings > 0 else 0.0
    photo.average_rating = avg_rating
    db.commit()
    return photo


async def get_rating_by_id(rating_id: int, db: Session):
    rating = db.query(PhotoRating).filter_by(id=rating_id).first()
    return rating


async def remove_rating(rating_id: int, db: Session):
    rating = await get_rating_by_id(rating_id, db)
    if rating:
        photo = await repository_photos.get_photo(photo_id=rating.photo_id, db=db)
        db.delete(rating)
        db.commit()
        await update_avg_photo_rating(photo, db)
    return rating


async def get_rating(limit: int, offset: int, db: Session):
    ratings = db.query(PhotoRating).limit(limit).offset(offset).all()
    print(ratings)
    return ratings
