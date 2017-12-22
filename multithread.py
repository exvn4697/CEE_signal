################################################################################
#By : Ervin Kwok
#
#
#matplotlib with tkinter tutorial :
#1. https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
#2. https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/?completed=/how-to-embed-matplotlib-graph-tkinter-gui/
#3.https://pythonprogramming.net/organizing-gui/?completed=/embedding-live-matplotlib-graph-tkinter-gui/
#4. https://pythonprogramming.net/plotting-live-bitcoin-price-data-tkinter-matplotlib/?completed=/organizing-gui/ 
#
#how to speed up matplotlib :
#1. http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#2. https://taher-zadeh.com/speeding-matplotlib-plotting-times-real-time-monitoring-purposes/
#
#threading in python with shared queue :
#1. https://stackoverflow.com/questions/16044452/sharing-data-between-threads-in-python
#2. https://www.troyfawkes.com/learn-python-multithreading-queues-basics/
##################################################################################

import threading
import queue
import time
import serial.tools.list_ports
import json

import serial
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.animation as animation #refer to matplotlib tutorial 4
from matplotlib.transforms import Bbox

import struct
import os

import tkinter
style.use('fivethirtyeight')
plt.rc('xtick',labelsize=12)
plt.rc('ytick',labelsize=12)

class Manager:
    def __init__(self):
        #initialize constants
        self.x = []
        self.x_index = []
        self.y = []
        self.sample_size = 200
        self.dataQueue = queue.Queue(self.sample_size)
        self.now = time.monotonic()
        self.freq = 15
        self.gain = 1
        self.wn = 10
        self.ser = ""
        self.port = ""
        self.poly_deg = 5
        self.lim_maxy = 1.835
        self.lim_miny = 1.810
        self.lim_fft_maxy = 0.0001
        self.lim_fft_miny = -0.00005
        self.lim_fft_maxx = 85
        self.lim_fft_minx = 0
        self.high = 4.096
        self.stop_bit = True
        self.bbox_xaxis = Bbox.from_bounds(105.325,372.277,915.84,390.276)
        self.smoothing = True
        self.fft = True
        
        #update constants from settings.txt
        def read_settings():
            with open('settings.txt','r') as f:
                lines = f.readlines()
                temp = ""
                for line in lines:
                    temp += line
                set = json.loads(temp)
                
                return set
        
        self.set = {}
        self.set = read_settings()
        self.sample_size = self.set['sample_size']
        self.gain = self.set['gain']
        self.wn = self.set['filter_freq']
        self.poly_deg = self.set['poly_deg']
        self.lim_maxy = self.set['max_yaxis']
        self.lim_miny = self.set['min_yaxis']
        self.lim_fft_maxy = self.set['max_fft_yaxis']
        self.lim_fft_miny = self.set['min_fft_yaxis']
        self.lim_fft_maxx = self.set['max_fft_xaxis']
        self.lim_fft_minx = self.set['min_fft_xaxis']
        
        #initialize tkinter and graph
        self._init_tkinter()
    
    #initialize GUI tkinter
    def _init_tkinter(self):
        #make tkinter object
        self.root = tkinter.Tk(  )
        self.root.wm_state('zoomed')
        ports = list( serial.tools.list_ports.comports() ) #list all available ports to connect
        line = 0
        
        #display all available ports to the interface
        tkinter.Label(self.root, text="Open Port: ").grid(row=line, column=0, sticky=tkinter.W)
        line += 1
        for p in ports:
            tkinter.Label(self.root, text=str(line)+". "+str(p)).grid(row=line,column=0)
            line += 1
         
        #connect to a port function 
        def connect():
            self.port = port_var.get()
            try:
                if self.ser != "" and self.ser.isOpen() == True:
                    self.ser.close()
                time.sleep(0.5)
                self.ser = serial.Serial(self.port, 9600)
                if self.ser.isOpen() == False:
                    self.ser.open()
                    
                connect_var.set("Connected to "+ self.port)
            except Exception as e:
                print(e)
                print(self.ser)
                connect_var.set("Can not connect to "+ self.port)
            
            self.root.update()
            return
            
        #port connection settings
        tkinter.Label(self.root, text="select port").grid(row=0,column=1)
        port_var = tkinter.StringVar()
        port_var.set("COM4")
        tkinter.Entry(self.root, textvariable=port_var).grid(row=1,column=1)
        tkinter.Button(self.root, text = "connect to port", command = connect).grid(row=0,column=2, rowspan=line, padx=5, pady=5 )

        if line<2 :
          line = 2
        
        #connection notification text
        connect_var = tkinter.StringVar()
        connect_var.set("")
        tkinter.Label(self.root, textvariable=connect_var).grid(row = line,column=0,columnspan=3,sticky=tkinter.N)
        line += 1

        tkinter.Label(self.root, textvariable="").grid(row = line,column=0,columnspan=3,sticky=tkinter.N)
        line += 1
        
        #graph settings labels
        tkinter.Label(self.root, text="GAIN :").grid(row=line+0,column=0)
        tkinter.Label(self.root, text="Polynomial Degree :").grid(row=line+1,column=0)
        tkinter.Label(self.root, text="Filtered frequency :").grid(row=line+2,column=0)
        tkinter.Label(self.root, text="maximum y-axis :").grid(row=line+3,column=0)
        tkinter.Label(self.root, text="minimum y-axis :").grid(row=line+4,column=0)
        tkinter.Label(self.root, text="maximum fft y-axis :").grid(row=line+5,column=0)
        tkinter.Label(self.root, text="minimum fft y-axis :").grid(row=line+6,column=0)
        tkinter.Label(self.root, text="maximum fft x-axis :").grid(row=line+7,column=0)
        tkinter.Label(self.root, text="minimum fft x-axis :").grid(row=line+8,column=0)
        tkinter.Label(self.root, text="Sample size :").grid(row=line+9,column=0)
        tkinter.Label(self.root, text="x-axis type:").grid(row=line+10,column=0)

        #graph settings textboxes and initialize them
        gain_var = tkinter.StringVar()
        gain_var.set(self.gain)
        tkinter.Entry(self.root, textvariable=gain_var).grid(row=line+0,column=1)
        poly_deg_var = tkinter.StringVar()
        poly_deg_var.set(self.poly_deg)
        tkinter.Entry(self.root, textvariable=poly_deg_var).grid(row=line+1,column=1)
        filter_freq_var = tkinter.StringVar()
        filter_freq_var.set(self.wn)
        tkinter.Entry(self.root, textvariable=filter_freq_var).grid(row=line+2,column=1)
        maxy_var = tkinter.StringVar()
        maxy_var.set(self.lim_maxy)
        tkinter.Entry(self.root, textvariable=maxy_var).grid(row=line+3,column=1)
        miny_var = tkinter.StringVar()
        miny_var.set(self.lim_miny)
        tkinter.Entry(self.root, textvariable=miny_var).grid(row=line+4,column=1)
        fft_maxy_var = tkinter.StringVar()
        fft_maxy_var.set(self.lim_fft_maxy)
        tkinter.Entry(self.root, textvariable=fft_maxy_var).grid(row=line+5,column=1)
        fft_miny_var = tkinter.StringVar()
        fft_miny_var.set(self.lim_fft_miny)
        tkinter.Entry(self.root, textvariable=fft_miny_var).grid(row=line+6,column=1)
        fft_maxx_var = tkinter.StringVar()
        fft_maxx_var.set(self.lim_fft_maxx)
        tkinter.Entry(self.root, textvariable=fft_maxx_var).grid(row=line+7,column=1)
        fft_minx_var = tkinter.StringVar()
        fft_minx_var.set(self.lim_fft_minx)
        tkinter.Entry(self.root, textvariable=fft_minx_var).grid(row=line+8,column=1)
        sample_size_var = tkinter.StringVar()
        sample_size_var.set(self.sample_size)
        tkinter.Entry(self.root, textvariable=sample_size_var).grid(row=line+9,column=1)
        
        #boolean for distinguish time-xaxis and index-xaxis
        self.on_off_bit = False
        def xaxis_time_button():
            state = self.on_off_bit
            self.on_off_bit = False
            self.lines[0].set_xdata(self.x)
                
        tkinter.Button(self.root, text="time", command = xaxis_time_button).grid(row=line+10, column=1)
        
        def xaxis_index_button():
            state = self.on_off_bit
            self.on_off_bit = True
            while len(self.x_index) > len(self.y) and len(self.x_index) > 0 :
                del self.x_index[-1]
                    
            for i in range(len(self.x_index), len(self.y), 1):
                self.x_index += [i]
            self.lines[0].set_xdata(self.x_index)
            
        tkinter.Button(self.root, text="index", command = xaxis_index_button).grid(row=line+10, column=2)
        
        #apply all setting indicated in graph settings textboxes
        def apply_setting():          
          try:
            self.gain = int(gain_var.get() )
          except:
            pass
          
          try:
            self.poly_deg = int(poly_deg_var.get() )
          except:
            pass
           
          try:
            self.wn = int(filter_freq_var.get() )
          except:
            pass

          try:
            self.lim_maxy = float(maxy_var.get() )
          except:
            pass
            
          try:
            self.lim_miny = float(miny_var.get() )
          except:
            pass
            
          try:
            self.lim_fft_maxy = float(fft_maxy_var.get() )
          except:
            pass
            
          try:
            self.lim_fft_miny = float(fft_miny_var.get() )
          except:
            pass
            
          try:
            self.lim_fft_maxx = float(fft_maxx_var.get() )
          except:
            pass
            
          try:
            self.lim_fft_minx = float(fft_minx_var.get() )
          except:
            pass
          
          try:
            self.sample_size = int(sample_size_var.get() )
          except:
            pass
          
          #draw the changes
          self.axes[0].set_ylim(self.lim_miny, self.lim_maxy)
          self.axes[1].set_ylim(self.lim_fft_miny, self.lim_fft_maxy)
          self.axes[1].set_xlim(self.lim_fft_minx, self.lim_fft_maxx)
          self.axes[1].draw_artist(self.axes[1].xaxis)
          self.fig.canvas.draw()
          self.background1 = self.fig.canvas.copy_from_bbox(self.axes[0].get_figure().bbox)
          print(self.freq)
          
          #save settings to file settings.txt
          def update_set():
              self.set['sample_size'] = self.sample_size
              self.set['gain'] = self.gain 
              self.set['filter_freq'] = self.wn
              self.set['poly_deg'] = self.poly_deg 
              self.set['max_yaxis'] = self.lim_maxy
              self.set['min_yaxis'] = self.lim_miny
              self.set['max_fft_yaxis'] = self.lim_fft_maxy
              self.set['min_fft_yaxis'] = self.lim_fft_miny
              self.set['max_fft_xaxis'] = self.lim_fft_maxx
              self.set['min_fft_xaxis'] = self.lim_fft_minx
          
          update_set()
          with open('settings.txt','w') as f:
              f.write(json.dumps(self.set, sort_keys=True,indent=2, separators=(',', ': ')))
          
          return

        tkinter.Button(self.root, text="Apply Setting", command = apply_setting).grid(row=line+0, column=2, columnspan=2, rowspan=10, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        
        line += 11
        
        tkinter.Label(self.root, text="smoothing line :").grid(row=line+0,column=0)
        def on_smoothing():
            self.smoothing = True
        tkinter.Button(self.root, text="on", command = on_smoothing).grid(row=line+0, column=1, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        def off_smoothing():
            self.smoothing = False
        tkinter.Button(self.root, text="off", command = off_smoothing).grid(row=line+0, column=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        
        line +=1
        tkinter.Label(self.root, text="fft line :").grid(row=line+0,column=0)
        def on_fft():
            self.fft = True
        tkinter.Button(self.root, text="on", command = on_fft).grid(row=line+0, column=1, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        def off_fft():
            self.fft = False
        tkinter.Button(self.root, text="off", command = off_fft).grid(row=line+0, column=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        
        line +=1
        
        def start_button():
            self.stop_bit = False
        
        tkinter.Button(self.root, text="Start", command = start_button).grid(row=line+0, column=0, columnspan=3, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        
        def stop_button():
            self.stop_bit = True
        
        tkinter.Button(self.root, text="Stop", command = stop_button).grid(row=line+1, column=0, columnspan=3, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
                       
        def reset_button():
            self.x = []
            self.x_index = []
            self.y = []
            while not self.dataQueue.empty():
                    data_xy = self.dataQueue.get_nowait()
            self.now = time.monotonic()
        
        tkinter.Button(self.root, text="Reset", command = reset_button).grid(row=line+2, column=0, columnspan=3, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
        
        self.lines = []
        self.fig, self.axes = plt.subplots(2,1,figsize=(9,7))
        plt.close('all')
        
        #data graph plot
        self.lines += [self.axes[0].plot(self.x, self.y, color='red', linewidth= 1, linestyle ='dotted', animated=True)[0]]
        self.lines += [self.axes[0].plot([], [], color='green', linewidth= 1, linestyle ='-', animated=True)[0]] #smoothing dummy
        self.lines += [self.axes[0].plot([], [], color='blue',linewidth=1, animated=True)[0]] #inverse fft dummy
        self.axes[0].set_ylabel('Voltage',size=12)
        self.axes[0].set_title('Time Signal',size=12)
        self.axes[0].set_ylim(self.lim_miny, self.lim_maxy)
        self.axes[0].get_xaxis().set_animated(True)
        self.axes[0].get_xaxis().set(zorder=-1)
        self.axes1 = self.axes[0]

        #fft graph plot
        self.lines += [self.axes[1].plot(self.x, self.y, 'b',linewidth=1, animated=True)[0]]
        self.lines += [self.axes[1].plot([], [], 'r',linewidth=1, animated=True)[0]] #filtered fft dummy
        self.axes[1].set_xlabel('Freq (Hz)',size=12)
        self.axes[1].set_ylabel('|Y(freq)|',size=12)
        self.axes[1].set_title('FFT on Time Signal',size=12)
        self.axes[1].set_xlim(self.lim_fft_minx, self.lim_fft_maxx)
        self.axes[1].set_ylim(self.lim_fft_miny, self.lim_fft_maxy)
        self.axes[1].get_xaxis().set_animated(True)
        self.axes[1].get_xaxis().set(zorder=-1)

        graph = tkinter.LabelFrame(self.root, text="Graph", padx=5,pady=5)
        graph.grid(row=0,column=4,rowspan=100,columnspan=100)
        self.fig.tight_layout()
        canvas = FigureCanvasTkAgg(self.fig, master=graph)
        canvas.show()
        self.background1 = self.fig.canvas.copy_from_bbox(self.axes[0].get_figure().bbox)
        self.background2 = self.fig.canvas.copy_from_bbox(self.axes[1].bbox)
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill= tkinter.BOTH, expand=1)
    
    def run_tkinter(self):
        self.root.mainloop()
    
    def serial_process(self):
        def read_serial():
            data_in = self.ser.readline()
            data_in = data_in.decode()
            if('\x00' == data_in[:1] ):
                data_in = data_in.split("\x00")[1];
                print("\\x00 detected")
            
            try:
                data_in = float ( ( data_in ).split("\\n")[0])
            except:
                print("FLOATING CONVERSION ERROR!")
                return -10.0
                pass
            
            return data_in

        def process(data):
            precision = 16 # 16-bit reading
            data = (data/(2 ** (precision-1)-1)) * (self.high/self.gain)
            
            return data
            
        while True:
            #do not put anything if there is no serial port connected
            #do not put anything if stop is clicked
            if self.ser == "" or self.stop_bit:
                while not self.dataQueue.empty():
                    data_xy = self.dataQueue.get_nowait()
                time.sleep(1)
                continue
            try:    
                data = read_serial()
            except Exception as e:
                time.sleep(1)
                continue
            
            #process and put data to shared queue
            data = process(data)
            if data > 0.0 and data < self.high/self.gain :
                try:
                    self.dataQueue.put_nowait([time.monotonic()-self.now, data])
                except queue.Full:
                    self.dataQueue.get_nowait()
                    self.dataQueue.put_nowait([time.monotonic()-self.now, data])
    
    def update_graph(self, i):
        data_x = []
        data_y = []
        
        #extract data from shared queue
        while not self.dataQueue.empty():
            data_xy = self.dataQueue.get_nowait()
            data_x += [data_xy[0]]
            data_y += [data_xy[1]]
        
        #nothing from queue
        if len(data_x) <= 0 :
            return self.lines + [self.axes[0].xaxis, self.axes[1].xaxis]
            
        if len(self.x) + len(data_x) > self.sample_size:
            self.x = self.x[len(self.x)-self.sample_size+len(data_x):] + data_x
            self.y = self.y[len(self.y)-self.sample_size+len(data_y):] + data_y
            self.freq = self.sample_size/(self.x[-1] - self.x[0])
        else:
            self.x += data_x
            self.y += data_y
        
        if len(self.x) > self.sample_size:
            self.x = self.x[(len(self.x)-self.sample_size):]
            self.y = self.y[(len(self.y)-self.sample_size):]
        
        x = []
        if self.on_off_bit == True:
            while len(self.x_index) > len(self.y) and len(self.x_index) > 0 :
                del self.x_index[-1]
                    
            for i in range(len(self.x_index), len(self.y), 1):
                self.x_index += [i]
            x = self.x_index
        else:
            x = self.x
            
        #update real data
        self.lines[0].set_data(x, self.y)
        
        #update smoothing
        coefs = np.polyfit(x, self.y, self.poly_deg)
        x_poly = np.linspace(min(x), max(x), self.sample_size*100)
        y_poly = np.polyval(coefs, x_poly)
        if self.smoothing:
            self.lines[1].set_data(x_poly, y_poly)
        else:
            self.lines[1].set_data([],[])
        self.axes[0].set_xlim(min(x), max(x))
        
        #update fft
        if(len(x) >= self.sample_size):
            yff = np.fft.fft(self.y)
            yf = np.fft.fft(self.y)/self.sample_size
            
            #update real fft
            yf = yf[range(self.sample_size//2)]
            xf = (np.arange(self.sample_size)/self.sample_size*self.freq)[range(self.sample_size//2)]
            self.lines[3].set_data(xf, abs(yf))
            
            #update filtered fft
            ydel = yf
            for i in range( len(ydel) ):
                if xf[i] < self.wn:
                    ydel[i] = 0.0
            self.lines[4].set_data(xf, abs(ydel))
            
            #update inverse fft
            if self.wn > 0 :
              for i in range(len(ydel)):
                  if xf[i] >= self.wn:
                      yff[i] = 0.0
                      yff[-i] = 0.0
            else:
              yff[:] = 0.0
            yff = np.fft.ifft(yff)
            if self.fft:
                self.lines[2].set_data(x, yff)
            else:
                self.lines[2].set_data([],[])
        else:
            pass
        
        self.fig.canvas.restore_region(self.background1)
        #draw data graph
        self.axes[0].draw_artist(self.lines[0] )
        self.axes[0].draw_artist(self.lines[1] )
        self.axes[0].draw_artist(self.lines[2] )
        self.axes[0].draw_artist(self.axes[0].xaxis )
        
        #draw fft graph
        self.axes[1].draw_artist(self.lines[3] )
        self.axes[1].draw_artist(self.lines[4] )
        self.axes[1].draw_artist(self.axes[1].xaxis )
        self.fig.canvas.blit(self.axes[1].get_figure().bbox )
        
        return self.lines

    def animate(self):
        ani = animation.FuncAnimation(self.fig, self.update_graph, blit= True, interval=100)
            
if __name__ == '__main__':
    manager = Manager()
    #serial thread
    serialThread = threading.Thread(group= None, target= manager.serial_process, args=[])
    serialThread.daemon = True
    serialThread.start()
    
    updateThread = threading.Thread(group=None, target= manager.animate, args=[]) 
    updateThread.daemon=True
    updateThread.start()
    
    manager.run_tkinter()
    