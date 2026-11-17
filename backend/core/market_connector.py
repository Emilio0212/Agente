import os
import json
import requests
from typing import Any

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob-api.polymarket.com"

def buscar_mercados_polymarket(query: str = "USD", limit: int = 5) -> list[dict[str, Any]]:
    """Consulta mercados activos en Polymarket usando Gamma API (solo lectura pública)."""
    resp = requests.get(
        f"{GAMMA_URL}/markets",
        params={"active": "true", "closed": "false", "limit": 50},
        timeout=10,
    )
    resp.raise_for_status()
    mercados = resp.json()

    resultados = []
    q = query.lower()
    for m in mercados:
        pregunta = m.get("question", "")
        if q in pregunta.lower() or not query:
            precios = json.loads(m.get("outcomePrices", "[]"))
            tokens = json.loads(m.get("clobTokenIds", "[]"))
            resultados.append({
                "id": m.get("id"),
                "pregunta": pregunta,
                "probabilidad_yes": float(precios[0]) if len(precios) > 0 else None,
                "probabilidad_no": float(precios[1]) if len(precios) > 1 else None,
                "volumen_usd": round(float(m.get("volumeNum", 0)), 2),
                "liquidez_usd": round(float(m.get("liquidityNum", 0)), 2),
                "token_id_yes": tokens[0] if len(tokens) > 0 else None,
                "fecha_cierre": m.get("endDate"),
            })
        if len(resultados) >= limit:
            break
    return resultados

def obtener_orderbook_token(token_id: str) -> dict[str, Any]:
    """Obtiene el mejor bid/ask y midpoint del CLOB de Polymarket para un token específico."""
    resp = requests.get(f"{CLOB_URL}/book", params={"token_id": token_id}, timeout=10)
    resp.raise_for_status()
    book = resp.json()
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    mejor_bid = float(bids[0]["price"]) if bids else 0.0
    mejor_ask = float(asks[0]["price"]) if asks else 1.0
    return {
        "token_id": token_id,
        "mejor_bid": mejor_bid,
        "mejor_ask": mejor_ask,
        "spread": round(mejor_ask - mejor_bid, 4),
        "midpoint": round((mejor_bid + mejor_ask) / 2, 4),
    }

def ejecutar_orden_simulada_o_local(token_id: str, lado: str, monto_usdc: float, precio: float) -> dict[str, Any]:
    """
    Capa aislada de ejecución:
    - En v0.1.0 opera en modo simulación (paper trading) por defecto.
    - La llave privada se lee únicamente de os.getenv() en tiempo de ejecución y NUNCA entra al contexto del LLM.
    """
    modo_real = os.getenv("POLYMARKET_LIVE_TRADING", "false").lower() == "true"
    if not modo_real:
        return {
            "modo": "SIMULACION_V0_1",
            "estado": "ORDEN_REGISTRADA_LOCAL",
            "token_id": token_id,
            "lado": lado.upper(),
            "monto_usdc": monto_usdc,
            "precio_limite": precio,
            "acciones_estimadas": round(monto_usdc / precio, 2) if precio > 0 else 0,
        }

    # Ejecución real con py-clob-client (requiere POLYMARKET_PRIVATE_KEY en .env local)
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import OrderArgs, OrderType

    pk = os.getenv("POLYMARKET_PRIVATE_KEY")
    if not pk:
        raise RuntimeError("Falta POLYMARKET_PRIVATE_KEY en el archivo .env local.")

    client = ClobClient(CLOB_URL, key=pk, chain_id=137)  # Polygon Mainnet
    client.set_api_creds(client.create_or_derive_api_creds())
    order_args = OrderArgs(price=precio, size=round(monto_usdc / precio, 2), side=lado.upper(), token_id=token_id)
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order, OrderType.GTC)
    return {"modo": "LIVE_POLYGON", "respuesta_clob": resp}