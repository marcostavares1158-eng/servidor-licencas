from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# Base de dados simples em memória (ou pode adaptar para SQLite)
# Dicionário: { "CHAVE-DE-LICENCA": "2026-11-28" }
LICENCAS = {"CLIENTE-VIP-01": "2026-12-01"}


@app.route("/", methods=["GET"])
def home():
  return jsonify(
      {
          "status": "online",
          "mensagem": "Servidor de Licenças MeuPDV-ERP a funcionar!",
      }
  )


# Rota para o PDV verificar se a licença está válida
@app.route("/api/verificar-licenca", methods=["POST"])
def verificar_licenca():
  dados = request.json or {}
  chave = dados.get("chave")

  if not chave or chave not in LICENCAS:
    return jsonify({"valida": False, "mensagem": "Licença não encontrada."}), 404

    str_data_exp = LICENCAS[chave]
  data_exp = datetime.strptime(str_data_exp, "%Y-%m-%d").date()
  hoje = datetime.now().date()

  if hoje <= data_exp:
    dias_restantes = (data_exp - hoje).days
    return jsonify({
        "valida": True,
        "expiracao": str_data_exp,
        "dias_restantes": dias_restantes,
    })
  else:
    return jsonify(
        {"valida": False, "expiracao": str_data_exp, "mensagem": "Licença expirada."}
    )


# Rota para receber o aviso automático do Asaas quando o cliente pagar
@app.route("/api/webhook-asaas", methods=["POST"])
def webhook_asaas():
  evento = request.json or {}
  # Aqui o Asaas avisa quando um pagamento é confirmado
  tipo_evento = evento.get("event")

  if tipo_evento == "PAYMENT_RECEIVED":
    payment = evento.get("payment", {})
    # Você pode identificar o cliente pelo email, externalReference ou ID da cobrança
    # Para simplificar, vamos estender 30 dias a partir de hoje para a chave padrão:
    chave_cliente = "CLIENTE-VIP-01"

    nova_data = datetime.now().date() + timedelta(days=30)
    LICENCAS[chave_cliente] = nova_data.strftime("%Y-%m-%d")

    return jsonify({"status": "sucesso", "nova_validade": str(nova_data)}), 200

  return jsonify({"status": "ignorado"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
