from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Ratings(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    product_id = Column(Integer, ForeignKey('products.id')) 
    grade = Column(Float)
    is_active = Column(Boolean, default=True)


class Reviews(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    product_id = Column(Integer, ForeignKey('products.id')) 
    rating = Column(Integer, ForeignKey('ratings.id')) 
    comment = Column(String)
    comment_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    users = relationship('User', back_populates='reviews')