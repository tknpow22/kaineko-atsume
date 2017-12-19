# -*- coding: utf-8 -*-

import io
import os
import requests
import datetime
import time
import RPi.GPIO as GPIO
import picamera

# 赤外線センサーモジュールで動きを感知した際に、明るさが充分あれば、カメラで撮影し、画像をサーバにアップロードする
#
# 使用した部品は以下のとおり:
#     - 赤外線センサーモジュール: HC-SR501: 赤外線センサーと制御IC BISS0001 を組み合わせたモジュール:
#         VCC は 5V に接続のこと。3.3V に接続した場合、おかしな動きをすることがあった
#     - フォトレジスタ: 明るさを検知する。A/D コンバーター に接続して使用する
#     - A/D コンバーター: MCP3008: 接続されたフォトレジスタの値を取得する
#     - カメラ: The Raspberry Pi Camera Module v1.3
#     - LED: カメラ撮影時および画像アップロード時に点灯させる

# 画像ファイルのアップロード先
IMG_UPLOAD_URL = 'http://192.168.1.4:8080/upload'

# カメラで撮影するかどうかのしきい値
# 要調整: フォトレジスタから取得した値 ＜ PVALUE_THRESHOLD の場合に、撮影を行う
#         フォトレジスタの値は明るいと値が小さくなり、暗いと大きくなる
PVALUE_THRESHOLD = 850

# 赤外線センサモジュールから状態を取得する
class Pir:
    def __init__(self):
        self.pin = 17
        GPIO.setup(self.pin, GPIO.IN)

    def cleanup(self):
        pass

    # 何かを感知したか
    def detected(self):
        return GPIO.input(self.pin) == GPIO.HIGH

# 明るさを取得する
# NOTE: GPIO と MCP3008 間の配線は SPI (Serial Peripheral Interface) を利用する場合と同じにしているが、
#       別の GPIO ポートでも動作する。
#       ※MCP3008 のデータシート SERIAL COMMUNICATION に記載された SPI 互換の方式で行う。
class Daylight:
    def __init__(self):
        self.pin_clock = 11 # SPI0 SCLK: Serial Peripheral Serial Clock: Output
        self.pin_mosi = 10  # SPI0 MOSI: Master Output Slave Input: Master Output
        self.pin_miso = 9   # SPI0 MISO: Master Input Slave Output: Master Input
        self.pin_cs = 8     # SPI0 CE0: CS(SS): Slave Select: 送受信中は Low
        self.channel = 0    # CH: 0 - 7

        GPIO.setup(self.pin_clock, GPIO.OUT)
        GPIO.setup(self.pin_mosi, GPIO.OUT)
        GPIO.setup(self.pin_miso, GPIO.IN)
        GPIO.setup(self.pin_cs, GPIO.OUT)

    def cleanup(self):
        pass

    # 明るさが充分あるか: OK なら True
    def enough(self):
        pvalue = self.read_pvalue()
        ##print('enough(): pvalue: [%d]' % (pvalue))

        if pvalue < PVALUE_THRESHOLD:
            return True

        return False

    # MCP3008 から指定チャンネルに接続されたフォトレジスタの値を取得する
    # ※フォトレジスタが MCP3008 の指定のチャンネルにつながっていること
    def read_pvalue(self):

        # 前準備
        GPIO.output(self.pin_cs, GPIO.HIGH)
        GPIO.output(self.pin_clock, GPIO.LOW)

        # 開始
        GPIO.output(self.pin_cs, GPIO.LOW)

        #
        # データ要求送信
        #
        # クロックで同期させながら、MOSI から送信する
        #
        # |B4|B3|D2|D1|D0|
        #     B4: 開始: 1
        #     B3: Single/Diff: 1: single-ended, 0: differential
        #     D2 - D0: 000: CH0, 001: CH1, 010: CH2, ... 111: CH7
        control_bits = 0x18             # 開始(1), single-ended(1)
        control_bits |= self.channel    # チャンネル

        # 左に寄せておく
        control_bits <<= 3

        for i in range(5):
            if (control_bits & 0x80):
                GPIO.output(self.pin_mosi, GPIO.HIGH)
            else:
                GPIO.output(self.pin_mosi, GPIO.LOW)

            control_bits <<= 1

            # クロックに同期のための信号を送る
            GPIO.output(self.pin_clock, GPIO.HIGH)
            GPIO.output(self.pin_clock, GPIO.LOW)

        # |sample| の終了
        GPIO.output(self.pin_clock, GPIO.HIGH)
        GPIO.output(self.pin_clock, GPIO.LOW)

        #
        # データ受信
        #
        # クロックで同期させながら、MISO から受信する
        #
        # |nb|B9|B8|B7|B6|B5|B4|B3|B2|B1|B0|
        #     nb: Null Bit
        #     B9 - B0: データ

        pvalue = 0

        for i in range(11):
            pvalue <<= 1
            if (GPIO.input(self.pin_miso) == GPIO.HIGH):
                pvalue |= 0x1

            # クロックに同期のための信号を送る
            GPIO.output(self.pin_clock, GPIO.HIGH)
            GPIO.output(self.pin_clock, GPIO.LOW)

        # 終了
        GPIO.output(self.pin_cs, GPIO.HIGH)

        # Null Bit は念のためマスクして捨てる
        ##print('%x' % pvalue)
        pvalue &= 0x3ff
        ##print('%x' % pvalue)

        return pvalue

# LED を操作する
class Led:
    def __init__(self):
        self.pin = 18
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()

    def cleanup(self):
        self.off()

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

# メイン
class Main:

    def __init__(self):
        self.camera = picamera.PiCamera()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.daylight = Daylight()
        self.pir = Pir()
        self.led = Led()

    def cleanup(self):
        self.daylight.cleanup()
        self.pir.cleanup()
        self.led.cleanup()

        GPIO.cleanup()

    # カメラで撮影を行い、画像データのストリームを返す
    def take_picture(self):
        stream = io.BytesIO()
        ##self.camera.resolution = (180, 120)
        self.camera.capture(stream, 'jpeg')
        stream.seek(0)

        return stream

    # 画像データをサーバにアップロードする
    def upload_picture(self, stream):
        now = datetime.datetime.now()
        filename = now.strftime("%Y%m%d%H%M%S") + '.jpg'
        result = 'failure'

        try:
            response = requests.post(IMG_UPLOAD_URL, files={'picture': (filename, stream, 'image/jpeg')}, data={'uploadfrom': 'take_picture'})
            result = response.text
        except Exception as ex:
            print(ex.args)

        print('upload_picture(): upload: [%s]: [%s]' % (result, filename))

    # メイン処理: 終了するには Ctrl + C
    def run(self):
        while True:
            if self.pir.detected() and self.daylight.enough():

                self.led.on()

                try:

                    with self.take_picture() as stream:
                        self.upload_picture(stream)

                except Exception as ex:
                    print(ex.args)

                self.led.off()

            time.sleep(1)

# スタートアップ
if __name__ == '__main__':
    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        main.cleanup()
        ##print 'cleanup done'
