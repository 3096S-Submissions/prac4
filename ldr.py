import busio
import digitalio
import board
import time
import threading
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library

global spi, cs, mcp
global sleep_time


def initialSetup():
    global spi, cs, mcp, sleep_time

    sleep_time = 10

    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)


def increaseSleepTime(channel):
    global sleep_time

    if sleep_time == 1:
        sleep_time = 5
    elif sleep_time == 5:
        sleep_time == 10
    elif sleep_time == 10:
        sleep_time == 1


def buttonsThread():
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(16, GPIO.RISING, callback=increaseSleepTime)


def timerThread():
    global start_time,sleep_time
    start_time = time.perf_counter()

    while True:
        runtime = time.perf_counter() - start_time
        print(f"{runtime}s", end="")

        # read temperature value and voltage
        [temperature_value, temperature_voltage] = readTempearture()

        # read light value and voltage
        [light_value, light_voltage] = readLDR()

        print(f" {temperature_value} \t {light_value} ")

        time.sleep(sleep_time)


def readLDR():
    chan = AnalogIn(mcp, MCP.P1)

    return [chan.value, chan.voltage]


def readTempearture():
    chan = AnalogIn(mcp, MCP.P1)

    return [chan.value, chan.voltage]


if __name__ == "__main__":
    initialSetup()

    start_time = time.perf_counter()

    adc_thread = threading.Thread(target=timerThread)
    buttons_thread = threading.Thread(target=buttonsThread)

    adc_thread.start()
    buttons_thread.start()
