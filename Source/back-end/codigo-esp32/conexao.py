import network
import time
import uasyncio
from microdot import Microdot, Response

# Informações da conexão
ssid = "silksongLovers"
pwd  = "aura+ego"

# ------------------------------------------------
# CONEXÃO WIFI
# ------------------------------------------------
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, pwd)

while not sta.isconnected():
    print('.', end="")
    time.sleep(0.3)

print('\nConectado com sucesso!')
print('Seu IP é: ', sta.ifconfig()[0])

# ------------------------------------------------
# MICRODOT
# ------------------------------------------------
app = Microdot()

Response.default_content_type = 'application/json'

# Variáveis globais
frequencia = 0
lancamentos = []  # Ex: [25.4, 30.1]
servo_lock = uasyncio.Lock()

# ------------------------------------------------
# CORS GLOBAL
# ------------------------------------------------
@app.after_request
async def cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ------------------------------------------------
# OPTIONS GLOBAL (PREFLIGHT)
# ------------------------------------------------
@app.route('/<path:path>', methods=['OPTIONS'])
async def options(request, path):
    return ''

# ------------------------------------------------
# -------------------- Rotas --------------------
# ------------------------------------------------

@app.route('/', methods=['GET'])
async def page(request):
    print("Rota / (Ping de conexão) acessada")
    return "OK"

@app.route('/lancar', methods=['POST'])
async def lancar(request):

    print("Rota /lancar acessada")

    try:

        if servo_lock.locked():
            return {
                "status": "error",
                "message": "Hardware ocupado"
            }, 423

        async with servo_lock:

            # Aqui você insere o código do Servo/Atuador

            # Exemplo:
            # mover_servo()

            # Simulando nova velocidade:
            # nova_velocidade = calcular_velocidade()
            # lancamentos.append(nova_velocidade)

            return {
                "status": "success"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }, 500

@app.route('/buzinar', methods=['POST'])
async def buzinar(request):

    print("Rota /buzinar acessada")

    try:

        # Código do buzzer aqui

        return {
            "status": "success"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }, 500

@app.route('/mudarFrequencia', methods=['POST'])
async def mudar_freq(request):

    print("Rota /mudarFrequencia acessada")

    global frequencia

    try:

        data = request.json or {}

        nova_freq = int(data.get("frequencia", 0))

        frequencia = nova_freq

        print(f"Nova frequência: {frequencia}")

        return {
            "status": "success"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }, 400

@app.route('/historico', methods=['GET'])
async def history(request):

    print("Rota /historico acessada")

    return lancamentos

# ------------------------------------------------
# EXECUÇÃO DO SERVIDOR
# ------------------------------------------------
app.run(port=80)