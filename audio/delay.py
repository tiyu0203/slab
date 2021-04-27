import numpy as np
from scipy import signal
import sounddevice as sd
import queue
import sys
import time as tim
print('Done importing')

dtype = 'float32'
samplerate = 8000 # int(sys.argv[1])
input_device  = int(sys.argv[1])
output_device = int(sys.argv[2])
bs = 8192*1 # int(sys.argv[4])
channels= 32 # int(sys.argv[5])

dump = np.zeros((bs, channels))

q_in = queue.Queue()
q_out = queue.Queue()

def input_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    #tim.sleep(1.99)
    q_in.put(indata.copy())

def output_callback(outdata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    tim.sleep(0.9)
    if status:
        print(status, file=sys.stderr)
    if not q_out.empty():
        print('good')
        outdata[:] = q_out.get()
    else:
        print('bad')
        outdata[:] = np.zeros((bs, channels))

try:
    with sd.InputStream(samplerate=samplerate, device=input_device, callback=input_callback, dtype=dtype, blocksize=bs):
        with sd.OutputStream(samplerate=samplerate, device=output_device, dtype=dtype, callback=output_callback, blocksize=bs) as ss:
            while True:
                if not q_in.empty():
                    data = q_in.get()
                    #print(ss.write_available)
                    #print(f"In data {data.shape}")
                    #data2 = data
                    #data2 = model.separate(data[:, 0]).T
                    # print(f"Out data {data2.shape}")
                    # print(data[:, 3])
                    #tim.sleep(0.9)
                    dump[:, :2] = data[:,:2]
                    q_out.put(dump)
                    
                    #q_out.put(data.T[:, 0][:,np.newaxis])
except KeyboardInterrupt:
    print('Exiting Gracefully!')
