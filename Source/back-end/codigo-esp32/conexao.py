import network
import time

frequencia = 0

# Informações da conexão
ssid = ""
pwd  = ""

# Conexão
sta = network.WLAN(network.AP_IF)
sta.active(True)
sta.config(essid=ssid, password=pwd)
while sta.active() == False:
    print('.', end="")
    time.sleep(0.3)

print('\nConectado ao ip: ', sta.ifconfig()[0])

from microdot import Microdot

app = Microdot()

# Variável com o histórico de lançamentos 
lancamentos = []

# ------------------------------------------------
# -------------------- Rotas --------------------
# ------------------------------------------------
@app.route('/', methods = ['GET'])
async def page(request):
    return "pagina"


@app.route('/lancar', methods=['POST'])
async def control(request):
    try:
        data = request.json
        # código para mexer o servo de modo a lançar e ligar um led
    except Exception as e:
        return {"status": f"error: {e}"}
    

@app.route('/buzinar', methods=['POST'])
async def control(request):
    try:
        data = request.json
        # código para buzinar
    except Exception as e:
        return {"status": f"error: {e}"}


@app.route('/mudarFrequencia', methods=['POST'])
async def control(request):
    try:
        data = request.json
        nova_freq = int(data.get("frequencia"))
        frequencia = nova_freq
    except Exception as e:
        return {"status": f"error: {e}"}


@app.route('/historico', methods = ['GET'])
async def historic(request):
    try:
        return lancamentos
    except Exception as e:
        return {"status": f"error: {e}"}


app.run(debug=True, port=80)