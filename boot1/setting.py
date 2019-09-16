#boot.py のペリフェラル初期化部分のみ
import lcd
import image
import time
import uos
import sys
from Maix import GPIO
from fpioa_manager import *

def boot_lcd():
    lcd.init()
    lcd.rotation(2) #Rotate the lcd 180deg

    try:
        img = image.Image("/sd/startup.jpg")
        lcd.display(img)

        test = "test"
        lcd.draw_string(lcd.width()//50,lcd.height()//2, test , lcd.WHITE, lcd.RED)
    
    except:
        lcd.draw_string(lcd.width()//50,lcd.height()//2, "Error: Cannot find start.jpg", lcd.WHITE, lcd.RED)   

def boot_set_IF():

    fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
    but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

    fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
    but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

    fm.register(board_info.LED_W, fm.fpioa.GPIO3)
    led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
    led_w.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_R, fm.fpioa.GPIO4)
    led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
    led_r.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_G, fm.fpioa.GPIO5)
    led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
    led_g.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_B, fm.fpioa.GPIO6)
    led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
    led_b.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_B, fm.fpioa.GPIO6)
    led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
    led_b.value(1) #

    time.sleep(0.5) # Delay for few seconds to see the start-up screen :p            

    if but_a.value() == 0:
        sys.exit()
