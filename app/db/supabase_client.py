from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """
    Crea y retorna un cliente global de Supabase.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY

    if not url or not key:
        raise ValueError("❌ No se encontró SUPABASE_URL o SUPABASE_KEY en el .env")

    return create_client(url, key)

supabase = get_supabase_client()
