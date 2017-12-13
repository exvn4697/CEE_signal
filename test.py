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

#graph initialization
style.use('fivethirtyeight')

n = 200  #sample size
freq = 15 #frequency in Hz
time_period = 1.0/freq
time = 2.0* time_period
wn = 10 #number of wave not filtered
gain = 1 #gain of ADC
poly_deg = 5 #smoothing degree

x= []
y= []

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
        print("FLOATING CONVERSION ERROR!")
        return -1.0
        pass
    
    return data_in

def process(data):
    low = 0
    high = 5
    precision = 16 # 16-bit reading
    global gain
    data = low + (data/(2 ** (precision-1))) * (high/gain)
    
    return data
    
def check_delay(t, now):
    before = t  
    t = Time.monotonic() - now
    after = t
    if( (after-before)/0.1 > 2.0):
        print("delay")
    
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
        

#data graph
fig, axes = plt.subplots(2,1)
axes[0].plot(x,y)
axes[0].plot([],[]) #smoothing dummy
axes[0].plot([],[]) #inverse fft dummy
axes[0].set_xlabel('Time')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Time Signal')
axes1 = axes[0]

#fft
axes[1].plot(x,y)
axes[1].plot([],[]) #delete dummy
axes[1].set_xlabel('Freq (Hz)')
axes[1].set_ylabel('|Y(freq)|')
axes[1].set_title('FFT on Time Signal')

plt.tight_layout()
plt.ion()
plt.show()

#serial port initialization
#port = "/dev/ttyUSB0"
port = "COM4"
ser = serial.Serial(port, 9600 )

ser.close()
ser.open()

t=0
now = Time.monotonic()
cnt = 0

while True:
    try:
        data_in = read_serial(ser)
        data_in = process(data_in)
        
        t = check_delay(t, now)
        
        update_x(t)
        update_y(data_in)
        update_freq()
        
        cnt += 1
        if cnt%100 == 50 :
          print(freq)
        
    except KeyboardInterrupt:
        break

ser.close()
