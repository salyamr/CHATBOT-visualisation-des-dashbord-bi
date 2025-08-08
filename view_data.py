#!/usr/bin/env python3
"""
Script simple pour afficher les données de la base PostgreSQL
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatbotAlten.settings')
django.setup()

from Chatbot.models import CasDeTest

def view_data():
    """
    Affiche toutes les données dans le terminal
    """
    print("🚀 ALTEN - Visualisation des Données")
    print("=" * 80)
    
    # Récupérer toutes les données
    queryset = CasDeTest.objects.all()
    
    if not queryset.exists():
        print("❌ Aucune donnée trouvée dans la base")
        return
    
    print(f"📊 Total: {queryset.count()} cas de test\n")
    
    # En-tête du tableau
    print(f"{'ID':<4} {'Projet':<10} {'Périmètre':<15} {'Profil':<12} {'Priorité':<8} {'Criticité':<9} {'État':<12}")
    print("-" * 80)
    
    # Afficher chaque ligne
    for cas in queryset:
        print(f"{cas.id:<4} {cas.projet:<10} {cas.test_perimeter:<15} {cas.profile:<12} {cas.prio:<8} {cas.criticality:<9} {cas.test_state:<12}")
    
    print("-" * 80)
    print(f"📊 Total: {queryset.count()} cas de test")

def view_summary():
    """
    Affiche un résumé statistique
    """
    print("\n📈 RÉSUMÉ STATISTIQUE")
    print("=" * 40)
    
    queryset = CasDeTest.objects.all()
    
    # Statistiques par priorité
    print("\n🎯 Par Priorité:")
    for prio in ['High', 'Medium', 'Low']:
        count = queryset.filter(prio=prio).count()
        print(f"   {prio:<8}: {count:>3} cas")
    
    # Statistiques par criticité
    print("\n⚡ Par Criticité:")
    for crit in ['High', 'Medium', 'Low']:
        count = queryset.filter(criticality=crit).count()
        print(f"   {crit:<8}: {count:>3} cas")
    
    # Statistiques par état
    print("\n📋 Par État:")
    states = queryset.values_list('test_state', flat=True).distinct().order_by('test_state')
    for state in states:
        count = queryset.filter(test_state=state).count()
        print(f"   {state:<12}: {count:>3} cas")
    
    # Statistiques par projet
    print("\n🏗️ Par Projet:")
    projects = queryset.values_list('projet', flat=True).distinct().order_by('projet')
    for project in projects:
        count = queryset.filter(projet=project).count()
        print(f"   {project:<10}: {count:>3} cas")

if __name__ == "__main__":
    # Afficher les données
    view_data()
    
    # Afficher le résumé
    view_summary()
    
    print("\n✅ Terminé!")
