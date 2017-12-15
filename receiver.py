import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

import struct
import time as Time
import os

#all possible serial ports
import serial.tools.list_ports
ports = list( serial.tools.list_ports.comports() )
for p in ports:
    print(p)

x = []
y = []
n = 200
freq = 15
wn = 10 #number of wave not filtered
gain = 1 #gain of ADC
poly_deg = 5 #smoothing degree
lim_maxy = 5.0
lim_miny = 0.0
lim_fft_maxy = 0.1
lim_fft_miny = -0.0005
x = []
y = []
    
def read_serial(ser):
    data_in = ser.readline()
    data_in = data_in.decode()
    if('\x00' == data_in[:1] ):
        #data_in = data_in[3:]
        data_in = data_in.split("\x00")[1];
        print("\\x00 detected")
    
    try:
        data_in = float ( ( data_in ).split("\\n")[0])
    except:
        #print("FLOATING CONVERSION ERROR!")
        return -1.0
        pass
    
    return data_in

def process(data):
    low = 0.0
    high = 4.096
    precision = 16 # 16-bit reading
    global gain
    data = low + (data/(2 ** (precision-1)-1)) * (high/gain)
    
    return data
    
def check_delay(t, now):
    before = t  
    t = Time.monotonic() - now
    after = t
    if( (after-before)/0.1 > 2.0):
        print("delay")
    
    #print("graph build time: "+str(after-before))
    return t

def update_x(t):
    global x
    x = x + [t]
    if( len(x) > n):
        x = x[1:]
    
def update_y(data):
    global y
    y = y + [data]
    if( len(y) >n ):
        y = y[1:]
        
def update_freq():
    global freq
    if len(x)>=n :
        freq = n/(x[n-1]-x[0])

#serial port initialization
#port = "/dev/ttyUSB0"
port = "COM4"
ser = serial.Serial(port, 9600 )

ser.close()
ser.open()

t=0
now = Time.monotonic()

while True:
    try:
        data_in = read_serial(ser)
        data_in = process(data_in)
        
        t = check_delay(t, now)
        
        update_x(t)
        update_y(data_in)
        update_freq()
        
        print(freq)
        
    except KeyboardInterrupt:
        break

ser.close()
