#Autores: Andres Galvis, Keppler Sánchez y Daniel Viafara

from machine import Pin, PWM, ADC
from neopixel import NeoPixel
import utime
from tm1637 import TM1637

# Configuración del servo 
servo = PWM(Pin(13), freq=50)

# Configuración de la tira Neopixel
num_leds = 16
pixels = NeoPixel(Pin(15), num_leds)

# Configuración del potenciómetro 
potenciometro = ADC(Pin(32))
potenciometro.atten(ADC.ATTN_11DB)  
potenciometro.width(ADC.WIDTH_12BIT) 

# Configuración de la pantalla TM1637
try:
    tm = TM1637(clk=Pin(2), dio=Pin(5))
except:
    tm = None

# Configuración del botón de pausa
boton_pausa = Pin(4, Pin.IN, Pin.PULL_UP)
ultimo_estado_boton = 1  # Para evitar rebotes

# Función para mapear valores
def map_value(x, in_min, in_max, out_min, out_max):
    return round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Función para mover el servo a un ángulo específico
def mover_servo(angulo):
    pwm_value = map_value(angulo, 0, 180, 40, 115)  
    servo.duty(pwm_value)

# Genera un degradado en rojo o azul con intensidad según la velocidad
def generar_degradado(base_color, intensidad):
    intensidad = max(0.2, min(intensidad, 1.0))  
    return [(int(base_color[0] * (i / num_leds) * intensidad), 
             int(base_color[1] * (i / num_leds) * intensidad), 
             int(base_color[2] * (i / num_leds) * intensidad)) for i in range(num_leds)]

# Función para actualizar el Neopixel
def actualizar_neopixel(angulo, direccion, velocidad):
    posicion_led = round((angulo / 180) * (num_leds - 1))

    intensidad = max(0.3, 1 - (velocidad / 100))  
    gradient = generar_degradado((255, 0, 0) if direccion == 1 else (0, 0, 255), intensidad)

    # Transición de color cuando cambia de dirección
    if angulo == 0 or angulo == 180:
        gradient = generar_degradado((255, 50, 50), 0.5)

    for i in range(num_leds):
        pixels[i] = gradient[i]
    
    pixels[posicion_led] = (255, 255, 255)  # Pixel blanco sigue el movimiento
    pixels.write()

# Función para manejar el botón de pausa con debounce
def leer_boton():
    global ultimo_estado_boton
    estado_actual = boton_pausa.value()
    
    if estado_actual == 0 and ultimo_estado_boton == 1:  # Cambio detectado (botón presionado)
        utime.sleep(0.05)  # Pequeño delay para evitar rebote
        ultimo_estado_boton = 0
        return True
    elif estado_actual == 1:
        ultimo_estado_boton = 1  # Se resetea cuando se suelta el botón
    
    return False

# Función principal
def main():
    angulo = 0
    direccion = 1  # 1: Derecha, -1: Izquierda
    pausado = False

    while True:
        if leer_boton():  # Si se detecta el botón presionado
            pausado = not pausado  # Cambia el estado de pausa

        if not pausado:
            velocidad = max(10, potenciometro.read() // 2)  # Ajusta velocidad mínima
            mover_servo(angulo)
            actualizar_neopixel(angulo, direccion, velocidad)
            
            if tm:
                tm.number(velocidad)  # Muestra la velocidad en la pantalla TM1637

            if angulo >= 180:
                direccion = -1
            elif angulo <= 0:
                direccion = 1

            angulo += direccion * 5  # Movimiento en pasos de 5°
            utime.sleep_ms(velocidad)

if __name__ == "__main__":
    main()
