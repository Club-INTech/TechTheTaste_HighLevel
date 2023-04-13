
MessageType = ['error       : ', 'sucess      : ', 'information : ' ,  'warning     : ' ]
process = ['mainProcess    :', #0
           'lidarProcess   :', #1
           'micro1Process  :', #2
           'micro2Process  :', #3
           'camBotProcess  :', #4
           'camMatProcess  :', #5
           'lpastarProcess :', #6  
           'launcher       :'] #7


def logMessage(logErrorNumber, message, processNumber):
    if (logErrorNumber <= 3) :
        log_msg = "LOG BOT : "
        log_msg += process[processNumber]
        log_msg += MessageType[logErrorNumber] 
        log_msg += message
        print(log_msg)

        return 1

    else :
        print("log out of range")
        return 3


def logMessageOpti(logErrorNumber, message):
    if (logErrorNumber <= 1) :        
        print(f'LOG BOT : {MessageType[logErrorNumber]}{message}')
        return 1
