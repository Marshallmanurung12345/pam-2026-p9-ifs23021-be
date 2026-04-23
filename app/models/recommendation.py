from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.extensions import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interest = Column(String(200))
    result = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
