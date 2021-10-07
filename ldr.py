import busio
import digitalio
import board
import time
import threading    
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

def initialSetup():
    light_thread = threading.Thread(target=ldrThread)
    temp_thread = threading.Thread(target=tempThread)
    return [light_thread,temp_thread]

def ldrThread():
    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    while True:
        chan = AnalogIn(mcp, MCP.P0)
        print(f"Light value {chan.value} voltage value {chan.voltage}")
        time.sleep(4)
    
    return[chan.value,chan.voltage]

def tempThread():
    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    while True:
        chan = AnalogIn(mcp, MCP.P3)
        print(f"Temperature value {chan.value} voltage value {chan.voltage}")
        time.sleep(4)

    return[chan.value,chan.voltage]

if __name__ == "__main__":
    [light_thread,temp_thread] = initialSetup()
    
    temp_thread.start()
    light_thread.start()
    