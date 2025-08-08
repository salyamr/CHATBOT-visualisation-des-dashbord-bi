from django.contrib import admin
from .models import CasDeTest

@admin.register(CasDeTest)
class CasDeTestAdmin(admin.ModelAdmin):
    list_display = ("projet", "marco_scenario", "test_state", "prio", "criticality")
    list_filter = ("projet", "test_state", "prio", "criticality", "profile")
    search_fields = ("marco_scenario", "test_cases", "expected_result")
