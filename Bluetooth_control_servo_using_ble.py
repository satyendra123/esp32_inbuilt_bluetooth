from machine import Pin
from machine import Timer
from time import sleep_ms
from machine import PWM
import time
import bluetooth

BLE_MSG = ""


class ESP32_BLE():
    def __init__(self, name):
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):        
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global BLE_MSG
        if event == 1: #_IRQ_CENTRAL_CONNECT 手机链接了此设备
            self.connected()
        elif event == 2: #_IRQ_CENTRAL_DISCONNECT 手机断开此设备
            self.advertiser()
            self.disconnected()
        elif event == 3: #_IRQ_GATTS_WRITE 手机发送了数据 
            buffer = self.ble.gatts_read(self.rx)
            BLE_MSG = buffer.decode('UTF-8').strip()
            
    def register(self):        
        service_uuid = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        reader_uuid = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        sender_uuid = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        services = (
            (
                bluetooth.UUID(service_uuid), 
                (
                    (bluetooth.UUID(sender_uuid), bluetooth.FLAG_NOTIFY), 
                    (bluetooth.UUID(reader_uuid), bluetooth.FLAG_WRITE),
                )
            ), 
        )

        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(services)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")


def buttons_irq(pin):
    led.value(not led.value())
    print('LED is ON.' if led.value() else 'LED is OFF')
    ble.send('LED is ON.' if led.value() else 'LED is OFF')


if __name__ == "__main__":
    ble = ESP32_BLE("ESP32BLE")

    # 检测boot按键
    but = Pin(0, Pin.IN)
    but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

    # 控制蓝色led
    led = Pin(2, Pin.OUT)
    
    # 控制舵机
    p15 = PWM(Pin(15))
    p15.freq(50)
    duty_num = 1638
    p15.duty_u16(1638)

    # 0度   p15.duty_u16(1638)
    # 90度  p15.duty_u16(4915)
    # 180度 p15.duty_u16(8192)

    while True:
        if BLE_MSG == 'read_LED':
            print(BLE_MSG)
            BLE_MSG = ""
            print('LED is ON.' if led.value() else 'LED is OFF')
            ble.send('LED is ON.' if led.value() else 'LED is OFF')
        elif BLE_MSG:
            print("接收到的信息：>>%s<<" % BLE_MSG)
            if BLE_MSG == "!B11:":  # 按下app上数字1
                duty_num += 100
                if duty_num > 8192:
                    duty_num = 8192
                print(duty_num)
                p15.duty_u16(duty_num)
            elif BLE_MSG == "!B219":  # 按下app上数字2
                duty_num -= 100
                if duty_num < 1638:
                    duty_num = 1638
                print(duty_num)
                p15.duty_u16(duty_num)
            elif BLE_MSG == "!B516":  # 按下app上up键
                p15.duty_u16(4915)
                duty_num = 4915
            elif BLE_MSG == "!B714":  # 按下app上left键
                p15.duty_u16(8192)
                duty_num = 8192
            elif BLE_MSG == "!B813":  # 按下app上right键
                p15.duty_u16(1638)
                duty_num = 1638
            BLE_MSG = ""
        sleep_ms(100)

