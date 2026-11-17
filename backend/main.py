# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.local_llm import consultar_agente_local, obtener_estado_senal

app = FastAPI(title="Quant Trading Bot Local", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mensaje: str
    modelo_dl: str = "lstm"

@app.get("/api/senal")
def get_senal(modelo: str = "lstm"):
    return obtener_estado_senal(modelo)

@app.post("/api/chat")
def post_chat(req: ChatRequest):
    respuesta = consultar_agente_local(req.mensaje, req.modelo_dl)
    return {"respuesta": respuesta}