from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserHabit(Base):
    __tablename__ = "user_habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    habit_id = Column(String, nullable=False)  # ID del hábito (ej: "mindfulness", "gratitude")
    completed_at = Column(Date, nullable=False, index=True)
    
    # Relación con el usuario
    user = relationship("User", back_populates="habits")

# En tu modelo User, agrega:
# habits = relationship("UserHabit", back_populates="user")