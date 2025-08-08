#!/usr/bin/env python3
"""
Test simple d'un graphique
"""
import requests
import json
import time

def test_single_chart():
    """Test une seule requête de graphique"""
    print("🔍 Test simple d'un graphique")
    print("=" * 40)
    
    url = "http://127.0.0.1:8000/Alten/Chatbot/generate-chart/"
    query = "graphique des demandes par priorité"
    
    print(f"📊 Test: '{query}'")
    print(f"🌐 URL: {url}")
    
    try:
        print("⏳ Envoi de la requête...")
        response = requests.post(url, data={'text': query}, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📏 Taille réponse: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON valide reçu")
                
                # Structure de base
                print(f"\n📋 Structure de la réponse:")
                print(f"  - success: {data.get('success')}")
                print(f"  - is_heatmap: {data.get('is_heatmap')}")
                print(f"  - title: {data.get('title')}")
                print(f"  - error: {data.get('error', 'Aucune')}")
                
                # Données du graphique
                if 'chart_data' in data:
                    chart_data = data['chart_data']
                    print(f"\n📊 Chart Data:")
                    print(f"  - type: {chart_data.get('type')}")
                    
                    if 'data' in chart_data:
                        inner_data = chart_data['data']
                        print(f"  - labels: {inner_data.get('labels')}")
                        
                        if 'datasets' in inner_data:
                            datasets = inner_data['datasets']
                            print(f"  - datasets count: {len(datasets)}")
                            
                            for i, dataset in enumerate(datasets):
                                print(f"    Dataset {i+1}:")
                                print(f"      - label: {dataset.get('label')}")
                                print(f"      - data: {dataset.get('data')}")
                                print(f"      - data length: {len(dataset.get('data', []))}")
                        else:
                            print("  ❌ Pas de datasets")
                    else:
                        print("  ❌ Pas de section 'data'")
                        
                    # Affichage complet pour débogage
                    print(f"\n🔍 JSON complet:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print("❌ Pas de chart_data")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON: {e}")
                print(f"Contenu brut: {response.text}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Contenu: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Le serveur Django est-il démarré ?")
        print("   Vérifiez que le serveur tourne sur http://127.0.0.1:8000/")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le serveur met trop de temps à répondre")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    print("🚀 Test simple de graphique ALTEN")
    print("=" * 50)
    test_single_chart()
    print("\n✅ Test terminé!")
