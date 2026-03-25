"""
Connexion à la base de données MySQL.

Lit la configuration depuis les variables d'environnement afin de ne
jamais coder en dur les identifiants de connexion.

Variables d'environnement reconnues :
    DB_HOST     : Hôte MySQL (défaut : localhost)
    DB_PORT     : Port MySQL (défaut : 3306)
    DB_USER     : Utilisateur MySQL (défaut : root)
    DB_PASSWORD : Mot de passe MySQL (défaut : root)
    DB_NAME     : Nom de la base de données (défaut : paiement_db)
"""

import os

import mysql.connector


def get_connection():
    """Retourne une nouvelle connexion MySQL à partir des variables d'env.

    Chaque appel crée une connexion fraîche. L'appelant est responsable
    de la fermer (conn.close()) après utilisation.

    Returns:
        Une connexion MySQL active.

    Raises:
        mysql.connector.Error: Si la connexion échoue.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "paiement_db"),
    )
