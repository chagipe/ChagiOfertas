
  /$$$$$$ /$$$$$$ /$$$$$$ /$$$$$$ /$$$$$$ /$$$$$$
 /$$__  $$|_  $$_/|_  $$_/|_  $$_/|_  $$_/| $$__  $$
| $$  \__/  | $$    | $$    | $$    | $$  | $$  \ $$
| $$ /$$$$  | $$    | $$    | $$    | $$  | $$$$$$$/
| $$|_  $$  | $$    | $$    | $$    | $$  | $$__  $$
| $$  \ $$  | $$    | $$    | $$    | $$  | $$  \ $$
|  $$$$$$/ /$$$$$$  | $$   /$$$$$$ /$$$$$$| $$  | $$
 \______/ |______/  |__/  |______/|______/|__/  |__/


<h1 align="center">🔥 ChagiOfertas — CSFloat Deal Hunter</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/CSFloat-API-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Discord-Webhook-5865F2?style=for-the-badge&logo=discord">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
</p>

<p align="center">
  <b>Bot inteligente que escanea CSFloat 24/7 en busca de ofertas con descuento 🚀</b><br>
  Detecta skins por debajo del precio de mercado y las envía a tu Discord al instante.
</p>

---

## ✨ Características

| 🔍 | Escaneo automático cada **15 segundos** con paginación completa |
|:--:|:--|
| 📉 | Calcula descuento real contra **precio de mercado** |
| 🧠 | **Buffer inteligente**: acumula ofertas y las envía en lotes |
| 💾 | **Persistencia**: no notifica dos veces el mismo item |
| 🎯 | Filtro configurable por **descuento mínimo** y **precio mínimo** |
| 🛡️ | Rate limit handling con retry automático |
| 🔗 | Embeds bonitos a Discord con precio, descuento y float |

---

## ⚙️ Cómo funciona

```
CSFloat API  ──▶  ChagiOfertas  ──▶  Discord Webhook
                     │
               ┌─────┴─────┐
               │  Buffer    │
               │  (cada 10  │
               │  min max 5)│
               └───────────┘
```

El bot:
1. Consulta todos los listados **buy_now** de CSFloat ordenados por mayor descuento
2. Calcula el descuento real contra el precio predicho por la API
3. Filtra solo las ofertas que superan tu umbral configurado
4. Las acumula en un buffer y las envía en lotes a tu Discord

---

## 🚀 Instalación

```bash
# 1. Clona el repo
git clone https://github.com/tu-usuario/ChagiOfertas.git
cd ChagiOfertas

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Configura las variables de entorno
cp .env.example .env
# Edita .env con tu API key y webhook

# 4. Ejecuta
python chagi.py
```

---

## 📁 Configuración (` .env`)

| Variable | Descripción | Default |
|:---------|:------------|:-------:|
| `CSFLOAT_API_KEY` | Tu API key de [CSFloat](https://csfloat.com/developer) | — |
| `DISCORD_WEBHOOK_URL` | URL del webhook de Discord | — |
| `DESCUENTO_MINIMO` | Descuento mínimo para notificar (%) | `40` |
| `PRECIO_MINIMO` | Precio mínimo en USD | `10` |
| `TIEMPO_ESPERA` | Segundos entre cada ciclo | `15` |
| `INTERVALO_LOTE` | Segundos entre lotes a Discord | `600` |
| `MAX_LOTE` | Máximo de ofertas por lote | `5` |

---

## 📦 Dependencias

```
requests
python-dotenv
```

---

## 🖼️ Ejemplo de salida en Discord

```
╔══════════════════════════════════════╗
║  #1 🔥 AK-47 | Redline (Field-Tested) ║
║  💰 $15.20 USD  📉 -65.3%  🎯 0.18   ║
╚══════════════════════════════════════╝
```

Cada embed incluye:
- Nombre del item con enlace directo a CSFloat
- Precio actual en USD
- Porcentaje de descuento (verde ≥40%, naranja ≥55%, rojo ≥70%)
- Float value del skin

---

## 📊 Dashboard visual

```
📈 Estadísticas en consola:
──────────────────────────────────────────────────
[CONFIG] Descuento mínimo: 40% | Precio mínimo: $10
[OK] 1250 listados obtenidos (25 páginas).
[FILTRO] 8 ofertas >= 40%
[BUFFER] 3 ofertas esperando | próximo lote en 420s
[DISCORD] ✅ Lote enviado: 5 ofertas
```

---

<p align="center">
  Made with ❤️ and 🥟 by <b>Chagi</b><br>
  <sub>CSFloat no está afiliado ni respalda este proyecto.</sub>
</p>
