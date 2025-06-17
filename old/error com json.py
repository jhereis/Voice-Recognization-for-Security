# 📦 Importações
import sounddevice as sd
from scipy.io.wavfile import write
import librosa
import numpy as np
import uuid
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# 🔑 IBM Watson - Coloque sua chave
API_KEY = "sua-api-key-aqui"
URL = "sua-url-aqui"

authenticator = IAMAuthenticator(API_KEY)
stt = SpeechToTextV1(authenticator=authenticator)
stt.set_service_url(URL)

# 🎤 Função para gravar áudio
def gravar_audio(duracao, arquivo):
    fs = 44100
    print("🎙️ Gravando...")
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()
    write(arquivo, fs, audio)
    print(f"✅ Gravação salva: {arquivo}")

# 🧠 Transcrição de voz
def reconhecer_voz_ibm(arquivo):
    with open(arquivo, 'rb') as audio_file:
        resposta = stt.recognize(
            audio=audio_file,
            content_type='audio/wav',
            model='pt-BR_BroadbandModel'
        ).get_result()
    try:
        texto = resposta['results'][0]['alternatives'][0]['transcript']
        return texto
    except (IndexError, KeyError):
        return ""

# 😠 Detecção de emoção por palavra-chave
def extrair_emocao(texto):
    texto = texto.lower()
    if "medo" in texto or "assustado" in texto or "pânico" in texto:
        return "medo"
    elif "raiva" in texto or "ódio" in texto or "irritado" in texto:
        return "raiva"
    elif "feliz" in texto or "alegre" in texto or "contente" in texto:
        return "alegria"
    elif "triste" in texto or "deprimido" in texto or "chorar" in texto:
        return "tristeza"
    else:
        return "neutro"

# 💾 Salvar feedback em CSV e JSON
def salvar_feedback(texto, emocao_detectada, emocao_corrigida):
    nova_linha = {
        "frase": texto,
        "emocao_detectada": emocao_detectada,
        "emocao_corrigida": emocao_corrigida
    }

    # CSV
    arquivo_csv = "feedback.csv"
    if os.path.exists(arquivo_csv):
        df = pd.read_csv(arquivo_csv)
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    else:
        df = pd.DataFrame([nova_linha])
    df.to_csv(arquivo_csv, index=False)

    # JSON
    arquivo_json = "feedback.json"
    if os.path.exists(arquivo_json):
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    else:
        dados = []
    dados.append(nova_linha)
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# 📊 Gráfico e análise de erros
def mostrar_analise_feedback():
    if not os.path.exists("feedback.csv"):
        print("⚠️ Nenhum feedback registrado ainda.")
        return

    df = pd.read_csv("feedback.csv")
    erros = df[df["emocao_corrigida"].notnull() & (df["emocao_corrigida"] != "") & (df["emocao_detectada"] != df["emocao_corrigida"])]

    if erros.empty:
        print("✅ Nenhum erro de detecção identificado.")
    else:
        print(f"🔎 Foram encontrados {len(erros)} casos de erro na detecção de emoção.")
        print(erros[["frase", "emocao_detectada", "emocao_corrigida"]])

        plt.figure(figsize=(10, 6))
        sns.countplot(data=erros, x="emocao_detectada", hue="emocao_corrigida")
        plt.title("Erros de Detecção de Emoção")
        plt.xlabel("Emoção Detectada")
        plt.ylabel("Ocorrências de Correção")
        plt.legend(title="Emoção Corrigida")
        plt.tight_layout()
        plt.show()

# 🔐 Sistema principal
def sistema_seguranca():
    nome_arquivo = f"voz_{uuid.uuid4().hex}.wav"
    gravar_audio(5, nome_arquivo)

    texto = reconhecer_voz_ibm(nome_arquivo)
    emocao_detectada = extrair_emocao(texto)

    print(f"\n🗣️ Texto reconhecido: {texto}")
    print(f"🧠 Emoção detectada: {emocao_detectada}")

    if emocao_detectada in ["medo", "tristeza"]:
        print("✅ Acesso autorizado.")
    else:
        print("❌ Acesso negado.")

    confirmacao = input("🔎 A emoção detectada estava correta? (sim/não): ").strip().lower()
    if confirmacao != "sim":
        emocao_corrigida = input("✏️ Qual era a emoção correta?: ").strip().lower()
    else:
        emocao_corrigida = ""

    salvar_feedback(texto, emocao_detectada, emocao_corrigida)
    mostrar_analise_feedback()

# ▶️ Rodar o sistema
sistema_seguranca()
