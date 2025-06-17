import sounddevice as sd
from scipy.io.wavfile import write
import uuid
import os

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Configurações IBM
API_KEY = 'sua_api_key_aqui'
URL = 'sua_url_aqui'

# Frase de segurança esperada
FRASE_SEGURA = "acesso autorizado"

def gravar_audio(duracao=5, arquivo_saida="voz.wav"):
    print("Gravando... fale agora!")
    fs = 44100  # taxa de amostragem
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()
    write(arquivo_saida, fs, audio)
    print("Gravação finalizada.")

def reconhecer_voz_ibm(arquivo):
    # Autenticador
    authenticator = IAMAuthenticator(API_KEY)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(URL)

    with open(arquivo, 'rb') as audio_file:
        response = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/wav',
            model='pt-BR_BroadbandModel'
        ).get_result()

    try:
        texto = response['results'][0]['alternatives'][0]['transcript']
        return texto.strip().lower()
    except:
        return None

def sistema_seguranca_por_voz():
    arquivo_temp = f"voz_{uuid.uuid4().hex}.wav"
    gravar_audio(5, arquivo_temp)

    texto_reconhecido = reconhecer_voz_ibm(arquivo_temp)
    os.remove(arquivo_temp)

    if texto_reconhecido:
        print(f"Você disse: {texto_reconhecido}")
        if FRASE_SEGURA in texto_reconhecido:
            print("✅ Acesso autorizado!")
        else:
            print("❌ Acesso negado. Frase não reconhecida.")
    else:
        print("⚠️ Não foi possível entender o áudio.")

if __name__ == "__main__":
    sistema_seguranca_por_voz()
