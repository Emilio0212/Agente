import ollama
from core.market_connector import (
    buscar_mercados_polymarket,
    obtener_orderbook_token,
    ejecutar_orden_simulada_o_local,
)

MODELO_LOCAL = "qwen2.5:7b"

SYSTEM_PROMPT = """
Eres un Bot Cuantitativo v0.1.0 conectado a modelos locales de Deep Learning y a Polymarket.
Reglas estrictas:
1. Nunca solicites, imprimas ni menciones llaves privadas o credenciales API.
2. Usa las herramientas disponibles para consultar mercados reales en Polymarket, revisar el spread del orderbook
   y comparar la probabilidad implícita (precio YES) frente a nuestras señales cuantitativas.
3. Si el usuario pide operar, ejecuta la orden en modo simulación reportando precio límite, acciones estimadas y spread.
"""

HERRAMIENTAS_POLYMARKET = [
    buscar_mercados_polymarket,
    obtener_orderbook_token,
    ejecutar_orden_simulada_o_local,
]

MAPA_FN = {fn.__name__: fn for fn in HERRAMIENTAS_POLYMARKET}

def consultar_agente_local(mensaje_usuario: str) -> str:
    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mensaje_usuario},
    ]
    res = ollama.chat(model=MODELO_LOCAL, messages=mensajes, tools=HERRAMIENTAS_POLYMARKET)

    if res.message.tool_calls:
        mensajes.append(res.message)
        for call in res.message.tool_calls:
            fn = MAPA_FN[call.function.name]
            salida = fn(**call.function.arguments)
            mensajes.append({"role": "tool", "content": str(salida)})
        res_final = ollama.chat(model=MODELO_LOCAL, messages=mensajes)
        return res_final.message.content

    return res.message.content