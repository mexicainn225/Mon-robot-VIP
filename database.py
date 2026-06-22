import sqlite3

def init_db():
    # Crée le fichier de base de données
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Crée une table pour stocker les IDs des utilisateurs validés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            id_1win TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def ajouter_utilisateur(user_id, id_1win):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, id_1win, status) VALUES (?, ?, ?)', 
                   (user_id, id_1win, 'pending'))
    conn.commit()
    conn.close()

def valider_utilisateur(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', ('active', user_id))
    conn.commit()
    conn.close()

def est_valide(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 'active'

# Initialiser la base au lancement
init_db()

