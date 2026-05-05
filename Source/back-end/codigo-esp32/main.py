#Imports
from machine import Pin, PWM,SoftSPI
from max7219 import Max7219
import time


#Portas e sensores
buzzer = PWM(Pin(25)) # Change 15 to your GPIO pin
buzzer.duty(0)

servo = PWM(Pin(23), freq=50)

spi = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(18), mosi=Pin(32), miso=Pin(4))
cs = Pin(5, Pin.OUT)
display = Max7219(32, 8, spi, cs) 

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
    testarDisplay()
    time.sleep(1)