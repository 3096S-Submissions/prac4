
#    author :        Dylan Hellig and Pius Gumo
#    description :   Python Code to Make use of the SPI bus to read temperature and LDR
#                    values from a temp resistor and ldr sensor and display them on a pi-zero
#    date :          08/10/2021

import busio
import digitalio
import board
import time
import threading
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO 

# define global variables that will be shared across 
# the threads and different functions
global spi, cs, mcp
global sleep_time

# setup the adc and set default time
def initialSetup():
    global spi, cs, mcp, sleep_time

    sleep_time = 1

    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)

# function to change the sleep_time when a button press event is called
def increaseSleepTime(channel):
    global sleep_time

    if sleep_time == 1:
        sleep_time = 5
    elif sleep_time == 5:
        sleep_time = 10
    elif sleep_time == 10:
        sleep_time = 1
    else:
        sleep_time = 1

# button thread function that will be setup to detect when the button is pressed
def buttonsThread():
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(16, GPIO.RISING, callback=increaseSleepTime)

# function to convert temperature voltage to actual degrees
def convertTempVoltageToDegrees(temp_voltage):
    # temperature coefficient defined according to the datasheet
    tC = 19.5

    # voltage at 0_degrees celsius defined according to the datasheet
    v_0 = 400

    # ambient temperature calculated from V_out = tA * tC + v_0
    tA = abs(temp_voltage - 400)/tC

    return tA

# thread that will read the temperature and ldr values
def readTempLightThread():
    global start_time,sleep_time

    # start time is defined as when this thread was created,
    # this is used to calculate the elapsed time when the values are read
    start_time = time.perf_counter()

    # printing the top level row of data columns
    print("{:^12s} | {:^12s} | {:^12s} | {:^12s}".format("Runtime","Temp Reading","Temp","Light Reading"))

    # while loop to read values until the Ctr + C key is depressed
    while True:

        # calculate the runtime when a value is read
        runtime = time.perf_counter() - start_time

        # read temperature value and voltage
        [temperature_value, temperature_voltage] = readTempearture()

        # read ldr value and voltage
        [light_value, light_voltage] = readLDR()

        # print the values in a row and format accordingly
        print("{:11d}s | {:^12.3f} | {:^12.1f} | {:^12.3f}".format(round(runtime),temperature_value,convertTempVoltageToDegrees(temperature_voltage),light_value))

        # sleep for the defined runtime
        time.sleep(sleep_time)


# function to read the current values of the LDR
def readLDR():
    chan = AnalogIn(mcp, MCP.P2)

    return [chan.value, chan.voltage]

# function to read the current values of temperature
def readTempearture():
    chan = AnalogIn(mcp, MCP.P1)

    return [chan.value, chan.voltage]


if __name__ == "__main__":
    initialSetup()

    adc_thread = threading.Thread(target=readTempLightThread)
    buttons_thread = threading.Thread(target=buttonsThread)

    adc_thread.start()
    buttons_thread.start()
