import os
import django
import random
from datetime import datetime, timedelta
from django.db import models

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
django.setup()

from Chatbot.models import CasDeTest

def create_simple_test_data():
    # Nettoyer les données existantes
    print("Nettoyage des données existantes...")
    CasDeTest.objects.all().delete()
    
    # Données de test simples
    projets = [f"Projet_{i}" for i in range(1, 6)]
    priorities = ["High", "Medium", "Low"]
    states = ["Not Started", "In Progress", "Blocked", "KO", "OK", "N/A"]
    perimeters = ["UAT", "INT", "XP", "PROD"]
    
    print("Création de 50 entrées de test...")
    
    for i in range(50):
        CasDeTest.objects.create(
            projet=random.choice(projets),
            marco_scenario=f"Scenario_{i+1}",
            test_perimeter=random.choice(perimeters),
            pre_requisites=f"Prérequis pour le test {i+1}",
            profile=f"Profil_{random.randint(1, 5)}",
            test_cases=f"Cas de test pour le scénario {i+1}",
            prio=random.choices(priorities, weights=[3, 5, 2], k=1)[0],
            criticality=random.choices(priorities, weights=[2, 4, 4], k=1)[0],
            test_state=random.choices(states, weights=[2, 3, 1, 2, 4, 1], k=1)[0],
            step_test=f"Étape 1: Préparer\nÉtape 2: Exécuter\nÉtape 3: Vérifier",
            expected_result=f"Résultat attendu pour le test {i+1}"
        )
    
    print("Données de test créées avec succès!")

def generate_simple_plot():
    import matplotlib
    matplotlib.use('Agg')  # Utiliser le backend non interactif
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Créer le dossier d'analyse s'il n'existe pas
    os.makedirs('static/analysis', exist_ok=True)
    
    # Récupérer les données
    data = CasDeTest.objects.values('prio').annotate(count=models.Count('id')).order_by('prio')
    
    if not data:
        print("Aucune donnée trouvée pour générer le graphique.")
        return
    
    # Préparer les données pour le graphique
    priorities = [item['prio'] for item in data]
    counts = [item['count'] for item in data]
    
    # Créer le graphique
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=priorities, y=counts, color="blue")
    
    # Ajouter des étiquettes et un titre
    plt.title('Répartition des cas de test par priorité')
    plt.xlabel('Priorité')
    plt.ylabel('Nombre de cas')
    
    # Ajouter les valeurs sur les barres
    for i, v in enumerate(counts):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    # Sauvegarder le graphique
    output_path = 'static/analysis/simple_priority_distribution.png'
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    print(f"Graphique simple généré avec succès : {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_simple_test_data()
    generate_simple_plot()
    
    # Afficher les statistiques
    total = CasDeTest.objects.count()
    print(f"\nStatistiques des données générées:")
    print(f"- Total des entrées: {total}")
    
    # Afficher la répartition par priorité
    print("\nRépartition par priorité:")
    for prio in ["High", "Medium", "Low"]:
        count = CasDeTest.objects.filter(prio=prio).count()
        print(f"- {prio}: {count} ({(count/total)*100:.1f}%)")
