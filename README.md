# Quant Trading Bot · v0.1.0

Agente autónomo de análisis y señalización cuantitativa impulsado por modelos de Deep Learning (PyTorch) y un LLM ejecutado 100 % en local.

## Versión
- **Versión actual:** `v0.1.0` (Entrega inicial: arquitectura base, inferencia de modelos entrenados y UI local).

## Tecnologías Aplicadas
- **Interfaz de Usuario (UI):** Vue 3, TypeScript, Vite.
- **Backend & API Local:** Python 3.11, FastAPI, Uvicorn.
- **Motor de IA / LLM Local:** Ollama (`qwen2.5:7b` / `llama3.1:8b`) con *Tool Calling* nativo (sin envío de datos ni llaves API a proveedores externos).
- **Modelos Cuantitativos:** PyTorch (`MLP`, `LSTM`, `CNN-1D`), Scikit-Learn (`StandardScaler`), Pandas, NumPy.
- **Mercados / Conectores:** Histórico auditado (`yfinance`) y adaptadores preparados para **MEXC** / **Polymarket**.

## Seguridad y Privacidad
- El sistema opera sin APIs externas de IA.
- Cualquier llave de exchange se gestiona exclusivamente mediante variables de entorno locales (`.env` excluido en `.gitignore`).