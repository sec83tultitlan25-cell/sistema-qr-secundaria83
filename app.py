from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = "secundaria83_qr_2026"

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")


@app.route("/", methods=["GET"])
def inicio():
    return "Sistema QR Secundaria 83 funcionando", 200


@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Token de verificacion incorrecto", 403


@app.route("/webhook", methods=["POST"])
def recibir_webhook():
    datos = request.get_json(silent=True)
    print("Webhook recibido:", datos)
    return jsonify({"status": "ok"}), 200


@app.route("/enviar-prueba", methods=["GET"])
def enviar_prueba():

    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return jsonify({
            "error": "Faltan variables de entorno de WhatsApp"
        }), 500

    numero_destino = "525534935142"

    url = (
        f"https://graph.facebook.com/v24.0/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    mensaje = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }

    respuesta = requests.post(
        url,
        headers=headers,
        json=mensaje,
        timeout=20
    )

    return jsonify({
        "status_code": respuesta.status_code,
        "respuesta_meta": respuesta.json()
    }), respuesta.status_code


@app.route("/alumno/<numero>", methods=["GET"])
def alumno(numero):
    if numero != "1":
        return jsonify({
            "ok": False,
            "mensaje": "Alumno no encontrado"
        }), 404

    numero_destino = "525534935142"

    url = (
        f"https://graph.facebook.com/v24.0/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    mensaje = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }

    respuesta = requests.post(
        url,
        headers=headers,
        json=mensaje,
        timeout=20
    )

    return jsonify({
        "ok": respuesta.ok,
        "numero_alumno": numero,
        "whatsapp_status": respuesta.status_code,
        "respuesta_meta": respuesta.json()
    }), respuesta.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
