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
import matplotlib.pyplot as plt
from django.db.models import Value, CharField
from django.db.models.functions import Concat


# Langchain / IA
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_openai import OpenAI  # optionnel si besoin d'OpenAI

# Modèles Django personnalisés
from .models import Demande, Responsable, Historique, Application, Transfert, Audit, Satisfaction

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
            # Initialiser le LLM Mistral
            llm = ChatMistralAI(
                model="mistral-large-latest",
                mistral_api_key="djGxrn5IJfal6irntxLpfaL2mq8qcRj2"
            )
            
            # Analyser la requête avec Mistral AI
            chart_config = analyze_chart_request(llm, user_query)
            
            if chart_config.get('error'):
                return JsonResponse({'error': chart_config['error']})
            
            # Générer les données selon le type de graphique demandé
            chart_data = generate_chart_data(chart_config)
            
            return JsonResponse({
                'success': True,
                'chart_data': chart_data,
                'title': chart_config.get('title', 'Graphique ALTEN'),
                'description': chart_config.get('description', ''),
                'query_analysis': chart_config
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

    BASE DE DONNÉES DISPONIBLE:
    - Demande: référence, application, date_ouverture, date_fermeture, catégorie, orientation, demandeur
    - Application: nom_application, périmètre  
    - Audit: résultat_audit, date_audit, auditeur
    - Satisfaction: score (1-10)
    - Transfert: date_transfert, expert, support
    - Responsable: identifiant, nom, prénom

    REQUÊTE UTILISATEUR: "{user_query}"
    
    Réponds UNIQUEMENT avec un JSON valide contenant:
    {{
        "chart_type": "bar|line|pie|doughnut|radar",
        "data_source": "demandes|applications|audits|satisfaction|transferts",
        "groupby": "mois|année|semaine|catégorie|application|orientation|auditeur",
        "metric": "count|average|sum",
        "time_period": "1_mois|3_mois|6_mois|1_an|tout",
        "title": "Titre du graphique",
        "description": "Description courte",
        "filters": {{}},
        "x_label": "Label axe X",
        "y_label": "Label axe Y"
    }}
    
    Exemples:
    - "graphique des demandes par mois" → chart_type: "bar", data_source: "demandes", groupby: "mois"
    - "évolution des scores de satisfaction" → chart_type: "line", data_source: "satisfaction", groupby: "mois"
    - "répartition par catégorie" → chart_type: "pie", data_source: "demandes", groupby: "catégorie"
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
        config['data_source'] = config.get('data_source', 'demandes')
        config['groupby'] = config.get('groupby', 'mois')
        config['metric'] = config.get('metric', 'count')
        config['time_period'] = config.get('time_period', '6_mois')
        
        return config
        
    except json.JSONDecodeError as e:
        return {'error': f'Erreur de parsing JSON: {str(e)}'}
    except Exception as e:
        return {'error': f'Erreur d\'analyse IA: {str(e)}'}

def generate_chart_data(config):
    """
    Génère les données du graphique selon la configuration
    """
    
    data_source = config['data_source']
    chart_type = config['chart_type']
    groupby = config['groupby']
    metric = config['metric']
    time_period = config['time_period']
    
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
    
    queryset = Demande.objects.all()
    
    # Filtrer par période si définie
    if start_date:
        queryset = queryset.filter(date_ouverture__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_ouverture__lte=end_date)
    
    groupby = config['groupby']
    chart_type = config['chart_type']
    
    if groupby == 'mois':
        data = list(queryset.annotate(
            periode=TruncMonth('date_ouverture')
        ).values('periode').annotate(
            count=Count('reference_demande')
        ).order_by('periode'))
        
        labels = [item['periode'].strftime('%Y-%m') for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'année':
        data = list(queryset.annotate(
            periode=TruncYear('date_ouverture')
        ).values('periode').annotate(
            count=Count('reference_demande')
        ).order_by('periode'))
        
        labels = [item['periode'].strftime('%Y') for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'catégorie':
        data = list(queryset.values('categorie').annotate(
            count=Count('reference_demande')
        ).order_by('-count'))
        
        labels = [item['categorie'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'orientation':
        data = list(queryset.values('orientation').annotate(
            count=Count('reference_demande')
        ).order_by('-count'))
        
        labels = [item['orientation'] for item in data]
        values = [item['count'] for item in data]
        
    elif groupby == 'application':
        data = list(queryset.values('application__nom_application').annotate(
            count=Count('reference_demande')
        ).order_by('-count')[:10])  # Top 10
        
        labels = [item['application__nom_application'] for item in data]
        values = [item['count'] for item in data]
        
    else:
        # Par défaut: comptage mensuel
        data = list(queryset.annotate(
            periode=TruncMonth('date_ouverture')
        ).values('periode').annotate(
            count=Count('reference_demande')
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
    
    queryset = Audit.objects.all()
    
    if start_date:
        queryset = queryset.filter(date_audit__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_audit__lte=end_date)
    
    groupby = config['groupby']
    metric = config['metric']
    
    if groupby == 'mois':
        if metric == 'average':
            data = list(queryset.annotate(
                periode=TruncMonth('date_audit')
            ).values('periode').annotate(
                avg_result=models.Avg('resultat_audit')
            ).order_by('periode'))
            
            labels = [item['periode'].strftime('%Y-%m') for item in data]
            values = [round(item['avg_result'], 2) if item['avg_result'] else 0 for item in data]
        else:
            data = list(queryset.annotate(
                periode=TruncMonth('date_audit')
            ).values('periode').annotate(
                count=Count('id')
            ).order_by('periode'))
            
            labels = [item['periode'].strftime('%Y-%m') for item in data]
            values = [item['count'] for item in data]
    
    elif groupby == 'auditeur':
        data = list(queryset.values('identifiant_audit__nom', 'identifiant_audit__prenom').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        labels = [f"{item['identifiant_audit__prenom']} {item['identifiant_audit__nom']}" for item in data]
        values = [item['count'] for item in data]
    
    else:
        # Répartition des résultats d'audit
        data = list(queryset.values('resultat_audit').annotate(
            count=Count('id')
        ).order_by('resultat_audit'))
        
        labels = [f"Résultat {item['resultat_audit']}" for item in data]
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
    """Génère un graphique des scores de satisfaction"""
    
    queryset = Satisfaction.objects.all()
    
    # Joindre avec les dates des demandes pour le filtrage temporel
    if start_date or end_date:
        demande_filter = Q()
        if start_date:
            demande_filter &= Q(ref_demande__date_ouverture__gte=start_date)
        if end_date:
            demande_filter &= Q(ref_demande__date_ouverture__lte=end_date)
        queryset = queryset.filter(demande_filter)
    
    if config['groupby'] == 'mois':
        data = list(queryset.annotate(
            periode=TruncMonth('ref_demande__date_ouverture')
        ).values('periode').annotate(
            avg_score=models.Avg('score')
        ).order_by('periode'))
        
        labels = [item['periode'].strftime('%Y-%m') for item in data]
        values = [round(item['avg_score'], 2) if item['avg_score'] else 0 for item in data]
    
    else:
        # Distribution des scores
        data = list(queryset.values('score').annotate(
            count=Count('id')
        ).order_by('score'))
        
        labels = [f"Score {item['score']}" for item in data]
        values = [item['count'] for item in data]
    
    return {
        'type': config['chart_type'],
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Score de satisfaction',
                'data': values,
                'backgroundColor': 'rgba(76, 175, 80, 0.8)',
                'borderColor': 'rgba(76, 175, 80, 1)',
                'borderWidth': 2
            }]
        }
    }

def generate_applications_chart(config, start_date, end_date):
    """Génère un graphique des applications"""
    
    # Nombre de demandes par application
    queryset = Application.objects.annotate(
        nb_demandes=Count('demandes')
    ).order_by('-nb_demandes')
    
    # Filtrer par période si nécessaire
    if start_date or end_date:
        demande_filter = Q()
        if start_date:
            demande_filter &= Q(demandes__date_ouverture__gte=start_date)
        if end_date:
            demande_filter &= Q(demandes__date_ouverture__lte=end_date)
        queryset = queryset.filter(demande_filter).annotate(
            nb_demandes=Count('demandes', filter=demande_filter)
        )
    
    data = list(queryset.values('nom_application', 'nb_demandes')[:10])
    
    labels = [item['nom_application'] for item in data]
    values = [item['nb_demandes'] for item in data]
    
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
    
    queryset = Transfert.objects.all()
    
    if start_date:
        queryset = queryset.filter(date_transfert__gte=start_date)
    if end_date:
        queryset = queryset.filter(date_transfert__lte=end_date)
    
    if config['groupby'] == 'mois':
        data = list(queryset.annotate(
            periode=TruncMonth('date_transfert')
        ).values('periode').annotate(
            count=Count('id')
        ).order_by('periode'))
        
        labels = [item['periode'].strftime('%Y-%m') for item in data]
        values = [item['count'] for item in data]
    
    else:
        # Transferts par expert
        data = list(queryset.values(
            'identifiant_expert__nom', 
            'identifiant_expert__prenom'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        labels = [f"{item['identifiant_expert__prenom']} {item['identifiant_expert__nom']}" 
                 if item['identifiant_expert__nom'] else 'Non assigné' for item in data]
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


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models.functions import Concat
from django.db.models import Value, CharField, Count, Q, F
from .models import Responsable, Historique
import uuid

@csrf_exempt
def analyze_command(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        conversation_id = request.POST.get("conversation_id")
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            colonnes = ["nom_complet", "nombre_demandes"]

            demandeurs = Responsable.objects.annotate(
                nom_complet_val=Concat(
                    F('prenom'), Value(' '), F('nom'),
                    output_field=CharField()
                ),
                nombre_demandes_count=Count(
                    'demandes',
                    filter=Q(demandes__date_ouverture__year=2024)
                )
            ).filter(
                nombre_demandes_count__gt=0
            ).values(
                'nom_complet_val', 'nombre_demandes_count'
            )[:10]

            resultat = list(demandeurs)

            return JsonResponse({
                "result": resultat,
                "is_table": True,
                "columns": colonnes,
                "conversation_id": conversation_id,
                "status": "success"
            })

        except Exception as e:
            error_message = f"Erreur d'analyse: {str(e)}"
            Historique.objects.create(
                requete=text,
                reponse=error_message,
                conversation_id=conversation_id
            )
            return JsonResponse({
                "error": error_message,
                "conversation_id": conversation_id
            }, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

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