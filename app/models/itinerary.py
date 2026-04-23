from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.extensions import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme = Column(String(200))
    duration_days = Column(Integer)
    budget = Column(String(50))
    group_type = Column(String(50))
    result = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
