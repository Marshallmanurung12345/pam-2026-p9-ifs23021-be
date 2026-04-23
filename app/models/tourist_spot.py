from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.extensions import Base


class TouristSpot(Base):
    __tablename__ = "tourist_spots"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String(500))
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
