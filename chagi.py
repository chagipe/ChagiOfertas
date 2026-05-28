import os
import requests
import time
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

load_dotenv()

CSFLOAT_API_KEY = os.getenv("CSFLOAT_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DESCUENTO_MINIMO = int(os.getenv("DESCUENTO_MINIMO", "40"))
PRECIO_MINIMO = int(os.getenv("PRECIO_MINIMO", "10"))
TIEMPO_ESPERA = int(os.getenv("TIEMPO_ESPERA", "15"))
INTERVALO_LOTE = int(os.getenv("INTERVALO_LOTE", "600"))
MAX_LOTE = int(os.getenv("MAX_LOTE", "5"))
CSFLOAT_API_URL = "https://csfloat.com/api/v1/listings"

if not CSFLOAT_API_KEY:
    print("[ERROR] CSFLOAT_API_KEY no está configurada.")
    sys.exit(1)

if not DISCORD_WEBHOOK_URL:
    print("[ERROR] DISCORD_WEBHOOK_URL no está configurada.")
    sys.exit(1)

print(f"[CONFIG] Descuento mínimo: {DESCUENTO_MINIMO}% | Precio mínimo: ${PRECIO_MINIMO} | Lote cada {INTERVALO_LOTE}s (max {MAX_LOTE})")

HEADERS = {
    "Authorization": CSFLOAT_API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "ChagiOfertas/1.0"
}


# =============================================================================
# CONSULTAR TODOS LOS LISTADOS (paginación por cursor)
# =============================================================================

def obtener_listados():
    todos = []
    cursor = None
    pagina = 0

    while True:
        params = {
            "type": "buy_now",
            "limit": 50,
            "sort_by": "highest_discount"
        }
        if cursor:
            params["cursor"] = cursor

        exito = False
        for intento in range(5):
            try:
                r = requests.get(CSFLOAT_API_URL, headers=HEADERS, params=params, timeout=30)

                if r.status_code == 429:
                    espera = 30 * (intento + 1)
                    print(f"[429] Rate limit ({intento+1}/5). Esperando {espera}s...")
                    time.sleep(espera)
                    continue

                r.raise_for_status()
                datos = r.json()
                listados = datos.get("data", [])
                todos.extend(listados)
                pagina += 1

                cursor = datos.get("cursor")
                if not cursor:
                    print(f"[OK] {len(todos)} listados obtenidos ({pagina} páginas).")
                    return todos

                print(f"  Página {pagina}: {len(listados)} items (total: {len(todos)})")
                exito = True
                break

            except requests.exceptions.Timeout:
                print("  [ERROR] Timeout.")
            except requests.exceptions.ConnectionError:
                print("  [ERROR] Conexión fallida.")
            except requests.exceptions.HTTPError as e:
                print(f"  [ERROR] HTTP {r.status_code}: {e}")
                return todos
            except json.JSONDecodeError:
                print("  [ERROR] Respuesta no es JSON.")
                return todos
            except Exception as e:
                print(f"  [ERROR] {e}")
                return todos

            time.sleep(10)

        if not exito:
            print(f"  [ERROR] No se pudo obtener página {pagina+1}.")
            return todos

        time.sleep(0.3)


# =============================================================================
# EXTRAER DESCUENTO (% real contra precio de mercado)
# =============================================================================

def extraer_descuento(item):
    """
    Calcula el descuento real comparando el precio del listado
    contra el precio de referencia (predicted_price) de la API.

    También expone max_offer_discount (en basis points, ej: 800 = 8%).
    """
    precio_listado = item.get("price", 0)
    ref = item.get("reference")

    if ref and isinstance(ref, dict):
        precio_ref = ref.get("predicted_price") or ref.get("base_price") or 0
        if precio_ref > 0 and precio_listado > 0:
            return round((1 - precio_listado / precio_ref) * 100, 2)

    d = item.get("max_offer_discount")
    if d is not None:
        d = float(d)
        if d > 100:
            d = d / 100
        return round(d, 2)

    return 0.0


# =============================================================================
# FILTRAR OFERTAS
# =============================================================================

def filtrar_ofertas(listados):
    ofertas = []

    for item in listados:
        if item.get("type") != "buy_now":
            continue

        precio_cents = item.get("price", 0)
        if precio_cents < PRECIO_MINIMO * 100:
            continue

        d = extraer_descuento(item)
        if d < DESCUENTO_MINIMO:
            continue

        ofertas.append(item)

    return ofertas


# =============================================================================
# FORMATEAR PRECIO
# =============================================================================

def fmt_precio(cents):
    return round(float(cents) / 100, 2)


# =============================================================================
# CREAR EMBED PARA DISCORD
# =============================================================================

def crear_embed(item, indice=None):
    datos_item = item.get("item", {})
    nombre = datos_item.get("market_hash_name") or item.get("market_hash_name", "Desconocido")
    precio = fmt_precio(item.get("price", 0))
    descuento = extraer_descuento(item)
    float_val = datos_item.get("float_value") or item.get("float_value", "N/A")
    list_id = item.get("id", "")
    enlace = f"https://csfloat.com/item/{list_id}"

    color = 0xFF0000 if descuento >= 70 else (0xFFA500 if descuento >= 55 else 0x00FF00)

    titulo = f"#{indice} 🔥 {nombre[:236]}" if indice else f"🔥 {nombre[:240]}"

    return {
        "title": titulo,
        "url": enlace,
        "color": color,
        "fields": [
            {"name": "💰 Precio", "value": f"${precio:,.2f} USD", "inline": True},
            {"name": "📉 Descuento", "value": f"**{descuento:.1f}%**", "inline": True},
            {"name": "🎯 Float", "value": f"{float_val}" if float_val != "N/A" else "N/A", "inline": True}
        ],
        "footer": {"text": f"ChagiOfertas • {datetime.now().strftime('%H:%M:%S')}"}
    }


# =============================================================================
# ENVIAR LOTE DE OFERTAS A DISCORD
# =============================================================================

def enviar_lote(ofertas):
    if not ofertas:
        return

    embeds = [crear_embed(item, i+1) for i, item in enumerate(ofertas)]
    payload = {"username": "ChagiOfertas", "embeds": embeds}

    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=15)
        r.raise_for_status()
        print(f"[DISCORD] ✅ Lote enviado: {len(ofertas)} ofertas")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[DISCORD] Error al enviar lote: {e}")
        return False


# =============================================================================
# BUCLE PRINCIPAL
# =============================================================================

def bucle_principal():
    print("=" * 50)
    print("  ChagiOfertas - Monitor CSFloat")
    print(f"  Descuento mínimo: {DESCUENTO_MINIMO}%")
    print(f"  Lote cada {INTERVALO_LOTE}s (max {MAX_LOTE})")
    print("=" * 50)
    print()

    notificados = cargar_notificados()
    buffer = []
    ultimo_envio = time.time()
    print(f"[RESTORE] {len(notificados)} IDs cargados del historial.")
    print()

    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Consultando...")

            listados = obtener_listados()
            if not listados:
                time.sleep(TIEMPO_ESPERA)
                continue

            ofertas = filtrar_ofertas(listados)
            print(f"[FILTRO] {len(ofertas)} ofertas >= {DESCUENTO_MINIMO}%")

            for item in ofertas:
                item_id = item.get("id", "")
                if item_id not in notificados:
                    buffer.append(item)
                    notificados.add(item_id)

            ahora = time.time()
            if ahora - ultimo_envio >= INTERVALO_LOTE:
                lote = buffer[:MAX_LOTE]
                buffer = buffer[MAX_LOTE:]
                enviar_lote(lote)
                guardar_notificados(notificados)
                ultimo_envio = ahora

            if buffer:
                prox = int(INTERVALO_LOTE - (ahora - ultimo_envio))
                print(f"[BUFFER] {len(buffer)} ofertas esperando | próximo lote en {prox}s")

            print(f"[SLEEP] {TIEMPO_ESPERA}s...\n")
            time.sleep(TIEMPO_ESPERA)

        except KeyboardInterrupt:
            print("\n[!] Detenido.")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(TIEMPO_ESPERA)


# =============================================================================
# PERSISTENCIA DE IDs NOTIFICADOS
# =============================================================================

ARCHIVO_NOTIFICADOS = "notificados.json"

def cargar_notificados():
    if not os.path.exists(ARCHIVO_NOTIFICADOS):
        return set()
    try:
        with open(ARCHIVO_NOTIFICADOS, "r") as f:
            datos = json.load(f)
            return set(datos)
    except Exception as e:
        print(f"[WARN] No se pudo cargar {ARCHIVO_NOTIFICADOS}: {e}")
        return set()

def guardar_notificados(ids):
    try:
        with open(ARCHIVO_NOTIFICADOS, "w") as f:
            json.dump(list(ids), f)
    except Exception as e:
        print(f"[WARN] No se pudo guardar {ARCHIVO_NOTIFICADOS}: {e}")


if __name__ == "__main__":
    bucle_principal()
