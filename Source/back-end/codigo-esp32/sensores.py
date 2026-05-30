import time
import uasyncio
from machine import PWM, Pin, SoftSPI
from max7129 import Max7219


class Sensores:

    def __init__(self):
        # ---------------- BUZZER ----------------
        self.buzzer = PWM(Pin(25))
        self.buzzer.duty(0)

        # ---------------- SERVO ----------------
        self.servo = PWM(Pin(23), freq=50)

        # ---------------- DISPLAY ----------------
        spi = SoftSPI(
            baudrate=10000000,
            polarity=1,
            phase=0,
            sck=Pin(18),
            mosi=Pin(32),
            miso=Pin(4)
        )
        cs = Pin(5, Pin.OUT)
        self.display = Max7219(32, 8, spi, cs)

        # ---------------- SENSORES ----------------
        self.sensorInicial = Pin(12, Pin.IN)
        self.sensorFinal = Pin(13, Pin.IN)

        # ---------------- TEMPOS ----------------
        self.timeInicial = 0
        self.timeFinal = 0

        # Distância em centímetros
        self.distanciaPista = 22 + 27 + 25

        # ---------------- INTERRUPÇÕES ----------------
        self.sensorInicial.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self.detectarInicioTrajeto
        )
        self.sensorFinal.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self.detectarFinalTrajeto
        )

    # =========================================================
    # CALLBACKS E RESETS
    # =========================================================
    def resetarTempos(self):
        self.timeInicial = 0
        self.timeFinal = 0

    def detectarInicioTrajeto(self, pin):
        self.timeInicial = time.ticks_ms()
        if self.timeFinal != 0:
            self.timeFinal = 0

    def detectarFinalTrajeto(self, pin):
        print("Entrou no tempo final")
        self.timeFinal = time.ticks_ms()

    # =========================================================
    # VELOCIDADE
    # =========================================================
    def calcularVelocidade(self):
        if self.timeInicial == 0 or self.timeFinal == 0:
            raise Exception("Tempos não definidos!")

        # cm -> m
        metroDistancia = self.distanciaPista / 100

        print(self.timeFinal)
        print(self.timeInicial)

        deltaTime = time.ticks_diff(self.timeFinal, self.timeInicial) / 1000

        if deltaTime <= 0:
            raise Exception("Delta de tempo inválido!")

        velocidade = metroDistancia / deltaTime

        self.timeInicial = 0
        self.timeFinal = 0

        self.tocarBuzina(1064, 1000)

        return velocidade

    # =========================================================
    # BUZZER
    # =========================================================
    def tocarBuzina(self, frequency, duration_ms):
        self.buzzer.freq(frequency)
        self.buzzer.duty(512)
        time.sleep_ms(duration_ms)
        self.buzzer.duty(0)

    # =========================================================
    # SERVO
    # =========================================================
    def girarServo(self, angulo):
        duty = int((angulo / 180) * 100 + 25)
        print(angulo)
        self.servo.duty(duty)

    # =========================================================
    # DISPLAY
    # =========================================================
    def mostrarMensagemDisplayLed(self, mensagem, scroll=False, brilho=15):
        self.display.brightness(brilho)
        self.display.fill(0)
        self.display.show()

        if scroll:
            self.display.scroll_text(mensagem)
        else:
            self.display.fill(0)
            self.display.text(mensagem, 0, 1)
            self.display.show()

    # =========================================================
    # DETECÇÃO DE CARRO
    # =========================================================
    def detectarCarro(self):
        if self.sensorInicial.value() == 0:
            self.tocarBuzina(1024, 100)
            return True
        return False

    def corridaFinalizada(self):
        return self.timeInicial != 0 and self.timeFinal != 0

    async def realizar_lancamento(self, tempo_espera_maximo=5.0):
            """
            Orquestra toda a sequência: contagem, abertura, espera e cálculo.
            Retorna a velocidade em m/s se houver sucesso, ou None se der timeout.
            """
            self.resetarTempos()
    
            # Contagem regressiva
            self.mostrarMensagemDisplayLed("3")
            await uasyncio.sleep(1)
            self.mostrarMensagemDisplayLed("2")
            await uasyncio.sleep(1)
            self.mostrarMensagemDisplayLed("1")
            await uasyncio.sleep(1)
            self.mostrarMensagemDisplayLed("GO!")
            self.tocarBuzina(2064, 500)
            
            # Abre a catraca
            self.girarServo(90)
            
            # Loop de espera (Polling)
            passo_espera = 0.1
            tempo_decorrido = 0
            sucesso = False
    
            while tempo_decorrido < tempo_espera_maximo:
                if self.corridaFinalizada():
                    sucesso = True
                    break 
                await uasyncio.sleep(passo_espera)
                tempo_decorrido += passo_espera
    
            # Fecha a catraca
            self.girarServo(0)
    
            # Processa o resultado
            if sucesso:
                vel_ms = self.calcularVelocidade()
                vel_arredondado = round(vel_ms, 2)
                
                self.mostrarMensagemDisplayLed(f"{vel_arredondado}")
                self.tocarBuzina(3000, 200) 
                return vel_arredondado
            else:
                self.mostrarMensagemDisplayLed("ERRO")
                self.tocarBuzina(500, 1000)
                return None
    # =========================================================
    # TESTES
    # =========================================================
    def testarBuzina(self):
        frequencias = [1064, 2064, 3064, 4064]
        for freq in frequencias:
            self.tocarBuzina(freq, 1000)

    def testarServo(self):
        for i in range(181):
            self.girarServo(i)
        time.sleep(1)
        self.girarServo(0)

    def testarDisplay(self):
        self.mostrarMensagemDisplayLed("Teste", True)
        time.sleep(1)
        self.mostrarMensagemDisplayLed("Teste")
        time.sleep(1)
