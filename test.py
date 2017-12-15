import matplotlib
matplotlib.use('Qt4Agg')

import numpy as np
import time
import matplotlib.pyplot as plt
import serial

#all constants used
ser = ""
port = ""
line = 0
n = 200  #sample size
freq = 15 #frequency in Hz
wn = 10 #number of wave not filtered
gain = 1 #gain of ADC
poly_deg = 5 #smoothing degree
lim_maxy = 5.0
lim_miny = 0.0
lim_fft_maxy = 0.1
lim_fft_miny = -0.0005
x = []
y = []

fig, axes = plt.subplots(2,1,figsize=(9,7))
ax = axes[0]
line, = ax.plot(y)
line2, = axes[1].plot(y,'-g')
axes[0].set_ylim(-5,10)
axes[0].set_xlim(0,10)
axes[1].set_ylim(-5,10)
axes[1].set_xlim(0,10)
plt.show(block=False)
fig.canvas.draw()

tstart = time.time()
num_plots = 0
ser = serial.Serial('COM4',9600)
ser.close()
ser.open()

t = 0
now = time.monotonic()

while time.time()-tstart < 5:
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
        low = 0.0
        high = 4.096
        precision = 16 # 16-bit reading
        global gain
        data = low + (data/(2 ** (precision-1)-1)) * (high/gain)
        
        return data
        
    def check_delay(t, now):
        before = t  
        t = time.monotonic() - now
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
    
    data_in = read_serial(ser)
    data_in = process(data_in)
    
    t = check_delay(t, now)
    
    update_x(t)
    update_y(data_in)
    update_freq()
    
    line.set_xdata(x)
    line.set_ydata(y)
    yff = np.fft.fft(y)
    yf = np.fft.fft(y)/200
    yff = np.fft.ifft(yff)
    ax.draw_artist(ax.patch)
    ax.draw_artist(line)
    
    line2.set_data(x,yff)
    axes[1].draw_artist(axes[1].patch)
    axes[1].draw_artist(line2)
    fig.canvas.update()
    fig.canvas.flush_events()
    num_plots += 1

ser.close()
print(num_plots/5)