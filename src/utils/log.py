
MessageType = ['error : ', 'success : ', 'information : ' ,  'warning : ' ]


def logMessage(logErrorNumber, message):
    if (logErrorNumber <= 3) :
        log_msg = "LOG BOT : "
        log_msg += MessageType[logErrorNumber] 
        log_msg += message
        print(log_msg)
        return 1

    else :
        print("log out of range")
        return 3


def logMessageOpti(logErrorNumber, message):
    if (logErrorNumber <= 1) :
        log_msg = "LOG BOT : "
        log_msg += MessageType[logErrorNumber] 
        log_msg += message
        print(log_msg)
        return 1
