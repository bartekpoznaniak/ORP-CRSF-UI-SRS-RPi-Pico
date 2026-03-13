import utime
import ustruct

class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()

    def reset(self):
        self.write_8(0x00, 0x00) # MODE1

    def freq(self, freq):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)
        
        oldmode = self.read_8(0x00) # MODE1
        newmode = (oldmode & 0x7F) | 0x10 # sleep
        self.write_8(0x00, newmode) # go to sleep
        self.write_8(0xFE, prescale) # set prescale
        self.write_8(0x00, oldmode)
        utime.sleep_us(5000)
        self.write_8(0x00, oldmode | 0xa1) # mode 1, autoincrement on

    def duty(self, index, value):
        # value powinno być od 0 do 4095
        self.i2c.writeto_mem(self.address, 0x06 + 4 * index, ustruct.pack('<HH', 0, value))

    def write_8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def read_8(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]
