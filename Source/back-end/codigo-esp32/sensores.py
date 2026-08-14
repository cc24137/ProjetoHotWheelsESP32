import time
import uasyncio
import neopixel
from machine import PWM, Pin


class Sensores:

    # ---------------- FONTE MICRO 3x4 ----------------
    FONTE_3x4 = {
        '0': [0b111, 0b101, 0b101, 0b111],
        '1': [0b010, 0b110, 0b010, 0b111],
        '2': [0b111, 0b011, 0b100, 0b111],
        '3': [0b111, 0b011, 0b011, 0b111],
        '4': [0b101, 0b101, 0b111, 0b001],
        '5': [0b111, 0b100, 0b011, 0b111],
        '6': [0b111, 0b100, 0b111, 0b111],
        '7': [0b111, 0b001, 0b010, 0b010],
        '8': [0b111, 0b111, 0b101, 0b111],
        '9': [0b111, 0b101, 0b111, 0b001],
        'A': [0b010, 0b101, 0b111, 0b101],
        'B': [0b110, 0b110, 0b101, 0b110],
        'C': [0b011, 0b100, 0b100, 0b011],
        'D': [0b110, 0b101, 0b101, 0b110],
        'E': [0b111, 0b110, 0b100, 0b111],
        'F': [0b111, 0b110, 0b100, 0b100],
        'G': [0b011, 0b100, 0b101, 0b011],
        'H': [0b101, 0b101, 0b111, 0b101],
        'I': [0b111, 0b010, 0b010, 0b111],
        'L': [0b100, 0b100, 0b100, 0b111],
        'O': [0b111, 0b101, 0b101, 0b111],
        'P': [0b110, 0b101, 0b110, 0b100],
        'R': [0b110, 0b101, 0b110, 0b101],
        'S': [0b011, 0b100, 0b001, 0b110],
        'T': [0b111, 0b010, 0b010, 0b010],
        'U': [0b101, 0b101, 0b101, 0b111],
        '!': [0b010, 0b010, 0b000, 0b010],
        '.': [0b000, 0b000, 0b000, 0b010],
        ' ': [0b000, 0b000, 0b000, 0b000],
    }

    def __init__(self, pin_neopixel=4):
        # ---------------- BUZZER ----------------
        self.buzzer = PWM(Pin(25))
        self.buzzer.duty(0)

        # ---------------- SERVO ----------------
        self.servo = PWM(Pin(23), freq=50)

        # ---------------- DISPLAY WS2812B (NEOPIXEL) ----------------
        self.num_leds = 48  # 3 matrizes 4x4 = 12 colunas x 4 linhas
        self.pin_display = Pin(pin_neopixel, Pin.OUT)
        self.np = neopixel.NeoPixel(self.pin_display, self.num_leds)
        self.limparDisplay()

        # ---------------- SENSORES ----------------
        self.sensor = Pin(12, Pin.IN)

        # ---------------- TEMPOS ----------------
        self.timeInicial = 0
        self.timeFinal = 0

        # Distância em centímetros
        self.distanciaPista = 1.17

        # ---------------- INTERRUPÇÕES ----------------
        self.sensor.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self.detectarFimTrajeto
        )

    # -----------------------------------
    # MÉTODOS AUXILIARES DO DISPLAY WS2812B
    # -----------------------------------
    def xy_para_index(self, x, y):
        """Converte coordenada (X, Y) do painel 12x4 para a posição no cabo do NeoPixel."""
        x_invertido = 11 - x 
        painel = x_invertido // 4 
        x_local = x_invertido % 4 
        return (painel * 16) + (y * 4) + x_local

    def limparDisplay(self):
        """Apaga todos os LEDs."""
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def desenharTexto(self, texto, pos_x=0, cor=(15, 15, 15)):
        """Desenha uma string de texto na posição X informada."""
        self.limparDisplay()

        cursor_x = pos_x
        for char in str(texto).upper():
            bitmap = self.FONTE_3x4.get(char, self.FONTE_3x4[' '])
            for y in range(4):
                linha = bitmap[y]
                for col in range(3):
                    if (linha >> (2 - col)) & 1:
                        x = cursor_x + col
                        if 0 <= x < 12:  # Desenha apenas se estiver na área visível 12x4
                            idx = self.xy_para_index(x, y)
                            self.np[idx] = cor
            cursor_x += 4  # 3 pixels da letra + 1 de espaço

        self.np.write()

    # -----------------------------------
    # CALLBACKS E RESETS
    # -----------------------------------
    def resetarTempos(self):
        self.tempoInicial = 0

    def detectarFimTrajeto(self, pin):
        # print("inicio")
#        self.timeFinal = time.ticks_ms()
        self.resetarTempos()
        
    # -----------------------------------
    # BUZZER
    # -----------------------------------
    def tocarBuzina(self, frequency, duration_ms):
        self.buzzer.freq(frequency)
        self.buzzer.duty(512)
        time.sleep_ms(duration_ms)
        self.buzzer.duty(0)

    # -----------------------------------
    # SERVO
    # -----------------------------------
    def girarServo(self, angulo):
        duty = int((angulo / 180) * 100 + 25)
        self.servo.duty(duty)
        
    # DISPLAY (INTERFACE DE MENSAGENS)
    # -----------------------------------
    def mostrarMensagemDisplayLed(self, mensagem, scroll=False, cor=(15, 15, 15), velocidade=0.08):
        """
        Exibe a mensagem no display WS2812B.
        - Se scroll=True: Desliza o texto.
        - Se scroll=False: Centraliza textos curtos (1 ou 2 caracteres) ou desenha direto.
        """
        msg_str = str(mensagem)

        if scroll:
            largura_total = len(msg_str) * 4
            for x in range(12, -largura_total, -1):
                self.desenharTexto(msg_str, pos_x=x, cor=cor)
                time.sleep(velocidade)
        else:
            # Centralização automática para telas 12x4
            if len(msg_str) == 1:
                offset_x = 4  # Centraliza 1 número/letra no meio
            elif len(msg_str) == 2:
                offset_x = 2  # Centraliza 2 números/letras
            else:
                offset_x = 0  # 3 caracteres usam toda a largura (12 cols)

            self.desenharTexto(msg_str, pos_x=offset_x, cor=cor)

    # -----------------------------------
    # DETECÇÃO DE CARRO
    # -----------------------------------
    def detectarCarro(self):
        if self.sensor.value() == 0:
            self.tocarBuzina(1024, 100)
            return True
        return False

    def corridaFinalizada(self):
        return self.tempoInicial == 0
    
    def calcularVelocidade(self, tempo):
        return self.distanciaPista / tempo

    async def realizar_lancamento(self, tempo_espera_maximo=5.0):
        """
        Orquestra toda a sequência: contagem, abertura, espera e cálculo.
        Retorna a velocidade em m/s se houver sucesso, ou None se der timeout.
        """
        
        # reseta tudo
        self.girarServo(0)
        self.buzzer.duty(0)

        # Contagem regressiva (com cores: Vermelho -> Amarelo -> Verde)
        self.mostrarMensagemDisplayLed("3", cor=(20, 0, 0))
        self.tocarBuzina(2064, 500)

        await uasyncio.sleep(1)

        self.mostrarMensagemDisplayLed("2", cor=(20, 10, 0))
        self.tocarBuzina(2064, 500)

        await uasyncio.sleep(1)

        self.mostrarMensagemDisplayLed("1", cor=(0, 20, 0))
        self.tocarBuzina(2064, 500)

        await uasyncio.sleep(1)
        self.mostrarMensagemDisplayLed("GO!", cor=(231, 82, 200))
       
        # Abre a catraca
        self.girarServo(90)
        self.tocarBuzina(3064, 1000)
        
        self.resetarTempos()
        self.tempoInicial = time.ticks_ms()
        print(f"tempo inicial no início: {self.tempoInicial}")
        
        # Loop de espera (Polling)
        passo_espera = 0.1
        tempo_decorrido = 0
        sucesso = False

        while tempo_decorrido < tempo_espera_maximo:
            print(f"tempo decorrido dentro do loop: {tempo_decorrido}")
            if self.corridaFinalizada():
                sucesso = True
                break
            await uasyncio.sleep(passo_espera)
            tempo_decorrido += passo_espera

        # Fecha a catraca
        self.girarServo(0)

        # Processa o resultado
        print(f"tempo decorrido depois do loop: {tempo_decorrido}")
        print(f"sucesso: {sucesso}")
        if sucesso:
            vel_ms = self.calcularVelocidade(tempo_decorrido)
            print(vel_ms)
            vel_arredondado = round(vel_ms, 2)
            print(vel_arredondado)
            # Exibe a velocidade em azul
            self.mostrarMensagemDisplayLed(f"{vel_arredondado}", scroll=True, cor=(0, 15, 25))
            self.tocarBuzina(3000, 200)
            return vel_arredondado, tempo_decorrido
        else:
            # Exibe ERRO em vermelho deslizando ou fixo
            self.mostrarMensagemDisplayLed("ERRO", cor=(25, 0, 0))
            self.tocarBuzina(500, 1000)
            return None

    # -----------------------------------
    # TESTES
    # -----------------------------------
    def testarBuzina(self):
        print("testando buzina")
        frequencias = [1064, 2064, 3064, 4064]
        for freq in frequencias:
            self.tocarBuzina(freq, 1000)

    def testarServo(self):
        print("testando servo")
        self.girarServo(90)
        time.sleep(1)
        self.girarServo(0)
        time.sleep(1)

    def testarDisplay(self):
        print("testando display")
        self.mostrarMensagemDisplayLed("TESTE", scroll=True, cor=(10, 10, 20))
        time.sleep(1)
        self.mostrarMensagemDisplayLed("123", cor=(0, 20, 0))
        time.sleep(1)


# --- MAIN ---
def main():
    sensores = Sensores()
    while True:
        print('iniccio')
        print(uasyncio.run(sensores.realizar_lancamento()))
        time.sleep(8)


#main()