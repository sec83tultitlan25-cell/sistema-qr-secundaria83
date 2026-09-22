from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "secundaria83_qr_2026"

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
    print(datos)
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
