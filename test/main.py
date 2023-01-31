import time 
from random import random
from multiprocessing import Process
from multiprocessing import Pipe
from rich import print as rprint
import matplotlib.pyplot as plt
import matplotlib.animation as ani

def sender(connection):
    rprint("[ INFO ] [bold red]Sender[/bold red] starting …",flush=True)
    for i in range(50):
        value = random()
        time.sleep(1)
        # sending message
        connection.send(value)
    # closing connection
    connection.send(None)
    rprint("[ INFO ] [bold red]Sender[/bold red] connection closed ",flush=True)

def receiver(connection,fig_,animate_,X,Y,t0):
    rprint("[ INFO ] [bold cyan]Receiver[/bold cyan] starting …",flush=True)
    while True :
        item = connection.recv()
        rprint("[ INFO ] [bold cyan]Receiver[/bold cyan] got :",item,flush=True)
        X.append(item)
        Y.append(Y[-1]+time.time() - t0)
        #rprint("Current X :",X,flush=True)
        #rprint("Current Y :",Y,flush=True)
        if item == None:
            plt.close()
            break
    rprint("[ INFO ] [bold cyan]Receiver[/bold cyan] connection closed ",flush=True)

def animate(i,X,Y,conn2):
    """perform animation step"""
    global close,animation
    item = conn2.recv()
    if item == None:
        close = False
    rprint("[ INFO ] [bold cyan]Receiver[/bold cyan] got :",item,flush=True)
    X.append(item)
    Y.append(Y[-1]+time.time() - t0)
    ax.clear()
    plt.xlabel('Elasped time') 
    plt.ylabel('Y value')
    ax.scatter(Y,X)
    

if __name__ == '__main__':
    # creating the pipe
    conn1, conn2 = Pipe()
    close = False
    # start the sender
    sender_process = Process(target=sender, args=(conn2,),daemon=True)
    sender_process.start()
    # start the receiver
     # variables for the plot
    fig, ax = plt.subplots() 
    
    y1 = 0.1
    X = [y1]
    t0 = time.time()
    Y = [t0]
    animation = ani.FuncAnimation(fig, animate, fargs=(X,Y,conn1),interval=100)
    plt.show()

    while True:
        rprint("Rentré")
        if close: 
            rprint("[red] On close !!!!!!")
            sender_process.join()
            plt.close()
        pass
    

