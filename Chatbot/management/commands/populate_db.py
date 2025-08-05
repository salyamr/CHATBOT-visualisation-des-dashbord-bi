from django.core.management.base import BaseCommand
from Chatbot.models import Responsable, Application, Demande, Transfert, Audit, Satisfaction
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données fictives'

    def handle(self, *args, **options):
        self.stdout.write("Création des données fictives...")
        
        # Nettoyer les tables existantes
        self.stdout.write("Nettoyage des tables existantes...")
        Satisfaction.objects.all().delete()
        Audit.objects.all().delete()
        Transfert.objects.all().delete()
        Demande.objects.all().delete()
        Application.objects.all().delete()
        Responsable.objects.all().delete()
        
        # Créer des responsables
        responsables = []
        for i in range(1, 11):
            resp = Responsable.objects.create(
                identifiant=f'USER{i:03d}',
                nom=f'Nom{i}',
                prenom=f'Prenom{i}'
            )
            responsables.append(resp)
            self.stdout.write(f"Créé responsable: {resp}")
        
        # Créer des applications
        applications = []
        app_names = ['DIL', 'Plateforme PLM WEB', 'Outils Auteurs V6', 'Catia V5', '3DCom / VPM']
        for name in app_names:
            app = Application.objects.create(
                nom_application=name,
                perimetre=random.choice(['France', 'International', 'Europe'])
            )
            applications.append(app)
            self.stdout.write(f"Créée application: {app}")
        
        # Créer des demandes
        categories = ['Incident', 'Demande', 'Problème', 'Question']
        for i in range(1, 101):
            date_ouverture = timezone.now() - timedelta(days=random.randint(1, 365))
            date_fermeture = date_ouverture + timedelta(days=random.randint(1, 30))
            
            demande = Demande.objects.create(
                reference_demande=f'DEM{1000 + i}',
                application=random.choice(applications),
                date_ouverture=date_ouverture,
                date_fermeture=date_fermeture if random.random() > 0.2 else None,
                categorie=random.choice(categories),
                commentaire=f"Commentaire pour la demande {i}",
                identifiant_demandeur=random.choice(responsables),
                orientation=random.choice(['refus', 'non'])
            )
            
            # Créer des transferts pour certaines demandes
            if random.random() > 0.7:  # 30% des demandes ont un transfert
                Transfert.objects.create(
                    ref_demande=demande,
                    identifiant_expert=random.choice(responsables),
                    identifiant_support=random.choice(responsables),
                    date_transfert=date_ouverture + timedelta(hours=random.randint(1, 24))
                )
            
            # Créer un audit pour certaines demandes
            if random.random() > 0.5:  # 50% des demandes ont un audit
                Audit.objects.create(
                    identifiant_demande=demande,
                    resultat_audit=random.randint(1, 5),
                    identifiant_audit=random.choice(responsables),
                    date_audit=date_fermeture if demande.date_fermeture else timezone.now()
                )
            
            # Créer une satisfaction pour certaines demandes fermées
            if demande.date_fermeture and random.random() > 0.3:  # 70% des demandes fermées ont une satisfaction
                Satisfaction.objects.create(
                    ref_demande=demande,
                    score=random.randint(1, 5)
                )
            
            if i % 10 == 0:
                self.stdout.write(f"Créées {i} demandes...")
        
        self.stdout.write(self.style.SUCCESS("Données fictives créées avec succès !"))
