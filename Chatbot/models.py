from django.db import models
class CasDeTest(models.Model):
    projet = models.CharField(max_length=100)

    marco_scenario = models.CharField(max_length=200)
    test_perimeter = models.CharField(max_length=100)
    pre_requisites = models.TextField(blank=True, null=True)
    profile = models.CharField(max_length=100)
    test_cases = models.TextField()
    prio = models.CharField(max_length=10, choices=[
        ("High", "High"), ("Medium", "Medium"), ("Low", "Low")
    ])
    criticality = models.CharField(max_length=10, choices=[
        ("High", "High"), ("Medium", "Medium"), ("Low", "Low")
    ])
    test_state = models.CharField(max_length=20, choices=[
        ("Not Started", "Not Started"), ("In Progress", "In Progress"), ("Blocked", "Blocked"),
        ("KO", "KO"), ("KO JDD", "KO JDD"), ("OK", "OK"), ("N/A", "N/A")
    ])
    step_test = models.TextField()
    expected_result = models.TextField()

    def __str__(self):
        return f"{self.projet} - {self.marco_scenario} ({self.test_state})"
