from Maix import I2S, GPIO
import audio
from Maix import GPIO
from fpioa_manager import *
from machine import I2C
import uos
import time

# mpu6886 用レジスタアドレスの定義
class MPU6886_regmap:
    #SLAVE ADDLESS
    SL_ADD = 104
    
    #REGISTER ADDLESS
    XG_OFFS_TC_H = 4
    XG_OFFS_TC_L = 5
    YG_OFFS_TC_H = 7
    YG_OFFS_TC_L = 8
    ZG_OFFS_TC_H = 10
    ZG_OFFS_TC_L = 11
    SELF_TEST_X_ACCEL = 13
    SELF_TEST_Y_ACCEL = 14
    SELF_TEST_Z_ACCEL = 15
    XG_OFFS_USRH = 19
    XG_OFFS_USRL = 20
    YG_OFFS_USRH = 21
    YG_OFFS_USRL = 22
    ZG_OFFS_USRH = 23
    ZG_OFFS_USRL = 24
    SMPLRT_DIV = 25
    CONFIG = 26
    GYRO_CONFIG = 27
    ACCEL_CONFIG = 28
    ACCEL_CONFIG2 = 29
    LP_MODE_CFG = 30
    ACCEL_WOM_X_THR = 32
    ACCEL_WOM_Y_THR = 33
    ACCEL_WOM_Z_THR = 34
    FIFO_EN = 35
    FSYNC_INT = 54
    INT_PIN_CFG = 55
    INT_ENABLE = 56
    FIFO_WM_INT_STATUS =57
    INT_STATUS = 58
    ACCEL_XOUT_H = 59
    ACCEL_XOUT_L = 60
    ACCEL_YOUT_H = 61
    ACCEL_YOUT_L = 62
    ACCEL_ZOUT_H = 63
    ACCEL_ZOUT_L = 64
    TEMP_OUT_H = 65
    TEMP_OUT_L  = 66
    GYRO_XOUT_H  = 67
    GYRO_XOUT_L  = 68
    GYRO_YOUT_H  = 69
    GYRO_YOUT_L  = 70
    GYRO_ZOUT_H  = 71
    GYRO_ZOUT_L  = 72
    SELF_TEST_X_GYRO  = 80
    SELF_TEST_Y_GYRO  = 81
    SELF_TEST_Z_GYRO  = 82
    E_ID0  = 83
    E_ID1  = 84
    E_ID2  = 85
    E_ID3  = 86
    E_ID4  = 87
    E_ID5  = 88
    E_ID6  = 89
    FIFO_WM_TH1  = 96
    FIFO_WM_TH2  = 97
    SIGNAL_PATH_RESET  = 104
    ACCEL_INTEL_CTRL  = 105
    USER_CTRL  = 106
    PWR_MGMT_1  = 107
    PWR_MGMT_2  = 108
    I2C_IF  = 112
    FIFO_COUNTH  = 114
    FIFO_COUNTL  = 115
    FIFO_R_W  = 116
    WHO_AM_I  = 117
    XA_OFFSET_H  = 119
    XA_OFFSET_L  = 120
    YA_OFFSET_H  = 122
    YA_OFFSET_L  = 123
    ZA_OFFSET_H  = 125
    ZA_OFFSET_L  = 126

# 音声鳴らす用関数
def SE_wav(pass_name): #pass_name example : "/sd/ding.wav"

    fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
    spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
    spk_sd.value(1) #Enable the SPK output

    fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
    fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
    fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

    wav_dev = I2S(I2S.DEVICE_0)

    try:
        player = audio.Audio(path = pass_name )
        player.volume(100)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
    except:
        pass

    spk_sd.value(0) #Disable the SPK output

# 6軸センサ( I2C I/F )を動かす
# M5stickV 内蔵の I2C デバイスを検索する。(アドレスをコンソール上に表示)
def check_I2C_add():
    i2c_scan = I2C(I2C.I2C0, freq=100000, scl=28, sda=29)   # クラス設定
    devices = i2c_scan.scan()
    print( "I2C address is" , devices )
    i2c_scan.__del__    # クラス解放

# アドレス 104(dec) = MPU6886 であること前提
def init():
    # 初期設定
    ## 読み込みパラメータ設定
    memaddr = MPU6886_regmap.SL_ADD # スレーブアドレス
    length = 1  # 操作バイト数(dec)
    read_buf = bytearray([length])  # 1byteのbytearrayセット

    # I2C初期セッティングでクラス呼び出し
    i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29, timeout=1000)
    # 設定
    i2c.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, 0x80, mem_size=8)
    time.sleep(0.01)    # 0.01s sleep
    # Step 1: Ensure that Accelerometer is running
    i2c.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, 0x00, mem_size=8)
    i2c.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_2, 0x07, mem_size=8)
    time.sleep(0.01)
    # Step 2: Set Accelerometer LPF bandwidth to 218.1 Hz
    i2c.writeto_mem(memaddr, MPU6886_regmap.ACCEL_CONFIG2, 0x01, mem_size=8)
    time.sleep(0.01)
    # Step 3: Enable Motion Interrupt
    i2c.writeto_mem(memaddr, MPU6886_regmap.INT_ENABLE, 0xE0, mem_size=8)
    time.sleep(0.01)
    # Step 4: Set Motion Threshold
    i2c.writeto_mem(memaddr, MPU6886_regmap.ACCEL_WOM_X_THR, 0xF0, mem_size=8)
    i2c.writeto_mem(memaddr, MPU6886_regmap.ACCEL_WOM_Y_THR, 0xF0, mem_size=8)
    i2c.writeto_mem(memaddr, MPU6886_regmap.ACCEL_WOM_Z_THR, 0x10, mem_size=8)
    time.sleep(0.01)
    # Step 5: Enable Accelerometer Hardware Intelligence
    i2c.writeto_mem(memaddr, MPU6886_regmap.ACCEL_INTEL_CTRL, 0xC0, mem_size=8)
    time.sleep(0.01)
    # Step 6: Set Frequency of Wake-up
    i2c.writeto_mem(memaddr, MPU6886_regmap.SMPLRT_DIV, 0xC0, mem_size=8)
    time.sleep(0.01)
    # Step 7: Enable Cycle Mode (Accelerometer Low-Power Mode )
    i2c.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, 0xA0, mem_size=8)
    time.sleep(0.01)
    print("clear")

    while 1:
        try:
            read = i2c.readfrom_mem( memaddr, MPU6886_regmap.ACCEL_XOUT_H, 2 )
            print(read)
            time.sleep(0.1)
        except:
            err_counter = err_counter + 1
            if err_counter == 20:
                lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)   
            time.sleep(0.1)
            continue

    i2c.__del__    # クラス解放


# アドレス 104(dec) = MPU6886 であること前提
# 動作テスト
def test():

    # I2C初期セッティングでクラス呼び出し
    i2c_test = I2C(I2C.I2C0, freq=400000, scl=28, sda=29, timeout=1000)

    memaddr = MPU6886_regmap.SL_ADD # スレーブアドレス

    tempdata = 0x00
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, bytearray([tempdata]))
    time.sleep_ms(10)

    tempdata = 0x01<<7
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, bytearray([tempdata]))
    time.sleep_ms(10)

    tempdata = 0x01<<0
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.PWR_MGMT_1, bytearray([tempdata]))
    time.sleep_ms(10)

    tempdata = 0x10
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.ACCEL_CONFIG, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x18
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.GYRO_CONFIG, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x01
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.CONFIG, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x05
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.SMPLRT_DIV, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x00
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.INT_ENABLE, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x00
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.ACCEL_CONFIG2, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x00
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.USER_CTRL, bytearray([tempdata]))
    time.sleep_ms(1)
    tempdata = 0x00
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.FIFO_EN, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x22
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.INT_PIN_CFG, bytearray([tempdata]))
    time.sleep_ms(1)

    tempdata = 0x01
    i2c_test.writeto_mem(memaddr, MPU6886_regmap.INT_ENABLE, bytearray([tempdata]))
    time.sleep_ms(100)

    aRes = 8.0/32768.0
    gRes = 2000.0/32768.0
    kira_flag = 0
    while True:
        time.sleep_ms(100)
        accel = i2c_test.readfrom_mem(memaddr, MPU6886_regmap.ACCEL_XOUT_H, 6)
        accel_x = (accel[0]<<8 | accel[1])
        accel_y = (accel[2]<<8 | accel[3])
        accel_z = (accel[4]<<8 | accel[5])

        #負の数に変換
        if accel_x>32768:
            accel_x=accel_x-65536
        if accel_y>32768:
            accel_y=accel_y-65536
        if accel_z>32768:
            accel_z=accel_z-65536
        accel_array = [accel_x*aRes, accel_y*aRes, accel_z*aRes]

        if accel_array[2] >= 2 :
            SE_wav("/sd/ding.wav")
            kira_flag = 1

        gyro = i2c_test.readfrom_mem(memaddr, MPU6886_regmap.GYRO_XOUT_H, 6)
        gyro_x = (gyro[0]<<8 | gyro[1])
        gyro_y = (gyro[2]<<8 | gyro[3])
        gyro_z = (gyro[4]<<8 | gyro[5])

        #負の数に変換
        if gyro_x>32768:
            gyro_x=gyro_x-65536
        if gyro_y>32768:
            gyro_y=gyro_y-65536
        if gyro_z>32768:
            gyro_z=gyro_z-65536

        gyro_array = [gyro_x*gRes, gyro_y*gRes, gyro_z*gRes]

        if (kira_flag == 1) and (accel_array[1] > 1.35 ):
            SE_wav("/sd/kira.wav")
            kira_flag = 0

        temp = i2c_test.readfrom_mem(memaddr, MPU6886_regmap.TEMP_OUT_H, 2)
        temp_dat = (temp[0]<<8 | temp[1])
        print(accel_array,"_",gyro_array,"_",temp_dat)

    i2c_test.__del__    # クラス解放    
