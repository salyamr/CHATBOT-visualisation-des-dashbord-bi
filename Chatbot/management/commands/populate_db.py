from django.core.management.base import BaseCommand
from Chatbot.models import CasDeTest  # Only import existing models
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données fictives'

    def handle(self, *args, **options):
        self.stdout.write("Création des données fictives...")
        
        # Nettoyer les tables existantes
        self.stdout.write("Nettoyage des tables existantes...")
        CasDeTest.objects.all().delete()
        
        # Create sample test cases
        self.stdout.write("Création des cas de test...")
        test_cases = [
            {
                "projet": "Projet A",
                "marco_scenario": "Test de connexion",
                "test_perimeter": "Frontend",
                "pre_requisites": "Avoir un compte valide",
                "profile": "Testeur",
                "test_cases": "1. Aller sur la page de connexion\n2. Entrer les identifiants\n3. Cliquer sur se connecter",
                "prio": "High",
                "criticality": "High",
                "test_state": "Not Started",
                "step_test": "Vérifier que l'utilisateur peut se connecter",
                "expected_result": "L'utilisateur est connecté et redirigé vers le tableau de bord"
            },
            {
                "projet": "Projet B",
                "marco_scenario": "Test de déconnexion",
                "test_perimeter": "Frontend",
                "pre_requisites": "Être connecté",
                "profile": "Testeur",
                "test_cases": "1. Cliquer sur le menu utilisateur\n2. Sélectionner Déconnexion",
                "prio": "Medium",
                "criticality": "Medium",
                "test_state": "In Progress",
                "step_test": "Vérifier que l'utilisateur peut se déconnecter",
                "expected_result": "L'utilisateur est déconnecté et redirigé vers la page de connexion"
            }
        ]
        
        for test_data in test_cases:
            CasDeTest.objects.create(**test_data)
        
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))