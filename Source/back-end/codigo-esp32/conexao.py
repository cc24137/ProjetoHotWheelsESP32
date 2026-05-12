import network
import time
import uasyncio
from microdot import Microdot

frequencia = 0

# Informações da conexão
ssid = "rededoesp"
pwd  = "senha123"

# Conexão
sta = network.WLAN(network.AP_IF)
sta.active(True)
sta.config(essid=ssid, password=pwd)
while sta.active() == False:
    print('.', end="")
    time.sleep(0.3)

print('\nConectado ao ip: ', sta.ifconfig()[0])

app = Microdot()

# Variável com o histórico de lançamentos 
lancamentos = []

# Lock
servo_lock = uasyncio.Lock()


# ------------------------------------------------
# -------------------- Rotas --------------------
# ------------------------------------------------
@app.route('/', methods = ['GET'])
async def page(request):
    print("Rota / acessada")
    return "pagina"


@app.route('/lancar', methods=['POST'])
async def lancar(request):
    print("Rota /lancar acessada")
    try:
        if servo_lock.locked(): # Se o servo está em movimento, não executa novo movimento
            return {"status": "error", "message": "O hardware está ocupado. Tente novamente em instantes."}, 423 
        
        async with servo_lock:
          data = request.json
          return {"status": "success"}
        # código para mexer o servo de modo a lançar e ligar um led
    except Exception as e:
        return {"status": f"error: {e}"}
    

@app.route('/buzinar', methods=['POST'])
async def buzinar(request):
    print("Rota /buzinar acessada")
    try:
        data = request.json
        # código para buzinar
        return {"status": "success"}
    except Exception as e: # ta ta ta tarariaria ta ta tatatata tararatrarara
        return {"status": f"error: {e}"}


@app.route('/mudarFrequencia', methods=['POST'])
async def mudar_freq(request):
    print("Rota /mudarFrequencia acessada")
    global frequencia
    try:
        data = request.json
        nova_freq = int(data.get("frequencia"))
        frequencia = nova_freq
        return {"status": "success"}
    except Exception as e:
        return {"status": f"error: {e}"}


@app.route('/historico', methods = ['GET'])
async def history(request):
    try:
        print("Rota /historico acessada")
        return lancamentos
    except Exception as e:
        return {"status": f"error: {e}"}


app.run(host= '0.0.0.0',debug=True, port=80)