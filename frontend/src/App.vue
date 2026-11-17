<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface SenalData {
  fecha_cierre_t: string
  ultimo_precio_close: number
  rendimiento_estimado_t1: number
  umbral_delta_congelado: number
  decision_operativa: string
  modelo_usado: string
}

interface Mensaje {
  rol: 'user' | 'bot'
  texto: string
}

const modeloSeleccionado = ref<'lstm' | 'mlp'>('lstm')
const senal = ref<SenalData | null>(null)
const mensajes = ref<Mensaje[]>([
  { rol: 'bot', texto: 'Bot v0.1.0 inicializado en entorno local (Ollama + PyTorch). Sin conexión a APIs externas de IA.' }
])
const inputUsuario = ref('')
const cargando = ref(false)

const cargarSenal = async () => {
  const res = await fetch(`http://localhost:8000/api/senal?modelo=${modeloSeleccionado.value}`)
  senal.value = await res.json()
}

const enviarMensaje = async () => {
  if (!inputUsuario.value.trim() || cargando.value) return
  const texto = inputUsuario.value
  mensajes.value.push({ rol: 'user', texto })
  inputUsuario.value = ''
  cargando.value = true

  try {
    const res = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensaje: texto, modelo_dl: modeloSeleccionado.value })
    })
    const data = await res.json()
    mensajes.value.push({ rol: 'bot', texto: data.respuesta })
  } finally {
    cargando.value = false
  }
}

onMounted(cargarSenal)
</script>

<template>
  <div class="layout">
    <header>
      <h1>Quant Trading Bot <span class="badge">v0.1.0</span></h1>
      <p>LLM Local (Ollama) · Deep Learning PyTorch · Sin API keys de terceros</p>
    </header>

    <main class="grid">
      <!-- Panel Izquierdo: Telemetría de Modelos -->
      <section class="card">
        <div class="card-header">
          <h2>Señal Cuantitativa</h2>
          <select v-model="modeloSeleccionado" @change="cargarSenal">
            <option value="lstm">LSTM (32 hidden)</option>
            <option value="mlp">MLP (64-32)</option>
          </select>
        </div>

        <div v-if="senal" class="metrics">
          <div class="metric">
            <span>Cierre ({{ senal.fecha_cierre_t }})</span>
            <strong>{{ senal.ultimo_precio_close }}</strong>
          </div>
          <div class="metric">
            <span>Pronóstico y<sub>t+1</sub></span>
            <strong>{{ (senal.rendimiento_estimado_t1 * 100).toFixed(4) }}%</strong>
          </div>
          <div class="metric">
            <span>Umbral δ (TR)</span>
            <strong>{{ (senal.umbral_delta_congelado * 100).toFixed(4) }}%</strong>
          </div>
          <div class="decision" :class="senal.decision_operativa.includes('COMPRAR') ? 'buy' : 'cash'">
            {{ senal.decision_operativa }}
          </div>
        </div>
      </section>

      <!-- Panel Derecho: Agente LLM Local -->
      <section class="card chat-box">
        <h2>Agente de Análisis Local</h2>
        <div class="messages">
          <div v-for="(m, i) in mensajes" :key="i" :class="['msg', m.rol]">
            {{ m.texto }}
          </div>
        </div>
        <form @submit.prevent="enviarMensaje" class="input-row">
          <input v-model="inputUsuario" placeholder="Consulta señal, simulación o métricas..." />
          <button type="submit" :disabled="cargando">{{ cargando ? '...' : 'Enviar' }}</button>
        </form>
      </section>
    </main>
  </div>
</template>

<style scoped>
.layout { max-width: 1100px; margin: 0 auto; padding: 1.5rem; font-family: system-ui, sans-serif; color: #e2e8f0; background: #0f172a; min-height: 100vh; }
.badge { background: #2563eb; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.9rem; }
.grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 1.5rem; margin-top: 1.5rem; }
.card { background: #1e293b; padding: 1.25rem; border-radius: 10px; border: 1px solid #334155; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.metrics { display: grid; gap: 0.8rem; }
.metric { display: flex; justify-content: space-between; padding: 0.6rem; background: #0f172a; border-radius: 6px; }
.decision { text-align: center; padding: 0.8rem; border-radius: 6px; font-weight: bold; margin-top: 0.5rem; }
.buy { background: #065f46; color: #6ee7b7; }
.cash { background: #334155; color: #cbd5e1; }
.chat-box { display: flex; flex-direction: column; height: 450px; }
.messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1rem; }
.msg { padding: 0.7rem; border-radius: 8px; max-width: 85%; line-height: 1.4; }
.user { align-self: flex-end; background: #2563eb; }
.bot { align-self: flex-start; background: #0f172a; border: 1px solid #334155; }
.input-row { display: flex; gap: 0.5rem; }
input { flex: 1; padding: 0.6rem; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; }
button { padding: 0.6rem 1.2rem; border-radius: 6px; border: none; background: #2563eb; color: white; cursor: pointer; }
</style>