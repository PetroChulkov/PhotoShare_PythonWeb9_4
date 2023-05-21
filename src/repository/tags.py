from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from src.database.models import Tag


async def create_tags_for_photo(tags: list, db: Session):
    tag_obj = []
    if len(tags) > 5:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Maximum amount of tags is 5"
        )
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
        if not tag:
            tag = Tag(tag_name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_obj.append(tag)
    return tag_obj
