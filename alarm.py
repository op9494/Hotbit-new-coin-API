import win32api
    
def triggeralarm():
    for i in range(20):
        win32api.Beep(1000,500)