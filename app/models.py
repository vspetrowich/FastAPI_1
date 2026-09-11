# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float
from database import Base

class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description =  Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String(70), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    def to_dict(self):
        """Вспомогательный метод для преобразования ORM-объекта в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,

        }