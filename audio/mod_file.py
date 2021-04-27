#!/usr/bin/env python3
import argparse

import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.integrate import simps
from scipy import signal 

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', metavar='FILENAME',
    help='audio file to be played back')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
args = parser.parse_args(remaining)

try:
    data, fs = sf.read(args.filename, dtype='float32')
    print(fs)
    print(data.shape)

    M = 1
    data = 1 + M * data
    print(np.mean(data))
    #data = data -1;
    
    f_target = 192000;
    resamp = signal.resample(data, f_target//fs * data.shape[0], axis=0) 
    print(resamp.shape)
    
    f_mod = 40000
    
    mod_wave = np.sin(2*np.pi*f_mod*np.linspace(0, data.shape[0]/fs, resamp.shape[0]))
    mod_wave = np.array([mod_wave,mod_wave]).T
    print(mod_wave.shape)
    
    
    #out = resamp.dot(mod_wave)
    out = resamp * mod_wave
    #out = np.multiply(resamp, mod_wave);
    print(out)
    
    sd.play(out, f_target, device=args.device)
    status = sd.wait()
    
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
if status:
    parser.exit('Error during playback: ' + str(status)) 
