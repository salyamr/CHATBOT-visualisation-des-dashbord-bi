# Standard Python
import logging, re, uuid, json, io, base64
from datetime import datetime, date, timedelta

# Django
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import (
    Count, Avg, Max, Min, Sum, Q, F,
    Subquery, OuterRef, ExpressionWrapper, fields
)
from django.db.models.functions import TruncMonth, TruncYear, TruncWeek
from django.core.exceptions import ObjectDoesNotExist

# Externes
import pandas as pd
import numpy as np
from django.db.models import Value, CharField
from django.db.models.functions import Concat


# Langchain / IA
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_openai import OpenAI  # optionnel si besoin d'OpenAI

# Modèles Django personnalisés
from .models import CasDeTest

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'chatbot.html')


@csrf_exempt
@csrf_exempt
def generate_chart(request):
    """
    Fonction pour générer des graphiques basés sur la base de données ALTEN
    Utilise Mistral AI pour analyser la requête et générer le graphique approprié
    """
    if request.method == 'POST':
        user_query = request.POST.get('text', '').strip()
        
        if not user_query:
            return JsonResponse({'error': 'Requête vide'})
        
        try:
            # Vérifier si la requête concerne la matrice de priorité/criticité
            if any(term in user_query.lower() for term in ['matrice', 'priorité/criticité', 'priorite/criticite', 'matrice priorité', 'matrice criticité']):
                chart_data = generate_priority_criticality_matrix()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Matrice Priorité/Criticité',
                    'description': 'Répartition des cas de test par niveau de priorité et de criticité',
                    'is_heatmap': True  # Indique au frontend qu'il s'agit d'une heatmap
                })
            
            # Détection directe des requêtes courantes (fonctions simplifiées)
            elif any(term in user_query.lower() for term in ['priorité', 'priority', 'prio']):
                chart_data = generate_priority_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Priorité',
                    'description': 'Nombre de cas de test par niveau de priorité',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['projet', 'project']):
                chart_data = generate_project_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Projet',
                    'description': 'Nombre de cas de test par projet',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['statut', 'status', 'état']):
                chart_data = generate_status_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Statut',
                    'description': 'Nombre de cas de test par statut',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['périmètre', 'perimeter']):
                chart_data = generate_test_perimeter_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Périmètre de Test',
                    'description': 'Nombre de cas de test par périmètre de test',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['état', 'state']):
                chart_data = generate_test_states_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par État des Tests',
                    'description': 'Nombre de cas de test par état des tests',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['profil', 'profile']):
                chart_data = generate_profile_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Profil',
                    'description': 'Nombre de cas de test par profil',
                    'is_heatmap': False
                })
            elif any(term in user_query.lower() for term in ['criticité', 'criticality']):
                chart_data = generate_criticality_chart()
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': 'Répartition par Criticité',
                    'description': 'Nombre de cas de test par niveau de criticité',
                    'is_heatmap': False
                })
            else:
                # Utiliser l'IA Mistral comme fallback
                llm = ChatMistralAI(
                    model="mistral-large-latest",
                    mistral_api_key="3Q57TEIWwcxOE8fSK4CuYvRPJnOKfP9w"
                )
                
                chart_config = analyze_chart_request(llm, user_query)
                
                if chart_config.get('error'):
                    return JsonResponse({'error': chart_config['error']})
                
                chart_data = generate_chart_data(chart_config)
                
                return JsonResponse({
                    'success': True,
                    'chart_data': chart_data,
                    'title': chart_config.get('title', 'Graphique ALTEN'),
                    'description': chart_config.get('description', ''),
                    'query_analysis': chart_config,
                    'is_heatmap': False
                })
            
        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de la génération: {str(e)}'})
    
    return JsonResponse({'error': 'Méthode non autorisée'})

def analyze_chart_request(llm, user_query):
    """
    Utilise Mistral AI pour analyser la demande de graphique
    """
    
    # Prompt structuré pour l'analyse
    analysis_prompt = f"""
    Tu es un expert en analyse de données pour le système ALTEN. 
    Analyse cette requête utilisateur et détermine quel type de graphique générer.

    BASE DE DONNÉES DISPONIBLE (modèle CasDeTest):
    - projet: nom du projet
    - test_perimeter: périmètre du test
    - profile: profil de l'utilisateur
    - prio: priorité (High, Medium, Low)
    - criticality: criticité (High, Medium, Low)
    - test_state: état du test (Not Started, In Progress, Blocked, KO, KO JDD, OK, N/A)

    REQUÊTE UTILISATEUR: "{user_query}"
    
    Réponds UNIQUEMENT avec un JSON valide contenant:
    {{
        "chart_type": "bar|line|pie|doughnut|radar",
        "data_source": "demandes",  # Toujours 'demandes' car nous n'avons qu'une source de données
        "groupby": "test_state|projet|périmètre|profil|priorité",
        "metric": "count",  # Toujours 'count' pour l'instant
        "title": "Titre du graphique",
        "description": "Description courte",
        "filters": {{}},
        "x_label": "Label axe X",
        "y_label": "Label axe Y"
    }}
    
    Exemples:
    - "graphique des cas de test par état" → chart_type: "bar", groupby: "test_state"
    - "répartition par projet" → chart_type: "pie", groupby: "projet"
    - "nombre de cas par profil" → chart_type: "bar", groupby: "profil"
    - "priorité des cas de test" → chart_type: "pie", groupby: "priorité"
    - "périmètre des tests" → chart_type: "bar", groupby: "périmètre"
    """
    
    try:
        response = llm.invoke(analysis_prompt)
        
        # Nettoyer la réponse pour extraire le JSON
        response_text = response.content.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
            
        config = json.loads(response_text)
        
        # Validation et valeurs par défaut
        config['chart_type'] = config.get('chart_type', 'bar')
        config['data_source'] = 'demandes'  # Forcer cette valeur car c'est la seule source
        config['groupby'] = config.get('groupby', 'test_state')
        config['metric'] = 'count'  # Forcer cette valeur car c'est la seule métrique supportée
        
        # Titre par défaut basé sur le groupby
        if 'title' not in config or not config['title']:
            groupby_labels = {
                'test_state': 'État des tests',
                'projet': 'Projets',
                'périmètre': 'Périmètre des tests',
                'profil': 'Profils utilisateurs',
                'priorité': 'Priorité des tests'
            }
            config['title'] = f"Répartition par {groupby_labels.get(config['groupby'], 'données')}"
        
        return config
        
    except json.JSONDecodeError as e:
        return {'error': f'Erreur de parsing JSON: {str(e)}'}
    except Exception as e:
        return {'error': f'Erreur lors de l\'analyse de la requête: {str(e)}'}

def generate_chart_data(config):
    """
    Génère les données du graphique selon la configuration
    """
    
    data_source = config['data_source']
    chart_type = config['chart_type']
    groupby = config['groupby']
    metric = config['metric']
    time_period = config.get('time_period', '6_mois')
    
    # Définir la période de temps
    end_date = datetime.now()
    if time_period == '1_mois':
        start_date = end_date - timedelta(days=30)
    elif time_period == '3_mois':
        start_date = end_date - timedelta(days=90)
    elif time_period == '6_mois':
        start_date = end_date - timedelta(days=180)
    elif time_period == '1_an':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = None
    
    try:
        if data_source == 'demandes':
            return generate_demandes_chart(config, start_date, end_date)
        elif data_source == 'applications':
            return generate_applications_chart(config, start_date, end_date)
        elif data_source == 'audits':
            return generate_audits_chart(config, start_date, end_date)
        elif data_source == 'satisfaction':
            return generate_satisfaction_chart(config, start_date, end_date)
        elif data_source == 'transferts':
            return generate_transferts_chart(config, start_date, end_date)
        else:
            raise ValueError(f"Source de données non supportée: {data_source}")
            
    except Exception as e:
        return {
            'type': 'bar',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Données indisponibles',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_demandes_chart(config, start_date, end_date):
    """Génère un graphique des demandes"""
    
    queryset = CasDeTest.objects.all()
    
    # Filtrer par période si définie
    if start_date:
        queryset = queryset.filter(date_creation__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_creation__lte=end_date)
    
    groupby = config['groupby']
    chart_type = config['chart_type']
    
    if groupby == 'test_state':
        data = list(queryset.values('test_state').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_state'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'projet':
        data = list(queryset.values('projet').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['projet'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'périmètre':
        data = list(queryset.values('test_perimeter').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_perimeter'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'profil':
        data = list(queryset.values('profile').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['profile'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'priorité':
        data = list(queryset.values('prio').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['prio'] for item in data]
        values = [item['count'] for item in data]
        
    else:
        # Par défaut: comptage mensuel
        data = list(queryset.annotate(
            periode=TruncMonth('date_creation')
        ).values('periode').annotate(
            count=Count('id')
        ).order_by('periode'))
        
        labels = [item['periode'].strftime('%Y-%m') for item in data]
        values = [item['count'] for item in data]
    
    # Couleurs selon le type de graphique
    if chart_type in ['pie', 'doughnut']:
        colors = [
            '#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3'
        ]
        background_colors = colors[:len(labels)]
    else:
        background_colors = ['rgba(255, 215, 0, 0.8)'] * len(labels)
        border_colors = ['rgba(255, 215, 0, 1)'] * len(labels)
    
    chart_data = {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': [{
                'label': config.get('title', 'Nombre de demandes'),
                'data': values,
                'backgroundColor': background_colors,
                'borderColor': border_colors if chart_type not in ['pie', 'doughnut'] else None,
                'borderWidth': 2 if chart_type not in ['pie', 'doughnut'] else None
            }]
        }
    }
    
    return chart_data

def generate_audits_chart(config, start_date, end_date):
    """Génère un graphique des audits"""
    
    queryset = CasDeTest.objects.all()
    
    if start_date:
        queryset = queryset.filter(date_creation__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_creation__lte=end_date)
    
    groupby = config['groupby']
    metric = config['metric']
    
    if groupby == 'test_state':
        data = list(queryset.values('test_state').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_state'] for item in data]
        values = [item['count'] for item in data]
    
    elif groupby == 'projet':
        data = list(queryset.values('projet').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['projet'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'périmètre':
        data = list(queryset.values('test_perimeter').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_perimeter'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'profil':
        data = list(queryset.values('profile').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['profile'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'priorité':
        data = list(queryset.values('prio').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['prio'] for item in data]
        values = [item['count'] for item in data]
        
    else:
        # Répartition des résultats d'audit
        data = list(queryset.values('test_state').annotate(
            count=Count('id')
        ).order_by('test_state'))
        
        labels = [f"Résultat {item['test_state']}" for item in data]
        values = [item['count'] for item in data]
    
    return {
        'type': config['chart_type'],
        'data': {
            'labels': labels,
            'datasets': [{
                'label': config.get('title', 'Audits'),
                'data': values,
                'backgroundColor': 'rgba(68, 68, 255, 0.8)',
                'borderColor': 'rgba(68, 68, 255, 1)',
                'borderWidth': 2
            }]
        }
    }

def generate_satisfaction_chart(config, start_date, end_date):
    """Génère un graphique des scores de satisfaction basé sur les priorités des cas de test"""
    
    queryset = CasDeTest.objects.all()
    
    # Filtrage par période si nécessaire
    # Note: Comme CasDeTest n'a pas de date, on ne peut pas filtrer par date
    # On garde la structure pour une éventuelle utilisation future
    
    if config['groupby'] == 'test_state':
        data = list(queryset.values('test_state').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_state'] for item in data]
        values = [item['count'] for item in data]
    
    else:
        # Distribution des priorités
        data = list(queryset.values('prio').annotate(
            count=Count('id')
        ).order_by('prio'))
        
        labels = [f"Priorité {item['prio']}" for item in data]
        values = [item['count'] for item in data]
    
    return {
        'type': config['chart_type'],
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Répartition par priorité',
                'data': values,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                'borderWidth': 1
            }]
        },
        'options': {
            'responsive': True,
            'plugins': {
                'legend': {
                    'position': 'top',
                },
                'title': {
                    'display': True,
                    'text': 'Répartition des cas de test par priorité'
                }
            }
        }
    }

def generate_applications_chart(config, start_date, end_date):
    """Génère un graphique des applications"""
    
    # Nombre de demandes par application
    queryset = CasDeTest.objects.all()
    
    # Filtrer par période si nécessaire
    if start_date or end_date:
        demande_filter = Q()
        if start_date:
            demande_filter &= Q(date_creation__gte=start_date)
        if end_date:
            demande_filter &= Q(date_creation__lte=end_date)
        queryset = queryset.filter(demande_filter)
    
    data = list(queryset.values('projet').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    labels = [item['projet'] for item in data]
    values = [item['count'] for item in data]
    
    return {
        'type': config['chart_type'],
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Nombre de demandes',
                'data': values,
                'backgroundColor': 'rgba(255, 193, 7, 0.8)',
                'borderColor': 'rgba(255, 193, 7, 1)',
                'borderWidth': 2
            }]
        }
    }

def generate_transferts_chart(config, start_date, end_date):
    """Génère un graphique des transferts"""
    
    from django.db import models
    
    queryset = CasDeTest.objects.all()
    
    if start_date:
        queryset = queryset.filter(date_creation__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_creation__lte=end_date)
    
    if config['groupby'] == 'test_state':
        data = list(queryset.values('test_state').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        labels = [item['test_state'] for item in data]
        values = [item['count'] for item in data]
    
    else:
        # Transferts par expert
        data = list(queryset.values(
            'profile'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        labels = [f"{item['profile']}" for item in data]
        values = [item['count'] for item in data]
    
    return {
        'type': config['chart_type'],
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Nombre de transferts',
                'data': values,
                'backgroundColor': 'rgba(156, 39, 176, 0.8)',
                'borderColor': 'rgba(156, 39, 176, 1)',
                'borderWidth': 2
            }]
        }
    }

def generate_priority_criticality_matrix():
    """
    Génère une matrice de priorité/criticité pour les cas de test.
    Retourne un dictionnaire avec les données formatées pour Chart.js
    """
    # Récupérer les données groupées par priorité et criticité
    from django.db.models import Count
    
    # Vérifier d'abord s'il y a des données
    total_cases = CasDeTest.objects.count()
    if total_cases == 0:
        return {
            'type': 'heatmap',
            'data': {
                'x': ['High', 'Medium', 'Low'],
                'y': ['High', 'Medium', 'Low'],
                'z': [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                'type': 'heatmap',
                'colorscale': [
                    [0, 'rgb(158, 202, 225)'],
                    [0.5, 'rgb(49, 130, 189)'],
                    [1, 'rgb(8, 48, 107)']
                ],
                'showscale': True
            },
            'layout': {
                'title': 'Matrice Priorité/Criticité (Aucune donnée trouvée)',
                'xaxis': {'title': 'Criticité'},
                'yaxis': {'title': 'Priorité'}
            }
        }
    
    # Créer une requête qui compte les cas par priorité et criticité
    priorities = ['High', 'Medium', 'Low']
    criticalities = ['High', 'Medium', 'Low']
    
    # Initialiser la matrice avec des zéros
    matrix = []
    for _ in priorities:
        matrix.append([0] * len(criticalities))
    
    # Récupérer les données de la base
    queryset = CasDeTest.objects.all()
    
    # Remplir la matrice avec les comptes
    for i, prio in enumerate(priorities):
        for j, crit in enumerate(criticalities):
            count = queryset.filter(prio=prio, criticality=crit).count()
            matrix[i][j] = count
    
    # Créer les données pour le graphique
    chart_data = {
        'type': 'heatmap',
        'data': {
            'x': criticalities,
            'y': priorities,
            'z': matrix,
            'type': 'heatmap',
            'colorscale': [
                [0, 'rgb(247, 251, 255)'],      # Blanc très clair
                [0.2, 'rgb(222, 235, 247)'],   # Bleu très clair
                [0.4, 'rgb(198, 219, 239)'],   # Bleu clair
                [0.6, 'rgb(158, 202, 225)'],   # Bleu moyen
                [0.8, 'rgb(107, 174, 214)'],   # Bleu foncé
                [1, 'rgb(49, 130, 189)']       # Bleu très foncé
            ],
            'showscale': True,
            'colorbar': {
                'title': {
                    'text': 'Nombre de cas',
                    'font': {'size': 14}
                },
                'thickness': 20,
                'len': 0.7
            },
            'hovertemplate': '<b>%{y}</b> priorité<br><b>%{x}</b> criticité<br><b>%{z}</b> cas de test<extra></extra>',
            'text': matrix,
            'texttemplate': '%{z}',
            'textfont': {
                'size': 16,
                'color': 'white',
                'family': 'Arial Black'
            }
        },
        'layout': {
            'title': {
                'text': 'Matrice Priorité/Criticité - Répartition des Cas de Test',
                'font': {'size': 18, 'color': '#2c3e50'},
                'x': 0.5
            },
            'xaxis': {
                'title': {
                    'text': 'Niveau de Criticité',
                    'font': {'size': 14, 'color': '#34495e'}
                },
                'tickfont': {'size': 12, 'color': '#2c3e50'},
                'side': 'bottom'
            },
            'yaxis': {
                'title': {
                    'text': 'Niveau de Priorité',
                    'font': {'size': 14, 'color': '#34495e'}
                },
                'tickfont': {'size': 12, 'color': '#2c3e50'}
            },
            'margin': {'l': 80, 'r': 100, 't': 80, 'b': 80},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font': {'family': 'Arial, sans-serif'}
        }
    }
    
    return chart_data

def generate_priority_chart():
    """
    Génère directement un graphique des priorités (similaire à la matrice)
    """
    try:
        # Récupérer les données directement depuis la base
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par priorité
        priority_data = list(CasDeTest.objects.values('prio').annotate(count=Count('id')).order_by('-count'))
        
        if not priority_data:
            # Données par défaut si la base est vide
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['prio'] for item in priority_data]
            values = [item['count'] for item in priority_data]
            # Couleurs pour les priorités
            color_map = {
                'High': '#e74c3c',    # Rouge
                'Medium': '#f39c12',  # Orange
                'Low': '#27ae60'      # Vert
            }
            colors = [color_map.get(label, '#3498db') for label in labels]
        
        # Construire les données Chart.js
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Priorité'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Nombre de cas'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Niveau de priorité'
                        }
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_priority_chart: {e}")
        # Graphique d'erreur
        return {
            'type': 'bar',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_project_chart():
    """
    Génère directement un graphique des projets
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par projet
        project_data = list(CasDeTest.objects.values('projet').annotate(count=Count('id')).order_by('-count'))
        
        if not project_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['projet'] for item in project_data]
            values = [item['count'] for item in project_data]
            # Couleurs variées pour les projets
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e'][:len(labels)]
        
        chart_data = {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Projet'
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_project_chart: {e}")
        return {
            'type': 'pie',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_status_chart():
    """
    Génère directement un graphique des statuts
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par statut
        status_data = list(CasDeTest.objects.values('test_state').annotate(count=Count('id')).order_by('-count'))
        
        if not status_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['test_state'] for item in status_data]
            values = [item['count'] for item in status_data]
            # Couleurs selon le statut
            color_map = {
                'OK': '#27ae60',           # Vert
                'KO': '#e74c3c',           # Rouge
                'In Progress': '#f39c12',  # Orange
                'Not Started': '#95a5a6',  # Gris
                'Blocked': '#8e44ad',      # Violet
                'N/A': '#34495e'           # Gris foncé
            }
            colors = [color_map.get(label, '#3498db') for label in labels]
        
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Statut'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Nombre de cas'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Statut du test'
                        }
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_status_chart: {e}")
        return {
            'type': 'bar',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_test_perimeter_chart():
    """
    Génère directement un graphique des périmètres de test
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par périmètre de test
        perimeter_data = list(CasDeTest.objects.values('test_perimeter').annotate(count=Count('id')).order_by('-count'))
        
        if not perimeter_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['test_perimeter'] for item in perimeter_data]
            values = [item['count'] for item in perimeter_data]
            # Couleurs variées pour les périmètres
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e'][:len(labels)]
        
        chart_data = {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Périmètre'
                    },
                    'legend': {
                        'position': 'right'
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_test_perimeter_chart: {e}")
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_test_states_chart():
    """
    Génère directement un graphique des états des tests
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par état de test
        states_data = list(CasDeTest.objects.values('test_state').annotate(count=Count('id')).order_by('test_state'))
        
        if not states_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['test_state'] for item in states_data]
            values = [item['count'] for item in states_data]
            # Couleurs selon l'état
            color_map = {
                'OK': '#27ae60',           # Vert
                'KO': '#e74c3c',           # Rouge
                'KO JDD': '#c0392b',       # Rouge foncé
                'In Progress': '#f39c12',  # Orange
                'Not Started': '#95a5a6',  # Gris
                'Blocked': '#8e44ad',      # Violet
                'N/A': '#34495e'           # Gris foncé
            }
            colors = [color_map.get(label, '#3498db') for label in labels]
        
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par État'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Nombre de cas'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'État du test'
                        }
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_test_states_chart: {e}")
        return {
            'type': 'bar',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_profile_chart():
    """
    Génère directement un graphique des profils utilisateurs
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par profil
        profile_data = list(CasDeTest.objects.values('profile').annotate(count=Count('id')).order_by('-count'))
        
        if not profile_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['profile'] for item in profile_data]
            values = [item['count'] for item in profile_data]
            # Couleurs pour les profils
            colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'][:len(labels)]
        
        chart_data = {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Profil'
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_profile_chart: {e}")
        return {
            'type': 'pie',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

def generate_criticality_chart():
    """
    Génère directement un graphique des niveaux de criticité
    """
    try:
        from django.db.models import Count
        from .models import CasDeTest
        
        # Compter les cas par criticité
        criticality_data = list(CasDeTest.objects.values('criticality').annotate(count=Count('id')).order_by('criticality'))
        
        if not criticality_data:
            labels = ['Aucune donnée']
            values = [0]
            colors = ['#ff6b6b']
        else:
            labels = [item['criticality'] for item in criticality_data]
            values = [item['count'] for item in criticality_data]
            # Couleurs pour les criticités
            color_map = {
                'High': '#e74c3c',    # Rouge
                'Medium': '#f39c12',  # Orange
                'Low': '#27ae60'      # Vert
            }
            colors = [color_map.get(label, '#3498db') for label in labels]
        
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre de cas de test',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Répartition des Cas de Test par Criticité'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Nombre de cas'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Niveau de criticité'
                        }
                    }
                }
            }
        }
        
        return chart_data
        
    except Exception as e:
        print(f"Erreur dans generate_criticality_chart: {e}")
        return {
            'type': 'bar',
            'data': {
                'labels': ['Erreur'],
                'datasets': [{
                    'label': 'Erreur de génération',
                    'data': [0],
                    'backgroundColor': ['#ff6b6b']
                }]
            }
        }

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models.functions import Concat
from django.db.models import Value, CharField, Count, Q, F
from .models import CasDeTest
import uuid

@csrf_exempt
def analyze_command(request):
    """Analyse une commande utilisateur et retourne une réponse"""
    if request.method == 'POST':
        try:
            # Vérifier le type de contenu
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    user_input = data.get('text', '').strip()
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            else:  # format x-www-form-urlencoded
                user_input = request.POST.get('text', '').strip()
            
            if not user_input:
                return JsonResponse({'error': 'No input provided'}, status=400)
            
            # Construire la réponse de base
            response_data = {
                'result': f"Commande reçue : {user_input}",
                'suggestions': []
            }
            
            # Essayer d'ajouter des informations sur les cas de test
            try:
                test_cases = list(CasDeTest.objects.all()[:5].values('projet', 'marco_scenario', 'test_state'))
                if test_cases:
                    response_data['test_cases'] = test_cases
            except Exception as e:
                logger.warning(f"Erreur récupération cas de test: {str(e)}")
                # Ne pas échouer si on ne peut pas récupérer les cas de test
            
            return JsonResponse({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Erreur analyse commande: {str(e)}", exc_info=True)
            return JsonResponse(
                {'error': 'Une erreur est survenue lors du traitement de votre demande'}, 
                status=500
            )
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def get_conversation_history(request):
    """Récupère l'historique d'une conversation"""
    if request.method == "GET":
        conversation_id = request.GET.get("conversation_id")
        if conversation_id:
            historique = Historique.objects.filter(
                conversation_id=conversation_id
            ).order_by('date_requete').values(
                'requete', 'reponse', 'date_requete'
            )
            return JsonResponse({
                "history": list(historique),
                "conversation_id": conversation_id
            })
    return JsonResponse({"error": "ID de conversation requis"}, status=400)


@csrf_exempt
def chatbot_suggestions(request):
    """Fournit des suggestions de questions pour le chatbot"""
    suggestions = [
        "Combien de demandes au total ?",
        "Quelles sont les catégories de demandes les plus fréquentes ?",
        "Combien de demandes sont encore ouvertes ?",
        "Quel est le score moyen de satisfaction ?",
        "Quels sont les demandeurs les plus actifs ?",
        "Combien de demandes ont été transférées ?",
        "Quelles applications génèrent le plus de demandes ?",
        "Combien d'audits ont été réalisés ce mois ?",
        "Quel est le délai moyen de traitement ?",
        "Combien de demandes ont été refusées ?"
    ]
    
    return JsonResponse({"suggestions": suggestions})