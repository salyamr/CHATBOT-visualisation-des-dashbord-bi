import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
django.setup()

from Chatbot.models import CasDeTest
from Chatbot.views import generate_priority_criticality_matrix

def test_data_and_chart():
    print("=== TEST DE DÉBOGAGE ===")
    
    # 1. Vérifier les données dans la base
    total_count = CasDeTest.objects.count()
    print(f"Total d'entrées dans la base : {total_count}")
    
    if total_count == 0:
        print("❌ Aucune donnée trouvée !")
        return
    
    # 2. Afficher quelques exemples
    print("\n--- Exemples de données ---")
    for cas in CasDeTest.objects.all()[:5]:
        print(f"Projet: {cas.projet}, Priorité: {cas.prio}, Criticité: {cas.criticality}")
    
    # 3. Compter par priorité et criticité
    print("\n--- Répartition par priorité ---")
    for prio in ['High', 'Medium', 'Low']:
        count = CasDeTest.objects.filter(prio=prio).count()
        print(f"{prio}: {count}")
    
    print("\n--- Répartition par criticité ---")
    for crit in ['High', 'Medium', 'Low']:
        count = CasDeTest.objects.filter(criticality=crit).count()
        print(f"{crit}: {count}")
    
    # 4. Matrice complète
    print("\n--- Matrice Priorité/Criticité ---")
    priorities = ['High', 'Medium', 'Low']
    criticalities = ['High', 'Medium', 'Low']
    
    for i, prio in enumerate(priorities):
        row = []
        for j, crit in enumerate(criticalities):
            count = CasDeTest.objects.filter(prio=prio, criticality=crit).count()
            row.append(count)
        print(f"{prio}: {row}")
    
    # 5. Tester la fonction de génération de graphique
    print("\n--- Test de la fonction generate_priority_criticality_matrix ---")
    try:
        chart_data = generate_priority_criticality_matrix()
        print("✅ Fonction exécutée avec succès")
        print(f"Type de graphique: {chart_data.get('type', 'Non défini')}")
        print(f"Titre: {chart_data.get('layout', {}).get('title', 'Non défini')}")
        
        # Afficher la matrice Z
        z_data = chart_data.get('data', {}).get('z', [])
        if z_data:
            print("Matrice Z (données du graphique):")
            for i, row in enumerate(z_data):
                print(f"  {priorities[i]}: {row}")
        else:
            print("❌ Aucune donnée Z trouvée")
            
        # Vérifier s'il y a un message d'erreur
        if 'empty_data_message' in chart_data:
            print(f"❌ Message d'erreur: {chart_data['empty_data_message']}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_and_chart()
