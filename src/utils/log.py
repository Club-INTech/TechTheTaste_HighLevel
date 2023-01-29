
MessageType = ['error : ', 'success : ', 'information : ' ,  'warning : ' ]
ERROR, SECCESS, INFO, WARN = range(4)


def logMessage(logErrorNumber, message):
    if (logErrorNumber <= 3) :
        print(f'LOG BOT : {MessageType[logErrorNumber]}{message}')
        return 1

    else :
        print("log out of range")
        return 3


def logMessageOpti(logErrorNumber, message):
    if (logErrorNumber <= 1) :        
        print(f'LOG BOT : {MessageType[logErrorNumber]}{message}')
        return 1
