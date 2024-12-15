from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy.sql import func
from sqlalchemy import select, update, insert

from app.backend.db_depends import get_db
from app.schemas import CreateReview, CreateRating, CreateProduct
from app.models.users import User
from app.models.products import Product
from app.models.reviews import Reviews, Ratings
from app.routers.auth import get_current_user


router = APIRouter(prefix='/reviewies', tags=['review'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Reviews).where(Reviews.is_active == True))

    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are not reviews'
        )
    return reviews.all()


@router.get('/detail/{product_id}')
async def get_product_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    review = await db.scalars(select(Reviews).where(Reviews.is_active == True, Reviews.product_id == product_id))

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no review found'
        )
    return review

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_reviews_and_ratings(db: Annotated[AsyncSession, Depends(get_db)],
                        create_review: CreateReview, create_ratings: CreateRating, product_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        grade = await db.execute(insert(Ratings).values(user_id=get_user.get('id'), product_id=product_id, grade=create_ratings.grade))
        await db.commit()
        grade= await db.execute(select(Ratings).join(User).where(Ratings.is_active == True, Ratings.product_id == product_id, Ratings.user_id == get_user.get('id')))
        await db.execute(insert(Reviews).values(user_id=get_user.get('id'), product_id=product_id, rating=grade.id, comment=create_review.comment))
        await db.commit()
        # считаем средний рейтинг
        avg_grade_product = await db.query(func.avg(Product.rating).label('average')).filter(Product.id==product_id)
        await db.execute(update(Product).where(Product.id == product_id)).values(rating=avg_grade_product)
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have customer permission"
        )


@router.delete('/')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        review = await db.scalar(select(Reviews).where(Reviews.id == review_id))
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no review found'
            )
        await db.execute(update(Reviews).where(Reviews.id == review_id).values(is_active=False))
        await db.commit()
        await db.execute(update(Ratings).where(Ratings.id == review.rating).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method"
        )