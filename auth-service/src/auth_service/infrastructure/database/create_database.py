import sqlite3

# Nom du fichier SQLite
db_path = "authservice.db"

# Connexion (crée le fichier si inexistant)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Exécuter le script SQL
with open("script.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()

print("Base de données et tables créées !")