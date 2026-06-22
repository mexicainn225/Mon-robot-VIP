import os
from supabase import create_client

# Récupère les clés depuis les variables d'environnement sur Render
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def ajouter_utilisateur(user_id, id_1win):
    # Insère ou met à jour l'utilisateur dans la table "users"
    supabase.table("users").upsert({
        "user_id": user_id, 
        "id_1win": id_1win, 
        "status": "pending"
    }).execute()

def valider_utilisateur(user_id):
    # Change le statut en 'active'
    supabase.table("users").update({"status": "active"}).eq("user_id", user_id).execute()

def est_valide(user_id):
    # Vérifie si le statut est 'active'
    response = supabase.table("users").select("status").eq("user_id", user_id).execute()
    data = response.data
    return len(data) > 0 and data[0]['status'] == 'active'
