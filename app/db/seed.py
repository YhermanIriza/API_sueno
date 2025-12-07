from app.db.supabase_client import supabase
from app.api.services import hash_password


def seed_roles():
    """
    Crea los roles básicos si no existen.
    """
    roles = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "usuario"}
    ]
    
    for role_data in roles:
        existing, count = supabase.table("roles").select("id", count='exact').eq("name", role_data["name"]).execute()
        
        if count == 0:
            supabase.table("roles").insert(role_data).execute()
            print(f"✔ Rol '{role_data['name']}' creado")
        else:
            print(f"✔ Rol '{role_data['name']}' ya existe")


def seed_admin_user():
    """
    Crea un usuario administrador de demostración.
    """
    email = "admin@demo.com"
    
    # Verificar si existe
    existing, count = supabase.table("users").select("id", count='exact').eq("email", email).execute()

    if count > 0:
        print(f"✔ Usuario {email} ya existe")
        return

    # Crear usuario admin
    data = {
        "email": email,
        "hashed_password": hash_password("admin123"),
        "full_name": "Administrador Demo",
        "role_id": 1,  # admin
        "is_active": True,
        "is_verified": True
    }

    supabase.table("users").insert(data).execute()
    print(f"🚀 Usuario admin creado: {email} / admin123")


def seed_test_users():
    """
    Crea usuarios para testing/pruebas.
    """
    test_users = [
        {
            "email": "admin@test.com",
            "password": "admin123",
            "full_name": "Admin Test",
            "role_id": 1  # admin
        },
        {
            "email": "user@test.com",
            "password": "user123",
            "full_name": "User Test",
            "role_id": 2  # usuario
        }
    ]
    
    for user in test_users:
        # Verificar si existe
        existing, count = supabase.table("users").select("id", count='exact').eq("email", user["email"]).execute()
        
        if count > 0:
            print(f"✔ Usuario de prueba {user['email']} ya existe")
            continue
        
        # Crear usuario
        data = {
            "email": user["email"],
            "hashed_password": hash_password(user["password"]),
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "is_active": True,
            "is_verified": True
        }
        
        supabase.table("users").insert(data).execute()
        print(f"🚀 Usuario de prueba creado: {user['email']} / {user['password']}")


def run_seed():
    """
    Ejecuta todas las seeds en orden.
    """
    print("=" * 50)
    print("Iniciando seed...")
    print("=" * 50)
    
    seed_roles()
    print()
    
    seed_admin_user()
    print()
    
    seed_test_users()
    print()
    
    print("=" * 50)
    print("✅ Seed completado exitosamente")
    print("=" * 50)
    print("\nUsuarios creados:")
    print("  Admin demo: admin@demo.com / admin123")
    print("  Admin test: admin@test.com / admin123")
    print("  User test:  user@test.com / user123")


if __name__ == "__main__":
    run_seed()