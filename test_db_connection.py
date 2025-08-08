import os
import django
import psycopg2
from psycopg2 import OperationalError

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
django.setup()

from django.conf import settings
from Chatbot.models import CasDeTest

def test_postgresql_connection():
    """Test la connexion directe à PostgreSQL"""
    print("=== TEST CONNEXION POSTGRESQL ===")
    
    db_config = settings.DATABASES['default']
    print(f"Configuration DB:")
    print(f"- Engine: {db_config['ENGINE']}")
    print(f"- Name: {db_config['NAME']}")
    print(f"- User: {db_config['USER']}")
    print(f"- Host: {db_config['HOST']}")
    print(f"- Port: {db_config['PORT']}")
    
    try:
        # Test de connexion directe
        connection = psycopg2.connect(
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config['PORT']
        )
        print("✅ Connexion PostgreSQL réussie")
        
        # Test de requête directe
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM \"Chatbot_casdetest\";")
        count = cursor.fetchone()[0]
        print(f"✅ Nombre d'entrées dans PostgreSQL: {count}")
        
        if count > 0:
            cursor.execute("SELECT projet, prio, criticality FROM \"Chatbot_casdetest\" LIMIT 5;")
            rows = cursor.fetchall()
            print("✅ Exemples de données PostgreSQL:")
            for row in rows:
                print(f"  - Projet: {row[0]}, Priorité: {row[1]}, Criticité: {row[2]}")
        
        cursor.close()
        connection.close()
        
    except OperationalError as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        return False
    
    return True

def test_django_orm():
    """Test via l'ORM Django"""
    print("\n=== TEST ORM DJANGO ===")
    
    try:
        # Test du count via Django ORM
        total_count = CasDeTest.objects.count()
        print(f"✅ Nombre d'entrées via Django ORM: {total_count}")
        
        if total_count > 0:
            print("✅ Exemples via Django ORM:")
            for cas in CasDeTest.objects.all()[:5]:
                print(f"  - Projet: {cas.projet}, Priorité: {cas.prio}, Criticité: {cas.criticality}")
        else:
            print("❌ Aucune donnée trouvée via Django ORM")
            
        return total_count > 0
        
    except Exception as e:
        print(f"❌ Erreur Django ORM: {e}")
        return False

def check_database_file():
    """Vérifie s'il y a un fichier SQLite local"""
    print("\n=== VÉRIFICATION FICHIER SQLITE ===")
    
    sqlite_files = ['db.sqlite3', 'database.sqlite3', 'chatbot.sqlite3']
    for filename in sqlite_files:
        if os.path.exists(filename):
            print(f"⚠️  Fichier SQLite trouvé: {filename}")
            size = os.path.getsize(filename)
            print(f"   Taille: {size} bytes")
        else:
            print(f"✅ Pas de fichier {filename}")

if __name__ == "__main__":
    print("=== DIAGNOSTIC COMPLET BASE DE DONNÉES ===\n")
    
    # 1. Test PostgreSQL
    pg_ok = test_postgresql_connection()
    
    # 2. Test Django ORM
    orm_ok = test_django_orm()
    
    # 3. Vérification fichiers SQLite
    check_database_file()
    
    # 4. Conclusion
    print("\n=== CONCLUSION ===")
    if pg_ok and orm_ok:
        print("✅ Tout fonctionne correctement")
    elif pg_ok and not orm_ok:
        print("⚠️  PostgreSQL accessible mais pas de données via Django")
    elif not pg_ok:
        print("❌ Problème de connexion PostgreSQL")
        print("💡 Solutions possibles:")
        print("   1. Vérifier que PostgreSQL est démarré")
        print("   2. Vérifier les paramètres de connexion")
        print("   3. Utiliser SQLite temporairement")
    
    print("\n🔧 Pour résoudre le problème:")
    print("1. Si PostgreSQL ne fonctionne pas -> Passer à SQLite")
    print("2. Si PostgreSQL fonctionne -> Migrer les données vers PostgreSQL")
