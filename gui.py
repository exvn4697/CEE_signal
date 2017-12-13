import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.animation as animation

import struct
import time as Time
import os

import tkinter
import matplotlib
matplotlib.use("TkAgg")
style.use('fivethirtyeight')
plt.rc('xtick',labelsize=12)
plt.rc('ytick',labelsize=12)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

root = tkinter.Tk(  )
root.wm_state('zoomed')

#all constants used
ser = ""
port = ""
line = 0
n = 200  #sample size
freq = 15 #frequency in Hz
time_period = 1.0/freq
time = 2.0* time_period
wn = 10 #number of wave not filtered
gain = 1 #gain of ADC
poly_deg = 5 #smoothing degree
lim_maxy = 5.0
lim_miny = 0.0
lim_fft_maxy = 0.1
lim_fft_miny = -0.0005
x = []
y = []

#all possible serial ports
import serial.tools.list_ports
ports = list( serial.tools.list_ports.comports() )
tkinter.Label(root, text="Open Port: ").grid(row=line, column=0, sticky=tkinter.W)
line += 1
for p in ports:
    tkinter.Label(root, text=str(line)+". "+str(p)).grid(row=line,column=0)
    line += 1
 
def connect():
    global root
    global ser
    global port
    global port_var
    port = port_var.get()
    try:
        ser = serial.Serial(port, 9600)
        ser.close()
        ser.open()
        connect_var.set("Connected to "+port)
    except:
        connect_var.set("Can not connect to "+port)
    
    root.update()
    #plt.pause(1)
    return
    
tkinter.Label(root, text="select port").grid(row=0,column=1)
port_var = tkinter.StringVar()
port_var.set("COM4")
tkinter.Entry(root, textvariable=port_var).grid(row=1,column=1)
tkinter.Button(root, text = "connect to port", command = connect).grid(row=0,column=2, rowspan=line, padx=5, pady=5 )

if line<2 :
  line = 2
  
connect_var = tkinter.StringVar()
connect_var.set("")
tkinter.Label(root, textvariable=connect_var).grid(row = line,column=0,columnspan=3,sticky=tkinter.N)
line += 1

tkinter.Label(root, textvariable="").grid(row = line,column=0,columnspan=3,sticky=tkinter.N)
line += 1

tkinter.Label(root, text="GAIN :").grid(row=line+0,column=0)
tkinter.Label(root, text="Polynomial Degree :").grid(row=line+1,column=0)
tkinter.Label(root, text="Filtered frequency :").grid(row=line+2,column=0)
tkinter.Label(root, text="maximum y-axis :").grid(row=line+3,column=0)
tkinter.Label(root, text="minimum y-axis :").grid(row=line+4,column=0)
tkinter.Label(root, text="maximum fft y-axis :").grid(row=line+5,column=0)
tkinter.Label(root, text="minimum fft y-axis :").grid(row=line+6,column=0)

gain_var = tkinter.StringVar()
gain_var.set(gain)
tkinter.Entry(root, textvariable=gain_var).grid(row=line+0,column=1)
poly_deg_var = tkinter.StringVar()
poly_deg_var.set(poly_deg)
tkinter.Entry(root, textvariable=poly_deg_var).grid(row=line+1,column=1)
filter_freq_var = tkinter.StringVar()
filter_freq_var.set(wn)
tkinter.Entry(root, textvariable=filter_freq_var).grid(row=line+2,column=1)
maxy_var = tkinter.StringVar()
maxy_var.set(lim_maxy)
tkinter.Entry(root, textvariable=maxy_var).grid(row=line+3,column=1)
miny_var = tkinter.StringVar()
miny_var.set(lim_miny)
tkinter.Entry(root, textvariable=miny_var).grid(row=line+4,column=1)
fft_maxy_var = tkinter.StringVar()
fft_maxy_var.set(lim_fft_maxy)
tkinter.Entry(root, textvariable=fft_maxy_var).grid(row=line+5,column=1)
fft_miny_var = tkinter.StringVar()
fft_miny_var.set(lim_fft_miny)
tkinter.Entry(root, textvariable=fft_miny_var).grid(row=line+6,column=1)

def apply_setting():
  global filter_freq_var
  global poly_deg_var
  global gain_var
  global miny_var
  global maxy_var
  global fft_miny_var
  global fft_maxy_var
  
  global gain
  global poly_deg
  global wn
  global lim_maxy
  global lim_miny
  global lim_fft_maxy
  global lim_fft_miny
  
  try:
    gain = int(gain_var.get() )
  except:
    pass
  
  try:
    poly_deg = int(poly_deg_var.get() )
  except:
    pass
   
  try:
    wn = int(filter_freq_var.get() )
  except:
    pass

  try:
    lim_maxy = float(maxy_var.get() )
  except:
    pass
    
  try:
    lim_miny = float(miny_var.get() )
  except:
    pass
    
  try:
    lim_fft_maxy = float(fft_maxy_var.get() )
  except:
    pass
    
  try:
    lim_fft_miny = float(fft_miny_var.get() )
  except:
    pass
  
  axes[0].set_ylim(lim_miny,lim_maxy)
  axes[1].set_ylim(lim_fft_miny,lim_fft_maxy)
  
  return

tkinter.Button(root, text="Apply Setting", command = apply_setting).grid(row=line+0, column=2, columnspan=2, rowspan=7,
               sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
               
#tkinter.Label(root, text="PUT GRAPH HERE !").grid(row=line+3, column=0,rowspan=5, columnspan=5, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
lines = []
fig, axes = plt.subplots(2,1,figsize=(9,7))
plt.close('all')
lines += [axes[0].plot(x, y, color='red', linewidth= 1, linestyle ='dotted', animated=True)[0]]
lines += [axes[0].plot([], [], color='green', linewidth= 1, linestyle ='-', animated=True)[0]] #smoothing dummy
lines += [axes[0].plot([], [], color='blue',linewidth=1, animated=True)[0]] #inverse fft dummy
axes[0].set_xlabel('Time',size=12)
axes[0].set_ylabel('Voltage',size=12)
axes[0].set_title('Time Signal',size=12)
axes[0].set_ylim(lim_miny,lim_maxy)
axes1 = axes[0]

#fft
lines += [axes[1].plot(x, y, 'b',linewidth=1, animated=True)[0]]
lines += [axes[1].plot([], [], 'r',linewidth=1, animated=True)[0]] #filtered fft dummy
axes[1].set_xlabel('Freq (Hz)',size=12)
axes[1].set_ylabel('|Y(freq)|',size=12)
axes[1].set_title('FFT on Time Signal',size=12)
axes[1].set_xlim(0,20)
axes[1].set_ylim(lim_fft_miny,lim_fft_maxy)

graph = tkinter.LabelFrame(root, text="Graph", padx=5,pady=5)
graph.grid(row=0,column=4,rowspan=100,columnspan=100)
fig.tight_layout()
canvas = FigureCanvasTkAgg(fig, master=graph)
canvas.show()
#canvas.get_tk_widget().grid(row=0, column=4,rowspan=200, columnspan=50, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill= tkinter.BOTH, expand=1)

t=0
now = Time.monotonic()
print(lines)
def animate(i):
    global t
    global axes1
    global axes
    global poly_deg
    global x
    global y
    global lines
    
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
        high = 3.3
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
    try:
        if port == "":
          plt.pause(0.001)
          return lines
          
        data_in = read_serial(ser)
        data_in = process(data_in)
        
        t = check_delay(t, now)
        
        update_x(t)
        update_y(data_in)
        update_freq()
        
        #update real data
        lines[0].set_ydata(y)
        lines[0].set_xdata(x)
        #axes1.lines[0].remove()
        #axes1.plot(x,y,color='red', linewidth= 1, linestyle ='dotted')
        
        #update smoothing
        coefs = np.polyfit(x,y,poly_deg)
        x_poly = np.linspace(min(x),max(x),n*100)
        y_poly = np.polyval(coefs,x_poly )
        lines[1].set_xdata(x_poly)
        lines[1].set_ydata(y_poly)
        #axes1.lines[0].remove()
        #axes1.plot(x_poly ,y_poly,color='green', linewidth= 1, linestyle ='-')
        #axes1.set_ylim(lim_miny,lim_maxy)
        axes1.set_xlim(min(x),max(x))
        #axes1.autoscale_view()
        
        #update fft
        if(len(x) >= n):
            yff = np.fft.fft(y)
            yf = np.fft.fft(y)/n
            
            #update real fft
            yf = yf[range(n//2)]
            xf = (np.arange(n)/n*freq)[range(n//2)]
            lines[3].set_xdata(xf)
            lines[3].set_ydata(abs(yf) )
            #axes[1].lines[0].remove()
            #axes[1].plot(xf,abs(yf),'b',linewidth=1)
            #axes[1].set_xlim(0,freq)
            
            #update filtered fft
            ydel = yf
            ydel[0:wn] = 0.0
            lines[4].set_xdata(xf)
            lines[4].set_ydata(abs(ydel))
            #axes[1].lines[0].remove()
            #axes[1].plot(xf,abs(ydel),'r',linewidth=1)
            
            #update inverse fft
            if wn > 0 :
              yff[wn:-wn] = 0.0
            else:
              yff[:] = 0.0
            yff = np.fft.ifft(yff)
            lines[2].set_xdata(x)
            lines[2].set_ydata(yff)
            #axes1.lines[0].remove()
            #axes1.plot(x,yff,color='blue',linewidth=1)
        else:
            #axes1.lines[0].remove()
            #axes1.plot([],[])
            pass
          
        plt.pause(0.001)
    except KeyboardInterrupt:
        global root
        root.destroy()
        return lines
    
    return lines
         
ani = animation.FuncAnimation(fig, animate, blit= True, interval=1)
root.mainloop(  )