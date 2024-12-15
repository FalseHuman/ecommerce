from fastapi import APIRouter, Depends, status, HTTPException
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from app.models.category import Category
from app.models.products import Product
from sqlalchemy import select, update, insert
from app.routers.auth import get_current_user

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True and Product.stock > 0))
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are not product'
        )
    return products.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        category = await db.scalar(select(Category).where(Category.id == create_product.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(insert(Product).values(name=create_product.name,
                                        description=create_product.description,
                                        price=create_product.price,
                                        image_url=create_product.image_url,
                                        stock=create_product.stock,
                                        category_id=create_product.category,
                                        rating=0.0,
                                        slug=slugify(create_product.name),
                                        supplier_id=get_user.get('id')))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method"
        )



@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)],  category_slug: str):
    category = await db.scalars(select(Category).where(Category.slug == category_slug))
    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))
    all_category = [category.id] + [i.id for i in subcategories.all()]

    products = await db.scalars(select(Product).where(Product.category_id.in_(all_category) and Product.is_active == True and Product.stock > 0))
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are not product'
        )
    return products.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalars(select(Product).where(Product.slug== product_slug, Product.is_active == True, Product.stock > 0))
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    return product


@router.put('/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('id') == product_update.supplier_id:
        product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
        if product_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        category = await db.scalar(select(Category).where(Category.id == update_product_model.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(update(Product).where(Product.slug == product_slug)
                .values(name=update_product_model.name,
                        description=update_product_model.description,
                        price=update_product_model.price,
                        image_url=update_product_model.image_url,
                        stock=update_product_model.stock,
                        category_id=update_product_model.category,
                        slug=slugify(update_product_model.name)))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product update is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method"
        )

@router.delete('/')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
        if product_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method"
        )    