import requests
import json

def test_chart_endpoint():
    """Test l'endpoint de génération de graphiques"""
    print("=== TEST ENDPOINT GÉNÉRATION GRAPHIQUES ===")
    
    url = "http://127.0.0.1:8000/Alten/Chatbot/generate-chart/"
    
    # Test avec différentes requêtes
    test_queries = [
        "matrice priorité criticité",
        "matrice priorité/criticité", 
        "répartition des cas de test par priorité et criticité",
        "graphique priorité criticité",
        "heatmap priorité criticité"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: '{query}' ---")
        
        try:
            # Préparer les données POST
            data = {'text': query}
            
            # Faire la requête
            response = requests.post(url, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'Non défini')}")
            print(f"Taille réponse: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    print("✅ Réponse JSON valide")
                    
                    # Analyser la structure de la réponse
                    print(f"Clés de la réponse: {list(json_response.keys())}")
                    
                    if 'success' in json_response:
                        print(f"Success: {json_response['success']}")
                    
                    if 'error' in json_response:
                        print(f"❌ Erreur: {json_response['error']}")
                    
                    if 'chart_data' in json_response:
                        chart_data = json_response['chart_data']
                        print(f"✅ Chart data présent")
                        print(f"Type de graphique: {chart_data.get('type', 'Non défini')}")
                        
                        if 'data' in chart_data:
                            data_section = chart_data['data']
                            print(f"Données du graphique:")
                            print(f"  - X: {data_section.get('x', 'Non défini')}")
                            print(f"  - Y: {data_section.get('y', 'Non défini')}")
                            z_data = data_section.get('z', [])
                            if z_data:
                                print(f"  - Z (matrice): {z_data}")
                            else:
                                print(f"  - Z: Vide ou non défini")
                        
                        if 'layout' in chart_data:
                            layout = chart_data['layout']
                            print(f"Layout: {layout.get('title', 'Pas de titre')}")
                    
                    if 'title' in json_response:
                        print(f"Titre: {json_response['title']}")
                    
                    if 'is_heatmap' in json_response:
                        print(f"Est une heatmap: {json_response['is_heatmap']}")
                        
                except json.JSONDecodeError:
                    print("❌ Réponse non-JSON")
                    print(f"Contenu brut: {response.text[:500]}...")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                print(f"Contenu: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erreur de connexion - Le serveur Django est-il démarré ?")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
    
    print("\n=== RECOMMANDATIONS ===")
    print("1. Vérifiez que le serveur Django tourne sur http://127.0.0.1:8000")
    print("2. Testez dans le navigateur avec le mode graphique activé")
    print("3. Vérifiez la console du navigateur pour les erreurs JavaScript")

if __name__ == "__main__":
    test_chart_endpoint()
