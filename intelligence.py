import fitz  # PyMuPDF
from docx import Document
import os
import sqlite3
import csv
import pandas as pd
import json

def extract_text(file_path):
    ext = file_path.split('.')[-1].lower()
    text = ""

    try:
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == "pdf":
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
        elif ext == "docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == "csv":
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    text += ', '.join(row) + "\n"
        elif ext == "xls" or ext == "xlsx":
            df = pd.read_excel(file_path)
            text = df.to_string(index=False)
        elif ext == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = json.dumps(data, indent=4)
        else:
            with open(file_path, "rb") as f:
                content = f.read()
                try:
                    text = content.decode("utf-8")
                except UnicodeDecodeError:
                    text = "[Contenu binaire non analysable directement]"
    except Exception as e:
        return f"Erreur d'extraction : {e}"

    return text


def charger_keywords_db():
    try:
        conn = sqlite3.connect("mots_sensibles.db")
        c = conn.cursor()
        c.execute("SELECT word FROM sensitive_words")
        mots = [row[0] for row in c.fetchall()]
        conn.close()
        return mots
    except Exception as e:
        print("❌ Erreur chargement DB mots clés:", e)
        return []


def analyse_contenu_sensible(file_path):
    try:
        text = extract_text(file_path)
        if text.startswith("Erreur d'extraction"):
            return False, text

        lower_text = text.lower()
        mots_cibles = charger_keywords_db()

        print("🧠 TEXTE ANALYSÉ (début):")
        print(text[:300])
        print("📚 Mots clés chargés:", mots_cibles)

        detections = [mot for mot in mots_cibles if mot in lower_text]
        print("📌 Mots détectés dans le texte:", detections)

        est_sensible = len(detections) > 0
        message = "Analyse locale uniquement\n"
        if est_sensible:
            message += f"✅ Données sensibles détectées\n🟡 Mots : {', '.join(detections)}"
        else:
            message += "❌ Aucun mot sensible détecté localement."

        return est_sensible, message

    except Exception as e:
        return False, f"Erreur lors de l'analyse : {e}"
