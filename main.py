from tm1637 import TM1637
from machine import Pin, ADC, PWM
from neopixel import NeoPixel
import utime

# Configuración de la pantalla TM1637
tm = TM1637(clk=Pin(2), dio=Pin(5))

# Configuración del potenciómetro
potenciometro = ADC(Pin(32))
potenciometro.atten(ADC.ATTN_11DB)
potenciometro.width(ADC.WIDTH_12BIT)

# Configuración del servo en ESP32
servo = PWM(Pin(13), freq=50)

# Configuración de Neopixel
pixels = NeoPixel(Pin(15), 16)

# Definición de colores en Neopixel
red_gradient = [
    (255, 0, 0), (220, 0, 0), (190, 10, 0), (160, 20, 0),
    (130, 30, 0), (100, 40, 0), (70, 50, 0), (40, 60, 0),
    (10, 70, 0), (0, 80, 0), (0, 90, 10), (0, 100, 20),
    (0, 110, 30), (0, 120, 40), (0, 130, 50), (255, 255, 255)  # Blanco en movimiento
]

green_gradient = [
    (0, 255, 0), (0, 220, 0), (0, 190, 10), (0, 160, 20),
    (0, 130, 30), (0, 100, 40), (0, 70, 50), (0, 40, 60),
    (0, 10, 70), (10, 0, 80), (20, 0, 90), (30, 0, 100),
    (40, 0, 110), (50, 0, 120), (60, 0, 130), (255, 255, 255)  # Blanco en movimiento
]

# Lista de ángulos de rotación del servo
angulos = [
    0, 10, 20, 30, 40, 50, 60, 70, 80, 85, 90, 95, 100, 110, 120, 130,
    140, 150, 160, 170, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90, 80, 70,
    60, 50, 40, 30, 20, 10, 0
]

# Función para mapear valores a duty cycle (ESP32 usa 40 a 115)
def map_value(x, in_min, in_max, out_min, out_max):
    return round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Función para mover el servo a un ángulo específico
def angulo(a):
    pwm_value = map_value(a, 0, 180, 40, 115)  
    servo.duty(pwm_value)

# Función para actualizar los colores del Neopixel
def actualizar_neopixel(direccion):
    if direccion == -1:
        red_gradient.insert(0, red_gradient.pop())  # Mover rojo en sentido antihorario
        for j in range(16):
            pixels[j] = red_gradient[j]
    else:
        green_gradient.append(green_gradient.pop(0))  # Mover verde en sentido horario
        for j in range(16):
            pixels[j] = green_gradient[j]
    pixels.write()

# Función para mostrar valores decimales en TM1637
def mostrar_decimal_tm1637(valor):
    entero = int(valor)  
    decimal = int((valor - entero) * 10)  
    tm.show(f"{entero}{decimal}")

# Función principal
def main():
    direccion = 1  # 1 para horario, -1 para antihorario
    indice = 0  # Control del ángulo actual

    while True:
        # Leer el valor del potenciómetro y escalarlo
        poten = potenciometro.read() / 50
        delay = map_value(poten, 0, 40.95, 1, 20)  
        
        mostrar_decimal_tm1637(poten)

        print(f"Potenciómetro: {poten:.2f}, Delay: {delay} ms")

        angulo_actual = angulos[indice]
        angulo(angulo_actual)

        # Determinar dirección de rotación del Neopixel
        if indice > 0:
            direccion = 1 if angulos[indice] > angulos[indice - 1] else -1

        # Aplicar la rotación en Neopixel
        actualizar_neopixel(direccion)

        # Avanzar en la lista de ángulos
        indice = (indice + 1) % len(angulos)

        # Pequeña pausa en cada iteración (según el potenciómetro)
        utime.sleep_ms(delay)

if __name__ == "__main__":
    main()