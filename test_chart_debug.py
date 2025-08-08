#!/usr/bin/env python3
"""
Script de débogage pour tester les graphiques non-heatmap
"""
import requests
import json
import pprint

def test_chart_requests():
    """Test différents types de graphiques"""
    print("🔍 Test des graphiques non-heatmap")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/Alten/Chatbot/generate-chart/"
    
    # Tests avec différentes requêtes
    test_queries = [
        "graphique des demandes par priorité",
        "répartition des projets", 
        "graphique en secteur des statuts",
        "distribution des cas de test",
        "graphique en barres des priorités"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Faire la requête POST
            response = requests.post(url, data={'text': query}, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Réponse JSON reçue")
                    
                    # Analyser la structure
                    print(f"Success: {data.get('success', 'Non défini')}")
                    print(f"Is Heatmap: {data.get('is_heatmap', 'Non défini')}")
                    print(f"Title: {data.get('title', 'Non défini')}")
                    
                    if 'error' in data:
                        print(f"❌ ERREUR: {data['error']}")
                        continue
                    
                    if 'chart_data' in data:
                        chart_data = data['chart_data']
                        print(f"\n📈 Chart Data Structure:")
                        print(f"  Type: {chart_data.get('type', 'Non défini')}")
                        
                        if 'data' in chart_data:
                            chart_inner_data = chart_data['data']
                            print(f"  Labels: {chart_inner_data.get('labels', 'Non défini')}")
                            
                            if 'datasets' in chart_inner_data:
                                datasets = chart_inner_data['datasets']
                                print(f"  Datasets count: {len(datasets)}")
                                
                                for j, dataset in enumerate(datasets):
                                    print(f"    Dataset {j+1}:")
                                    print(f"      Label: {dataset.get('label', 'Non défini')}")
                                    print(f"      Data: {dataset.get('data', 'Non défini')}")
                                    print(f"      Data length: {len(dataset.get('data', []))}")
                            else:
                                print("  ❌ Pas de datasets trouvés")
                        else:
                            print("  ❌ Pas de section 'data' trouvée")
                        
                        # Afficher la structure complète pour débogage
                        print(f"\n🔍 Structure complète:")
                        pprint.pprint(chart_data, depth=3, width=80)
                    else:
                        print("❌ Pas de chart_data dans la réponse")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur JSON: {e}")
                    print(f"Contenu brut: {response.text[:500]}...")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                print(f"Contenu: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
        
        print()

def test_data_availability():
    """Test la disponibilité des données dans la base"""
    print("\n🗄️ Test de la disponibilité des données")
    print("=" * 50)
    
    try:
        import os
        import sys
        import django
        
        # Configuration Django
        project_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(project_path)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
        django.setup()
        
        from Chatbot.models import CasDeTest
        
        # Vérifier les données
        total_cases = CasDeTest.objects.count()
        print(f"📊 Total cas de test: {total_cases}")
        
        if total_cases > 0:
            # Répartition par priorité
            priorities = CasDeTest.objects.values('prio').distinct()
            print(f"🎯 Priorités disponibles: {[p['prio'] for p in priorities]}")
            
            for prio in priorities:
                count = CasDeTest.objects.filter(prio=prio['prio']).count()
                print(f"  - {prio['prio']}: {count} cas")
            
            # Répartition par projet
            projets = CasDeTest.objects.values('projet').distinct()[:5]
            print(f"📁 Projets disponibles (5 premiers): {[p['projet'] for p in projets]}")
            
            # Répartition par statut
            statuts = CasDeTest.objects.values('test_state').distinct()
            print(f"📋 Statuts disponibles: {[s['test_state'] for s in statuts]}")
            
        else:
            print("❌ Aucune donnée trouvée dans la base")
            
    except Exception as e:
        print(f"❌ Erreur lors du test des données: {e}")

if __name__ == "__main__":
    print("🚀 Script de débogage des graphiques ALTEN")
    print("=" * 60)
    
    # Test des données
    test_data_availability()
    
    # Test des endpoints
    test_chart_requests()
    
    print("\n✅ Tests terminés!")
