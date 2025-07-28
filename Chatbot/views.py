from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import logging
from datetime import datetime, date
import numpy as np
import matplotlib.pyplot as plt
import io, base64
from langchain_openai import OpenAI  # Si tu veux aussi utiliser OpenAI
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'chatbot.html')


@csrf_exempt
def generate_graph(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('fileInput')
        command = request.POST.get('command')

        if not excel_file or not command:
            return JsonResponse({'status': 'error', 'message': 'Fichier ou commande manquant.'})

        if hasattr(excel_file, 'seek'):
            excel_file.seek(0)
        file_name = excel_file.name.lower()

        try:
            if file_name.endswith('.csv'):
                try:
                    df = pd.read_csv(excel_file)
                except UnicodeDecodeError:
                    excel_file.seek(0)
                    df = pd.read_csv(excel_file, encoding='latin1')
                sheet_name = 'csv'
            elif file_name.endswith(('.xlsx', '.xlsm')):
                xls = pd.ExcelFile(excel_file, engine='openpyxl')
                sheet_name = xls.sheet_names[0]
                for name in xls.sheet_names:
                    if name.lower() in command.lower():
                        sheet_name = name
                        break
                df = pd.read_excel(xls, sheet_name=sheet_name, nrows=5000)
            elif file_name.endswith('.xls'):
                xls = pd.ExcelFile(excel_file, engine='xlrd')
                sheet_name = xls.sheet_names[0]
                for name in xls.sheet_names:
                    if name.lower() in command.lower():
                        sheet_name = name
                        break
                df = pd.read_excel(xls, sheet_name=sheet_name, nrows=5000)
            else:
                return JsonResponse({'status': 'error', 'message': 'Format de fichier non supporté. Veuillez fournir un fichier .csv, .xlsx ou .xls.'})

            cmd = command.lower()
            if "barre" in cmd:
                ax = df.plot(kind='bar')
            elif "courbe" in cmd or "line" in cmd:
                ax = df.plot(kind='line')
            elif "secteur" in cmd or "pie" in cmd:
                df.iloc[:, 0].value_counts().plot.pie(autopct='%1.1f%%')
            elif "histogramme" in cmd:
                ax = df.plot(kind='hist')
            else:
                ax = df.plot()

            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')

            return JsonResponse({'status': 'success', 'image': image_base64, 'sheet': sheet_name})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'})

@csrf_exempt
def analyze_command(request):
    if request.method == "POST":
        text = request.POST.get("text", "")

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key="AIzaSyDrefO2vmE1AFx1cvRRDMK9_nKxedu3EXE"
            )

            # Prompt pour une réponse simple et directe
            prompt = (
                "Réponds uniquement à la question suivante de façon concise et directe, sans explication ni justification. "
                "Si la réponse est un mot ou une phrase, donne uniquement ce mot ou cette phrase.\n"
                f"Question : {text}"
            )
            result = llm.invoke(prompt)

            content = getattr(result, 'content', None)
            if content:
                return JsonResponse({"result": content})
            return JsonResponse({"result": str(result)})
        except Exception as e:
            return JsonResponse({"error": f"Erreur d'analyse: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
