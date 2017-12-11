import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

import struct
import time as Time
import os

#graph initialization
style.use('fivethirtyeight')

n = 200  #sample size
freq = 15 #frequency in Hz
time_period = 1.0/freq
time = 2.0* time_period
wn = 40

x= []
y= []

#yf = np.fft.fft(y)/n
#yf = yf[range(n/2)]

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
port = "/dev/ttyUSB0"
ser = serial.Serial(port, 9600 )

ser.close()
ser.open()

t=0
now = Time.monotonic()

while True:
    try:
        data_in = ser.readline()
        data_in = data_in.decode()
        if('\x00' == data_in[:1] ):
            #data_in = data_in[3:]
            data_in = data_in.split("\x00")[1];
            print("\\x00 detected")
        
        try:
          data_in = float ( ( data_in ).split("\\n")[0])
        except:
          pass
         
        before = t  
        t = Time.monotonic() - now
        after = t
        if( (after-before)/0.1 > 2.0):
            print("delay")
        
        #print("time:",t)
        if len(x) >=n :
            x = x[1:] + [t]
            y = y[1:] + [data_in]
            freq = n/(x[n-1] - x[0])
        else:
            x = x+[t]
            y = y+[data_in]
        
        #print(freq)
        
        #update real data
        axes1.lines[0].remove()
        axes1.plot(x,y,color='red', linewidth= 1, linestyle ='dotted')
        axes1.set_xlim( min(x),max(x) )
        #axes1.relim()
        axes1.autoscale_view()
        
        #update smoothing
        axes1.lines[0].remove()
        poly_deg = 10
        coefs = np.polyfit(x,y,poly_deg)
        x_poly = np.linspace(min(x),max(x),n*100)
        y_poly = np.polyval(coefs,x_poly )
        axes1.plot(x_poly ,y_poly,color='green', linewidth= 1, linestyle ='-')
        #axes1.set_xlim( min(x),max(x) )
        axes1.relim()
        axes1.autoscale_view()
        
        #update fft
        if(len(x) >= n):
          yff = np.fft.fft(y)
          yf = np.fft.fft(y)/n
          yf = yf[range(n//2)]
          #xf = np.linspace(0.0,1.0/(2.0/800.0),n//2)
          xf = (np.arange(n)/n*freq)[range(n//2)]
          
          axes[1].lines[0].remove()
          axes[1].plot(xf,abs(yf),'b',linewidth=1)
          axes[1].set_ylim(-1.0,1.0)
          
          ydel = yf
          ydel[0:wn] = 0.0
          axes[1].lines[0].remove()
          axes[1].plot(xf,abs(ydel),'r',linewidth=1)
          #update inverse fft
          axes1.lines[0].remove()
          yff[wn:-wn] = 0.0
          yff = np.fft.ifft(yff)
          #yff = np.fft.ifft(np.append(yff[:3], [0.0]*(n-3)))
          axes1.plot(x,yff,color='blue',linewidth=1)
        else:
          axes1.lines[0].remove()
          axes1.plot([],[])
          
        plt.pause(0.001)
    except KeyboardInterrupt:
        break

ser.close()
