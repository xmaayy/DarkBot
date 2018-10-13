from ctypes import *
from ctypes.wintypes import *
import ctypes

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

SIZE_T = c_size_t; 
ReadProcessMemory.argtypes = [HANDLE, LPCVOID, LPVOID, SIZE_T, POINTER(SIZE_T)]; 
OpenProcess.restype = HANDLE; 
CloseHandle.argtypes = [HANDLE]

PROCESS_ALL_ACCESS = 0x1F0FFF

pid = 1204
address = 0x7FF4ABB9E9D8

val = c_int()
bufferSize = 20;
buffer = (c_char * bufferSize)()
bytesRead = SIZE_T()

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
    memmove(ctypes.byref(val), buffer, ctypes.sizeof(val))

    print("Success: " + str(val.value))
else:
    print("Failed.")

CloseHandle(processHandle)