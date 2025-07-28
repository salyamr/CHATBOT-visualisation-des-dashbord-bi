from django.db import models

# Table Responsable (utilisable pour demandeur, auditeur, expert, support)
class Responsable(models.Model):
    identifiant = models.CharField(max_length=50, primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# Table Application
class Application(models.Model):
    nom_application = models.CharField(max_length=100)
    perimetre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nom_application


# Table Demande
class Demande(models.Model):
    ORIENTATION_CHOICES = [
        ("refus", "Refus"),
        ("non", "Non orienté"),
    ]

    reference_demande = models.CharField(max_length=50, primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="demandes")
    date_ouverture = models.DateTimeField()
    date_fermeture = models.DateTimeField(blank=True, null=True)
    categorie = models.CharField(max_length=100)
    commentaire = models.TextField(blank=True, null=True)
    identifiant_demandeur = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name="demandes")
    orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES)

    def __str__(self):
        return self.reference_demande


# Table Transfert
class Transfert(models.Model):
    ref_demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name="transferts")
    identifiant_expert = models.ForeignKey(Responsable, on_delete=models.SET_NULL, null=True, related_name="transferts_expert")
    identifiant_support = models.ForeignKey(Responsable, on_delete=models.SET_NULL, null=True, related_name="transferts_support")
    date_transfert = models.DateTimeField()

    def __str__(self):
        return f"Transfert {self.ref_demande.reference_demande}"


# Table Audit
class Audit(models.Model):
    identifiant_demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name="audits")
    resultat_audit = models.IntegerField()
    identifiant_audit = models.ForeignKey(Responsable, on_delete=models.SET_NULL, null=True, related_name="audits_realises")
    date_audit = models.DateTimeField()

    def __str__(self):
        return f"Audit {self.id} - Demande {self.identifiant_demande.reference_demande}"


# Table Satisfaction
class Satisfaction(models.Model):
    ref_demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name="satisfactions")
    score = models.IntegerField()

    def __str__(self):
        return f"Satisfaction Demande {self.ref_demande.reference_demande}"


# Table Historique (pour enregistrer les requêtes d'une conversation du chatbot)
class Historique(models.Model):
    requete = models.TextField()
    reponse = models.TextField(blank=True, null=True)
    date_requete = models.DateTimeField(auto_now_add=True)
    conversation_id = models.CharField(max_length=100, help_text="Permet de relier les requêtes d'une même conversation")

    def __str__(self):
        return f"Historique {self.id} - Conversation {self.conversation_id}"

