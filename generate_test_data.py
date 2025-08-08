import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
django.setup()

from Chatbot.models import CasDeTest

def generate_test_data(num_entries=50):
    fake = Faker('fr_FR')
    
    # Listes de valeurs possibles pour les champs
    projets = ['ProjetA', 'ProjetB', 'ProjetC', 'ProjetD', 'ProjetE']
    etats = ['Not Started', 'In Progress', 'Blocked', 'KO', 'KO JDD', 'OK', 'N/A']
    priorites = ['High', 'Medium', 'Low']
    profils = ['Admin', 'Utilisateur', 'Testeur', 'Développeur', 'Chef de projet']
    perimetres = ['Frontend', 'Backend', 'API', 'Base de données', 'UI/UX']
    
    # Nettoyer les données existantes (optionnel, à décommenter si nécessaire)
    CasDeTest.objects.all().delete()
    print("Anciennes données supprimées.")
    
    # Générer les entrées
    for _ in range(num_entries):
        # Préparation des données pour test_cases
        test_case1 = fake.sentence()
        test_case2 = fake.sentence()
        test_case3 = fake.sentence()
        
        # Préparation des étapes
        etape1 = fake.sentence()
        etape2 = fake.sentence()
        etape3 = fake.sentence()
        
        cas_test = CasDeTest(
            projet=random.choice(projets),
            marco_scenario=fake.sentence(nb_words=6),
            test_perimeter=random.choice(perimetres),
            pre_requisites=fake.paragraph(nb_sentences=2),
            profile=random.choice(profils),
            test_cases=f"""
            Cas de test 1: {test_case1}
            Cas de test 2: {test_case2}
            Cas de test 3: {test_case3}
            """,
            prio=random.choice(priorites),
            criticality=random.choice(priorites),
            test_state=random.choice(etats),
            step_test=f"""
            1. {etape1}
            2. {etape2}
            3. {etape3}
            """,
            expected_result=fake.paragraph(nb_sentences=2)
        )
        cas_test.save()
    
    print(f"{num_entries} entrées de test ont été créées avec succès!")
    
    # Vérification
    total_count = CasDeTest.objects.count()
    print(f"Total d'entrées dans la base de données : {total_count}")
    
    # Afficher quelques exemples
    if total_count > 0:
        print("\nExemples d'entrées créées :")
        for cas in CasDeTest.objects.all()[:3]:
            print(f"- {cas.projet}: {cas.marco_scenario} (Priorité: {cas.prio}, Criticité: {cas.criticality})")
    
if __name__ == "__main__":
    # Générer 50 entrées de test (vous pouvez modifier ce nombre)
    generate_test_data(50)
