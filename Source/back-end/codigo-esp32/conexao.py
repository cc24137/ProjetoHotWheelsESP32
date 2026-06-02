import json
import time

import network
import uasyncio
from microdot import Microdot
from sensores import Sensores

# ------------------------------------------------
# INFORMAÇÕES DA REDE
# ------------------------------------------------
ssid = "silksongLovers"
pwd  = "aura+ego"

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, pwd)

while not sta.isconnected():
    print('.', end="")
    time.sleep(0.3)

print('\nConectado com sucesso!')
print('Seu IP é:', sta.ifconfig()[0])

app = Microdot()
controller = Sensores()

lancamentos = []
servo_lock = uasyncio.Lock()

def corsify(data, status=200):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    return json.dumps(data), status, headers

@app.route('/<path:path>', methods=['OPTIONS'])
async def options(request, path):
    return corsify({})

@app.route('/', methods=['GET'])
async def page(request):
    controller.buzzer.duty(0)
    return corsify({"status": "online"})

@app.route('/lancar', methods=['POST'])
async def lancar(request):
    print("Rota /lancar acessada")
    try:
        # Trava para evitar que duas pessoas cliquem em 'Iniciar' ao mesmo tempo
        if servo_lock.locked():
            return corsify({"status": "error", "message": "Hardware ocupado"}, 423)

        async with servo_lock:
            # O servidor web pede para o hardware fazer a corrida e aguarda o resultado
    
            velocidade, tempo = await controller.realizar_lancamento(tempo_espera_maximo=5.0)
            print(f"velocidade: {velocidade}")
            print(f"tempo: {tempo}")

            if velocidade is not None:
                lancamentos.append((velocidade, tempo))
                print(f"Velocidade registrada: {velocidade} m/s")
                return corsify({"status": "success"})
            else:
                print("Erro: O carrinho não cruzou o sensor a tempo.")
                return corsify({"status": "error", "message": "Timeout do carrinho"}, 400)

    except Exception as e:
        print("Erro /lancar:", e)
        controller.girarServo(0) # Proteção em caso de quebra de código
        return corsify({"status": "error", "message": str(e)}, 500)

@app.route('/buzinar', methods=['POST'])
async def buzinar(request):
    try:
        controller.tocarBuzina(2064, 1000)
        return corsify({"status": "success"})
    except Exception as e:
        return corsify({"status": "error", "message": str(e)}, 500)

@app.route('/historico', methods=['GET'])
async def history(request):
    return corsify(lancamentos)

app.run(port=80)
