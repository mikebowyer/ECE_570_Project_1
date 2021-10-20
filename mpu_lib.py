from smbus2 import SMBus
import time


class mpu_6050:
    # registers
    r_PWR_MGT_1 = 0x6B
    r_PWR_MGT_2 = 0x6C

    r_TEMP_HIGH = 0x41
    r_TEMP_LOW = 0x42

    r_GYRO_CONFIGURATION = 0x1B
    r_ACCEL_CONFIGURATION = 0x1C

    r_GYRO_X_DATA = 0x43
    r_GYRO_Y_DATA = 0x45
    r_GYRO_Z_DATA = 0x47

    r_ACCEL_X_DATA = 0x3B
    r_ACCEL_Y_DATA = 0x3D
    r_ACCEL_Z_DATA = 0x3F

    def __init__(self):
        self.bus = SMBus(1)
        self.address = 0x68
        print("CONFIGURATION: Waking device up")
        self.bus.write_byte_data(self.address, self.r_PWR_MGT_1, 0x00)
        self.gyroRange = 250
        self.set_gyro_config(self.gyroRange)
        self.accelRange = 2
        self.set_accel_config(self.accelRange)

    def readTemp(self, farienheit):
        # Open i2c bus 1 and read one byte from address 80, offset 0
        temp_high = self.bus.read_byte_data(self.address, self.r_TEMP_HIGH)
        temp_low = self.bus.read_byte_data(self.address, self.r_TEMP_LOW)

        value = (temp_high << 8) + temp_low
        if value >= 0x8000:
            value = -((65535 - value) + 1)

        returnVal = (value / 340.0) + 36.53
        if farienheit:
            returnVal = (returnVal * 1.8) + 32

        return returnVal

    def set_gyro_config(self, range):
        print("CONFIGURATION: Setting gyro range to " + str(range))
        self.bus.write_byte_data(self.address, self.r_GYRO_CONFIGURATION, 0x00)

        self.gyroRange = range

        write_byte = 0x00
        if range == 250:
            write_byte = 0x00
            self.gyroRangeModifer = 131.0
        elif range == 500:
            write_byte = 0x08
            self.gyroRangeModifer = 65.5
        elif range == 1000:
            write_byte = 0x10
            self.gyroRangeModifer = 32.8
        elif range == 2000:
            write_byte = 0x18
            self.gyroRangeModifer = 16.4

        self.bus.write_byte_data(self.address, self.r_GYRO_CONFIGURATION, write_byte)

    def set_accel_config(self, range):
        print("CONFIGURATION: Setting accel range to " + str(range))
        self.bus.write_byte_data(self.address, self.r_ACCEL_CONFIGURATION, 0x00)

        self.accelRange = range

        write_byte = 0x00
        if range == 2:
            write_byte = 0x00
            self.accelRangeModifier = 16384.0
        elif range == 4:
            write_byte = 0x08
            self.accelRangeModifier = 8192.0
        elif range == 8:
            write_byte = 0x10
            self.accelRangeModifier = 4096.0
        elif range == 16:
            write_byte = 0x1
            self.accelRangeModifier = 2048.0

        self.bus.write_byte_data(self.address, self.r_ACCEL_CONFIGURATION, write_byte)

    def read_two_bytes(self, reg):
        # Read the data from the registers
        msbyte = self.bus.read_byte_data(self.address, reg)
        lsbyte = self.bus.read_byte_data(self.address, reg + 1)

        value = (msbyte << 8) + lsbyte

        if value >= 0x8000:
            return -((65535 - value) + 1)
        else:
            return value

    def get_accel_data(self, g=False):
        x = self.read_two_bytes(self.r_ACCEL_X_DATA)
        y = self.read_two_bytes(self.r_ACCEL_Y_DATA)
        z = self.read_two_bytes(self.r_ACCEL_Z_DATA)

        x = x / self.accelRangeModifier
        y = y / self.accelRangeModifier
        z = z / self.accelRangeModifier

        if g is True:
            return {"x": x, "y": y, "z": z}
        elif g is False:
            x = x * 9.80665
            y = y * 9.80665
            z = z * 9.80665
            return {"x": x, "y": y, "z": z}

    def get_gyro_data(self):
        x = self.read_two_bytes(self.r_GYRO_X_DATA)
        y = self.read_two_bytes(self.r_GYRO_Y_DATA)
        z = self.read_two_bytes(self.r_GYRO_Z_DATA)

        x = x / self.gyroRangeModifer
        y = y / self.gyroRangeModifer
        z = z / self.gyroRangeModifer

        return {"x": x, "y": y, "z": z}


if __name__ == "__main__":
    print("Hello")  # next section explains the use of sys.exit

    sensor = mpu_6050()

    while True:
        print("Temperature in Farenheit: " + str(sensor.readTemp(True)))
        accel_data = sensor.get_accel_data(True)
        print("Accelerometer X: " + str(accel_data["x"]) + " Meter / s^2")
        print("Accelerometer Y: " + str(accel_data["y"]) + " Meter / s^2")
        print("Accelerometer Z: " + str(accel_data["z"]) + " Meter / s^2")
        gyro_data = sensor.get_gyro_data()
        print("Gyro X: " + str(gyro_data["x"]) + " Degree / Second")
        print("Gyro Y: " + str(gyro_data["y"]) + " Degree / Second")
        print("Gyro Z: " + str(gyro_data["z"]) + " Degree / Second")
        time.sleep(2)
