import network
import time
import uasyncio
from microdot import Microdot

frequencia = 0

# Informações da conexão
ssid = "silksongLovers"
pwd  = "aura+ego"

# Conexão
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, pwd)
while not sta.isconnected():
    print('.', end="")
    time.sleep(0.3)

print('\nConectado com sucesso!')
print('Seu IP é: ', sta.ifconfig()[0])

app = Microdot()

# Intercepta todas as respostas para adicionar os cabeçalhos de segurança (CORS)
@app.after_request
async def add_cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
    return response

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


@app.route('/lancar', methods=['POST', 'OPTIONS'])
async def lancar(request):
    
    if request.method == 'OPTIONS':
        return ""
    
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
    

@app.route('/buzinar', methods=['POST', 'OPTIONS'])
async def buzinar(request):
    
    if request.method == 'OPTIONS':
        return ""
    
    print("Rota /buzinar acessada")
    try:
        data = request.json
        # código para buzinar
        return {"status": "success"}
    except Exception as e: # ta ta ta tarariaria ta ta tatatata tararatrarara
        return {"status": f"error: {e}"}


@app.route('/mudarFrequencia', methods=['POST', 'OPTIONS'])
async def mudar_freq(request):
    
    if request.method == 'OPTIONS':
        return ""
    
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


app.run(port=80)