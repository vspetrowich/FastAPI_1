# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float
from database import Base

class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description =  Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    author_id = Column(Integer, nullable=False)
    #author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())


    def to_dict(self):
        """Вспомогательный метод для преобразования ORM-объекта в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author_id": self.author_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,

        }