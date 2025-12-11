from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel
from app.core.database import supabase
from app.core.security import get_current_user
import traceback

# ✅ SIN PREFIX - Se agregará desde main.py
router = APIRouter(tags=["achievements"])

class AchievementUnlock(BaseModel):
    achievement_id: str

class AchievementResponse(BaseModel):
    id: int
    user_id: str
    achievement_id: str
    unlocked_at: str

@router.get("/user/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtiene todos los logros desbloqueados del usuario"""
    try:
        print(f"🔍 get_user_achievements - user_id: {current_user['id']}")
        
        result = supabase.table("user_achievements")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        print(f"✅ Resultado de user_achievements: {result.data}")
        
        return result.data or []
        
    except Exception as e:
        print(f"❌ ERROR en get_user_achievements:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print(f"   Traceback completo:")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener achievements: {str(e)}"
        )

@router.post("/achievements", status_code=status.HTTP_201_CREATED)
async def unlock_achievement(
    achievement: AchievementUnlock,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Desbloquea un logro para el usuario"""
    try:
        print(f"🔍 unlock_achievement - user_id: {current_user['id']}, achievement_id: {achievement.achievement_id}")
        
        # Verificar si ya está desbloqueado
        existing = supabase.table("user_achievements")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .eq("achievement_id", achievement.achievement_id)\
            .execute()
        
        if existing.data:
            print(f"⚠️ Achievement ya desbloqueado")
            return {
                "message": "Achievement already unlocked",
                "achievement_id": achievement.achievement_id
            }
        
        # Desbloquear el achievement
        result = supabase.table("user_achievements").insert({
            "user_id": current_user["id"],
            "achievement_id": achievement.achievement_id
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al desbloquear achievement"
            )
        
        print(f"✅ Achievement desbloqueado exitosamente")
        
        return {
            "message": "Achievement unlocked successfully",
            "achievement_id": achievement.achievement_id,
            "data": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en unlock_achievement:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desbloquear achievement: {str(e)}"
        )

@router.get("/achievements/all")
async def get_all_achievements():
    """Obtiene todos los achievements disponibles"""
    try:
        print(f"🔍 Obteniendo todos los achievements disponibles")
        
        result = supabase.table("achievements")\
            .select("*")\
            .execute()
        
        print(f"✅ Total achievements encontrados: {len(result.data) if result.data else 0}")
        
        return result.data or []
        
    except Exception as e:
        print(f"❌ ERROR en get_all_achievements:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener achievements: {str(e)}"
        )