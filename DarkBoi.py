from ctypes import *
from ctypes.wintypes import *
import struct
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
    def __init__(self, name, address, buf_size=4):
        self.name = name
        self.address = address
        self.bufferSize = buf_size
        self.buffer = (c_char * buf_size)()

class Arena:
    PID = 0
    def __init__(self, PID):
        self.PID = PID


    def get_frame(self,feature):
        READ_ACCESS = 0x1F0FFF
        val = c_int();

        address = 0x7FF4ABB9EDF8 # Likewise; for illustration I'll get the .exe header.

        bufferSize = 4; 
        buffer = (c_char * feature.bufferSize)()
        bytesRead = SIZE_T()

        processHandle = OpenProcess(READ_ACCESS, False, self.PID)
        print(GetLastError())
        if ReadProcessMemory(processHandle, feature.address, buffer, feature.bufferSize, byref(bytesRead)):
            memmove(ctypes.byref(val), buffer, ctypes.sizeof(val))
            #print("Success:" + str(val.value))
        else:
            print("Failed.")
            print(GetLastError())
        CloseHandle(processHandle)
        return val.value


def main():
    arena = Arena(1204)
    frame = MemFeature("LastAnim", 0x7FF4ABB9EDF8)
    print(arena.get_frame(frame))

if __name__ == "__main__":
    main()