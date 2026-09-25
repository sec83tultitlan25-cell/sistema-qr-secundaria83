from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
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
        f"https://graph.facebook.com/v25.0/"
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
            "name": "aviso_llegada_alumno",
            "language": {
                "code": "es_MX"
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
    nombre_alumno = "Juan Pérez López"
    grado_grupo = "1° A"
    ahora = datetime.now(ZoneInfo("America/Mexico_City"))
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%I:%M %p")

    if numero != "1":
        return jsonify({
            "ok": False,
            "mensaje": "Alumno no encontrado"
        }), 404

    numero_destino = "525534935142"

    url = (
        f"https://graph.facebook.com/v25.0/"
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
            "name": "aviso_llegada_alumno",
            "language": {
                "code": "es_MX"
            },"components": [
    {
        "type": "body",
        "parameters": [
            {"type": "text", "text": nombre_alumno},
            {"type": "text", "text": grado_grupo},
            {"type": "text", "text": fecha},
            {"type": "text", "text": hora}
        ]
    }
]
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


@app.route("/scanner", methods=["GET"])
def scanner():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escáner QR - Secundaria 83</title>

    <script src="https://unpkg.com/html5-qrcode"></script>

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }

        #reader {
            width: 100%;
            max-width: 500px;
            margin: auto;
        }

        #resultado {
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>

<body>

    <h2>Escáner QR - Secundaria 83</h2>

    <p>Coloca el código QR de la credencial frente a la cámara.</p>

    <div id="reader"></div>

    <div id="resultado">
        Esperando código QR...
    </div>

    <script>
        let procesando = false;

        function qrLeido(texto) {

            if (procesando) return;
            procesando = true;

            document.getElementById("resultado").innerHTML =
                "QR detectado. Registrando llegada...";

            let numero = texto.trim();

            fetch("/alumno/" + encodeURIComponent(numero))
                .then(response => response.json())
                .then(data => {

                    if (data.ok) {
                        document.getElementById("resultado").innerHTML =
                            "✅ Llegada registrada y WhatsApp enviado.";
                    } else {
                        document.getElementById("resultado").innerHTML =
                            "⚠️ No se pudo completar el registro.";
                    }

                    setTimeout(function() {
                        procesando = false;
                        document.getElementById("resultado").innerHTML =
                            "Esperando siguiente código QR...";
                    }, 5000);

                })
                .catch(error => {

                    document.getElementById("resultado").innerHTML =
                        "❌ Error al procesar el código.";

                    setTimeout(function() {
                        procesando = false;
                    }, 5000);
                });
        }

        function errorQR(error) {
        }

        const lector = new Html5QrcodeScanner(
            "reader",
            {
                fps: 10,
                qrbox: { width: 250, height: 250 },
                rememberLastUsedCamera: true
            },
            false
        );

        lector.render(qrLeido, errorQR);

    </script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
