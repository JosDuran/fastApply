from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer, util
from email.message import EmailMessage
import smtplib
import re
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Carga las variables del .env
load_dotenv()


GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MENSAJE_BASE = os.getenv("AUTOEMAIL_MENSAJE", "error .env vacio, setearlo")
PROFILE_PATH = os.getenv("PERFILES_PATH")
with open(PROFILE_PATH, "r", encoding="utf-8") as f:
    perfiles = json.load(f)


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- Modelo para seleccionar CV ---
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# --- Regex para correo ---
regex_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# --- Funciones ---
def seleccionar_cv(texto_convocatoria: str) -> str:
    emb_texto = model.encode(texto_convocatoria, convert_to_tensor=True)
    max_sim = -1
    seleccionado = None
    for perfil, info in perfiles.items():
        emb_perfil = model.encode(info["descripcion"], convert_to_tensor=True)
        sim = util.cos_sim(emb_texto, emb_perfil).item()
        if sim > max_sim:
            max_sim = sim
            seleccionado = info["archivo"]
    return seleccionado

def extraer_correo(texto: str) -> str:
    match = re.search(regex_email, texto)
    return match.group(0) if match else None

def guardar_csv(texto: str, cargo: str, correo: str):
    with open("dataset_entrenamiento.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), texto, cargo, correo])

def enviar_correo(destino: str, archivo_adjunto: str, cargo: str):
    msg = EmailMessage()
    msg['From'] = GMAIL_USER
    msg['To'] = destino
    msg['Subject'] = cargo or "Postulación a empleo"    
    msg.set_content(MENSAJE_BASE)
    with open(archivo_adjunto, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=archivo_adjunto.split('/')[-1])

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

# --- Rutas ---
@app.get("/", response_class=HTMLResponse)
async def formulario(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/previsualizar", response_class=HTMLResponse)
async def previsualizar(request: Request, texto_convocatoria: str = Form(...), cargo_manual: str = Form(...)):
    correo = extraer_correo(texto_convocatoria)
    archivo = seleccionar_cv(texto_convocatoria)

    # Guardamos CSV
    guardar_csv(texto_convocatoria, cargo_manual, correo)
    

# Si usaste \\n en .env, reemplaza para saltos de línea reales

    correo_preview = {
        "para": correo,
        "asunto": cargo_manual or "(Sin cargo detectado)",
        "mensaje": (MENSAJE_BASE
        ),
        "adjunto": archivo.split('/')[-1]
    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "preview": correo_preview,
        "texto_convocatoria": texto_convocatoria,
        "cargo_manual": cargo_manual
    })

@app.post("/enviar")
async def enviar(request: Request, texto_convocatoria: str = Form(...), cargo_manual: str = Form(...)):
    correo = extraer_correo(texto_convocatoria)
    archivo = seleccionar_cv(texto_convocatoria)

    if not correo:
        return {"status": "error", "mensaje": "No se encontró correo en la convocatoria"}

    try:
        enviar_correo(correo, archivo, cargo_manual)
        return {"status": "ok", "mensaje": f"Correo enviado a {correo} con {archivo.split('/')[-1]}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
