from ctypes import *
from ctypes.wintypes import *
import struct
import time
import os
import pdb
import warnings

READ_ACCESS = 0x1F0FFF
SIZE_T = c_size_t
OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle
ReadProcessMemory.argtypes = [HANDLE, LPCVOID, LPVOID, SIZE_T, POINTER(SIZE_T)]; 
OpenProcess.restype = HANDLE; 
CloseHandle.argtypes = [HANDLE]



class MemFeature:
    name = ""
    address = 0x0
    bufferSize = 0
    def __init__(self, name, address, buf_size=4, isStr = False):
        self.name = name
        self.address = address
        self.bufferSize = buf_size
        self.buffer = (c_char * buf_size)()
        self.isStr = isStr

class Arena:
    PID = 0
    DISABLE_MEM_ERR = False
    DISABLE_WARN = False
    def __init__(self, PID, offset=0x0):
        self.PID = PID
        self.offset = offset
        # Initializing the processHandle only once gives us about 10x speedup over
        # doing it each time we want to fetch a value. It takes approx 5ms to get
        # 1000 values
        READ_ACCESS = 0x1F0FFF        
        self.processHandle = OpenProcess(READ_ACCESS, False, self.PID)

    def close(self):
        CloseHandle(self.processHandle)

    def get_frame(self,feature):
        buffer = (c_char * feature.bufferSize)()
        buffer.raw = b'\x00'*feature.bufferSize
        bytesRead = SIZE_T()
        val = c_int()

        #                     Ret from OpenProc  Address to Copy  copyto    How much to copy    How much Was copid
        if ReadProcessMemory(self.processHandle, feature.address, buffer, feature.bufferSize, byref(bytesRead)):
            
            # If its not a string we need to be able to cast the fetched value as an integer
            # and we cant really figure out if its an int after the fact (because itll look like)
            # a char array so its just part of the feature you pass in
            memmove(ctypes.byref(val),buffer,ctypes.sizeof(val))
            if feature.isStr:
                return buffer.raw.decode('utf_16le').rstrip('\x00')
            else:
                return val.value
        # Rarely reading process memory will fail (permissions errors, etc) but erros in the clib that arent compiler
        # related wont halt the code, so I halt it myself
        else:
            if not self.DISABLE_MEM_ERR: # If you dont want the code to halt, change this flag
                raise MemoryError("Failed reading process memory for {0} at address {1} with error {2}".format(feature.name, feature.address, GetLastError()))
            elif not self.DISABLE_WARN:  # If you want silent failures, change this flag
                warnings.warn("Failed reading process memory for {0} at address {1} with error {2}".format(feature.name, feature.address, GetLastError()), RuntimeWarning)

            return "ERR"

def watch_features(feature_arr, arena, interval):
    try:
        while True:            
            os.system('cls||clear')
            for frame in feature_arr:
                print(frame.name + " : " + str(arena.get_frame(frame)))
            time.sleep(interval)
    except:
        arena.close()

def main():
    frames = []
    arena = Arena(15112, offset=0x7FF4AC609180)
    frames.append(MemFeature("CurrentAnim", 0x7FF4AC60CCC8, buf_size=40, isStr=True)) 
    frames.append(MemFeature("LastAnim", 0x7FF4AC60DD18))   
    frames.append(MemFeature("MaxHP", 0x7FF4AC60C2E0)) 
    frames.append(MemFeature("CurrentHP", 0x7FF4AC60C2D8))
    watch_features(frames, arena, 0.5)
    
if __name__ == "__main__":
    main()