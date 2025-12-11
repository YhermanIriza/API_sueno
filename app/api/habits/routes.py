from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel
from app.core.database import supabase
from app.core.security import get_current_user

# ✅ CAMBIADO: Quitamos /api del prefix
router = APIRouter(prefix="/habits", tags=["habits"])

# Modelos Pydantic
class HabitCreate(BaseModel):
    habit_id: str

class HabitResponse(BaseModel):
    id: int
    user_id: str
    habit_id: str
    completed_at: str
    date: str

@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit: HabitCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Marca un hábito como completado para hoy"""
    try:
        today = date.today().isoformat()
        
        # Verificar si ya existe el hábito para hoy
        existing = supabase.table("habits_history")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .eq("habit_id", habit.habit_id)\
            .eq("date", today)\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este hábito ya fue completado hoy"
            )
        
        # Crear el nuevo hábito
        result = supabase.table("habits_history").insert({
            "user_id": current_user["id"],
            "habit_id": habit.habit_id,
            "date": today,
            "completed_at": datetime.utcnow().isoformat()
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al guardar el hábito"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el hábito: {str(e)}"
        )

@router.get("/today", response_model=List[HabitResponse])
async def get_today_habits(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtiene los hábitos completados hoy"""
    try:
        today = date.today().isoformat()
        
        result = supabase.table("habits_history")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .eq("date", today)\
            .execute()
        
        return result.data or []
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los hábitos: {str(e)}"
        )

@router.delete("/{habit_id}", status_code=status.HTTP_200_OK)
async def delete_habit(
    habit_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Desmarca un hábito completado hoy"""
    try:
        today = date.today().isoformat()
        
        # Buscar el hábito
        result = supabase.table("habits_history")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .eq("habit_id", habit_id)\
            .eq("date", today)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado para hoy"
            )
        
        # Eliminar el hábito
        habit_record_id = result.data[0]["id"]
        supabase.table("habits_history")\
            .delete()\
            .eq("id", habit_record_id)\
            .execute()
        
        return {
            "message": "Hábito eliminado correctamente",
            "habit_id": habit_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el hábito: {str(e)}"
        )

@router.get("/stats")
async def get_habit_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtiene estadísticas de hábitos del usuario desde user_stats"""
    try:
        print(f"🔍 get_habit_stats - current_user: {current_user}")
        print(f"🔍 get_habit_stats - user_id: {current_user['id']} (tipo: {type(current_user['id'])})")
        
        # Obtener stats de la tabla user_stats
        print(f"🔍 Buscando en user_stats con user_id: {current_user['id']}")
        stats_result = supabase.table("user_stats")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        print(f"🔍 Resultado de user_stats: {stats_result.data}")
        
        if stats_result.data and len(stats_result.data) > 0:
            stats = stats_result.data[0]
            return {
                "total_habits_completed": stats.get("total_habits_completed", 0),
                "today_habits_completed": 0,
                "current_streak": stats.get("current_streak", 0),
                "longest_streak": stats.get("longest_streak", 0),
                "average_sleep_hours": float(stats.get("average_sleep_hours", 0))
            }
        
        # Si no existe registro en user_stats, calcular manualmente
        today = date.today().isoformat()
        
        print(f"🔍 No hay stats, calculando manualmente para user_id: {current_user['id']}")
        
        # Total de hábitos completados
        all_habits = supabase.table("habits_history")\
            .select("*", count="exact")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        total_habits = all_habits.count if hasattr(all_habits, 'count') else len(all_habits.data or [])
        
        # Hábitos completados hoy
        today_habits = supabase.table("habits_history")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .eq("date", today)\
            .execute()
        
        today_count = len(today_habits.data or [])
        
        # Calcular racha actual
        current_streak = 0
        check_date = date.today()
        
        for _ in range(365):
            check_date_str = check_date.isoformat()
            
            habits_on_date = supabase.table("habits_history")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("date", check_date_str)\
                .execute()
            
            if habits_on_date.data and len(habits_on_date.data) > 0:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        return {
            "total_habits_completed": total_habits,
            "today_habits_completed": today_count,
            "current_streak": current_streak,
            "longest_streak": 0,
            "average_sleep_hours": 0
        }
        
    except Exception as e:
        print(f"❌ ERROR COMPLETO en get_habit_stats: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.get("/history")
async def get_habit_history(
    days: int = 7,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtiene el historial de hábitos de los últimos N días"""
    try:
        start_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("habits_history")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .gte("date", start_date)\
            .order("date", desc=True)\
            .execute()
        
        return result.data or []
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el historial: {str(e)}"
        )