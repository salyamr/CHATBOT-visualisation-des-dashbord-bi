import os
import matplotlib
# Utiliser le backend 'Agg' pour éviter les problèmes d'affichage
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_test_plot():
    # Créer le dossier d'analyse s'il n'existe pas
    os.makedirs('static/analysis', exist_ok=True)
    
    # Données de test
    categories = ['High', 'Medium', 'Low']
    values = [30, 50, 20]  # Distribution arbitraire
    
    # Créer le graphique
    plt.figure(figsize=(10, 6))
    
    # Créer un graphique à barres
    bars = plt.bar(categories, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # Ajouter des titres et des étiquettes
    plt.title('Test de visualisation - Répartition par priorité')
    plt.xlabel('Priorité')
    plt.ylabel('Nombre de cas')
    
    # Ajuster la mise en page
    plt.tight_layout()
    
    # Sauvegarder le graphique
    output_path = 'static/analysis/test_plot.png'
    plt.savefig(output_path)
    plt.close()
    
    print(f"Graphique de test généré avec succès : {os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    plot_path = create_test_plot()
    print(f"Vous pouvez ouvrir le fichier suivant dans votre navigateur :")
    print(f"file://{os.path.abspath(plot_path)}")
