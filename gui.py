import tkinter
root = tkinter.Tk(  )

line = 0

#all possible serial ports
import serial.tools.list_ports
ports = list( serial.tools.list_ports.comports() )
tkinter.Label(root, text="Open Port: ").grid(row=line, column=0, sticky=tkinter.W)
line += 1
for p in ports:
    tkinter.Label(root, text=str(line)+". "+str(p)).grid(row=line,column=0)
    line += 1
 
def connect():
    return
    
tkinter.Label(root, text="select port").grid(row=0,column=1)
port = tkinter.StringVar()
port.set("COM4")
tkinter.Entry(root, textvariable=port).grid(row=1,column=1)
tkinter.Button(root, text = "connect to port", command = connect).grid(row=0,column=2, rowspan=line, padx=5, pady=5 )

tkinter.Label(root, text="").grid(row = line,column=0,columnspan=3)
line += 1

tkinter.Label(root, text="GAIN :").grid(row=line+0,column=0)
tkinter.Label(root, text="Polynomial Degree :").grid(row=line+1,column=0)
tkinter.Label(root, text="Filtered frequency :").grid(row=line+2,column=0)

gain = tkinter.StringVar()
gain.set(1)
tkinter.Entry(root, textvariable=gain).grid(row=line+0,column=1)
poly_deg = tkinter.StringVar()
poly_deg.set(5)
tkinter.Entry(root, textvariable=poly_deg).grid(row=line+1,column=1)
filter_freq = tkinter.StringVar()
filter_freq.set(2)
tkinter.Entry(root, textvariable=filter_freq).grid(row=line+2,column=1)

def apply_setting():
  global filter_freq
  global poly_deg
  global gain
  print(gain.get(),poly_deg.get(),filter_freq.get())
  return

tkinter.Button(root, text="Apply Setting", command = apply_setting).grid(row=line+0, column=2, columnspan=2, rowspan=3,
               sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
               
tkinter.Label(root, text="PUT GRAPH HERE !").grid(row=line+3, column=0,rowspan=5, columnspan=5, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S, padx=5, pady=5)
         
root.mainloop(  )