from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze_command, name='analyze_command'),
     path('generate-chart/', views.generate_chart, name='generate_chart'),
    # ...autres vues...
]