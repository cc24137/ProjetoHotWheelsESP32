
import network
import time
import uasyncio
from microdot import Microdot
import json

# ------------------------------------------------
# INFORMAÇÕES DA REDE
# ------------------------------------------------
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
print('Seu IP é:', sta.ifconfig()[0])

# ------------------------------------------------
# MICRODOT
# ------------------------------------------------
app = Microdot()

# ------------------------------------------------
# VARIÁVEIS GLOBAIS
# ------------------------------------------------
frequencia = 0

lancamentos = []  # Ex: [25.4, 30.1]

servo_lock = uasyncio.Lock()

# ------------------------------------------------
# RESPOSTA COM CORS
# ------------------------------------------------
def corsify(data, status=200):

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    body = json.dumps(data)

    return body, status, headers

# ------------------------------------------------
# OPTIONS GLOBAL (PREFLIGHT)
# ------------------------------------------------
@app.route('/<path:path>', methods=['OPTIONS'])
async def options(request, path):

    print("Preflight OPTIONS:", path)

    return corsify({})

# ------------------------------------------------
# -------------------- ROTAS --------------------
# ------------------------------------------------

@app.route('/', methods=['GET'])
async def page(request):

    print("Rota / acessada")

    return corsify({
        "status": "online"
    })

# ------------------------------------------------

@app.route('/lancar', methods=['POST'])
async def lancar(request):

    print("Rota /lancar acessada")

    try:

        if servo_lock.locked():

            return corsify({
                "status": "error",
                "message": "Hardware ocupado"
            }, 423)

        async with servo_lock:

            # ------------------------------------------------
            # CÓDIGO DO SERVO AQUI
            # ------------------------------------------------

            # Exemplo:
            # mover_servo()

            # Simulação:
            # lancamentos.append(42.5)

            return corsify({
                "status": "success"
            })

    except Exception as e:

        print("Erro /lancar:", e)

        return corsify({
            "status": "error",
            "message": str(e)
        }, 500)

# ------------------------------------------------

@app.route('/buzinar', methods=['POST'])
async def buzinar(request):

    print("Rota /buzinar acessada")

    try:

        # ------------------------------------------------
        # CÓDIGO DO BUZZER AQUI
        # ------------------------------------------------

        return corsify({
            "status": "success"
        })

    except Exception as e:

        print("Erro /buzinar:", e)

        return corsify({
            "status": "error",
            "message": str(e)
        }, 500)

# ------------------------------------------------

@app.route('/mudarFrequencia', methods=['POST'])
async def mudar_freq(request):

    print("Rota /mudarFrequencia acessada")

    global frequencia

    try:

        data = request.json or {}

        nova_freq = int(data.get("frequencia", 0))

        frequencia = nova_freq

        print("Nova frequência:", frequencia)

        return corsify({
            "status": "success"
        })

    except Exception as e:

        print("Erro /mudarFrequencia:", e)

        return corsify({
            "status": "error",
            "message": str(e)
        }, 400)

# ------------------------------------------------

@app.route('/historico', methods=['GET'])
async def history(request):

    print("Rota /historico acessada")

    return corsify(lancamentos)

# ------------------------------------------------
# EXECUÇÃO DO SERVIDOR
# ------------------------------------------------
app.run(port=80)