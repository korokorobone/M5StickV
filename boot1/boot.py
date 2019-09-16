import setting
import motion

# 起動時の画面を呼び出し
setting.boot_lcd()

#ペリフェラルセッティング
setting.boot_set_IF()

# センサのセッティング
motion.check_I2C_add()

#別音声呼び出しテスト
motion.SE_wav("/sd/pon.wav")

motion.SE_wav("/sd/kira.wav")

# MPU6680限定
motion.test()
