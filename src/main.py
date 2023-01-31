import time 
from random import random
from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import set_start_method
from rich import print as rprint
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import argparse
#from coord_tag_table import coord_tag
from coordv2 import coord_tag
set_start_method('fork')

def animate(i,X,Y,connection):
    item = connection.recv()
    if item == None:
        plt.close()
    #rprint("[ INFO ] [bold cyan]Receiver[/bold cyan] got :",item,flush=True)
    X.append(item)
    Y.append(Y[-1]+time.time() - t0)
    ax.clear()
    plt.xlabel('Elasped time') 
    plt.ylabel('Y value')
    # For points view
    #ax.scatter(Y,X)  
    # For graph view
    ax.plot(Y,X)  

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--view", type=bool,
    default=False,
    help="view graph sample data")
ap.add_argument("-t", "--type", type=str,
    default="DICT_ARUCO_ORIGINAL",
    help="type of ArUCo tag to detect")
ap.add_argument("-id1","--id1",type=int,default=None,
    help="id of the first tag to recognize")
ap.add_argument("-id2","--id2",type=int,default=None,
    help="id of the second tag to recognize")
ap.add_argument("-s1","--size1",type=float,default=None,
    help="size of the tag 1 to recognize")
ap.add_argument("-s2","--size2",type=float,default=None,
    help="size of the tag 2 to recognize")
args = vars(ap.parse_args())

# Creating the pipe if needed
if args["view"]:
    conn1, conn2 = Pipe()
else:
    conn2 = None

# start the coord_table_process
coord_tag_table_process = Process(
    target=coord_tag, 
    args=(args["type"],args["id1"],args["id2"],args["size1"],args["size2"],conn2,))
coord_tag_table_process.start()

# Optionnal plot
if args["view"]:
    fig, ax = plt.subplots() 
    y1 = 0.1
    X = [y1]
    t0 = time.time()
    Y = [t0]
    animation = ani.FuncAnimation(fig, animate, fargs=(X,Y,conn1),interval=100)
    plt.show()

# wait for all processes to finish
coord_tag_table_process.join()

