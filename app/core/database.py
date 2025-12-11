from supabase import create_client, Client
from app.core.config import settings


def get_supabase() -> Client:
    """
    Retorna una instancia global del cliente Supabase.
    Se reutiliza para evitar múltiples conexiones.
    """
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY

    if not url or not key:
        raise ValueError("❌ SUPABASE_URL o SUPABASE_KEY no están configurados.")

    client: Client = create_client(url, key)
    return client


# Cliente global reutilizable
supabase = get_supabase()