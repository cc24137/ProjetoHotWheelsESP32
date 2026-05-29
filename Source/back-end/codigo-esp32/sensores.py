#Imports
from machine import Pin, PWM,SoftSPI
from libs.max7129 import Max7219
import time


#Portas e sensorIniciales
buzzer = PWM(Pin(25)) # Change 15 to your GPIO pin
buzzer.duty(0)

servo = PWM(Pin(23), freq=50)

spi = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(18), mosi=Pin(32), miso=Pin(4))
cs = Pin(5, Pin.OUT)
display = Max7219(32, 8, spi, cs) 

#HW-201
sensorInicial = Pin(13, Pin.IN)
sensorFinal = Pin(14,Pin.IN)
timeInicial = 0
timeFinal = 0
distanciaPista = 45 #Valor precisa ser alterado
#Funções para Deploy
def detectarInicioTrajeto(pin):
    global timeInicial,timeFinal
    timeInicial = time.now()
    if timeFinal != 0:
        timeFinal =0

def detectarFinalTrajeto(pin):
    global timeFinal,timeInicial
    if timeInicial == 0:
        raise Exception("Objeto não passou pelo sensor Inicial!!")
    timeFinal = time.time()

def calcularVelocidade():
    global timeInicial,timeFinal,distanciaPista
    if timeInicial ==0 or timeFinal == 0:
        raise Exception("Tempos não definidos!")
    metroDistancia = distanciaPista /100 
    velocidade = metroDistancia / (timeFinal - timeInicial)
    timeInicial =0
    timeFinal = 0
    return velocidade

#Teste de callback
#Teste de sensor infravermelho, é para chamar as funções a partir da alteração dos sensores
sensorInicial.irq(trigger=Pin.IRQ_FALLING, handler=detectarInicioTrajeto)
sensorFinal.irq(trigger=Pin.IRQ_FALLING, handler=detectarFinalTrajeto)

#Funções
def tocarBuzina(frequency, duration_ms):
    buzzer.freq(frequency)
    buzzer.duty(512) 
    time.sleep_ms(duration_ms)
    buzzer.duty(0) 


def girarServo(angulo):
    duty = int((angulo / 180) * 100 +25) #Converte o angulo para um valor entre 0-1023
    print(angulo)
    servo.duty(duty)

def mostrarMensagemDisplayLed(mensagem,scrool=False,brihlo =15):
    display.fill(0)
    display.show()
    if(scrool):
        display.scroll_text(mensagem)
    else:
        display.fill(0)
        display.text(mensagem, 0, 1)
        display.show()

def detectarCarro():
    if(sensorInicial.value()==0):
        tocarBuzina(1024,100);
    return True


#Funcoes testes
frequencys = {1064,2064,3064,4064}
def testarBuzina():
    for i in frequencys:
        tocarBuzina(i,1000)

def testarServo():
    for i in range(180):
        girarServo(i)
    time.sleep(1)
    girarServo(0)

def testarDisplay():
    mostrarMensagemDisplayLed("Teste",True)
    time.sleep(1)
    mostrarMensagemDisplayLed("Teste")
    time.sleep(1)

#Inicialização
while True:
    if sensorInicial != 0 and sensorFinal !=0:
        calcularVelocidade()