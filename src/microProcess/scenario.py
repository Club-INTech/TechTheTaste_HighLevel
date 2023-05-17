from no_main_process import *

sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'mainProcess'))

import orderInterProcess 

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ Niveau 0 (départ panier) ------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def scenario_simple_no_green(pipe):
    
    orderInterProcess.waitingJumper(1)
    
    r.storage = ['R', '', '']
    s = SequenceNode()
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, 0.))
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, .0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .10, -.3))
    s.append(RobotAction(r, MOVEMENT, 'goto', .3, -.1))
    s.append(RobotAction(r, MOVEMENT, 'goto', .35, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .4, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, .3))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, -.2, True))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.45, -.05))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.45, -.07))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.35, .08))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, .05))

    s.append(Action(lambda: print('\nFinished')))
    
    sc = Scenario(r, pipe, s)
    sc.main_loop()
    
def scenario_simple_no_blue(pipe):
    
    orderInterProcess.waitingJumper(1)
    
    r.storage = ['R', '', '']
    s = SequenceNode()
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, 0.))
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, .0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .10, .3))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0.3, .1))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0.35, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, -.3))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, .2, True))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.45, -.05))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.45, -.07))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.35, -.8))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, -.05))

    s.append(Action(lambda: print('\nFinished')))

    sc = Scenario(r, pipe, s)
    sc.main_loop()

#même chose mais avec une pile trié
def scenario_sort_no_green(pipe):
    
    orderInterProcess.waitingJumper(1)
    
    r.storage = ['R', '', '']
    s = SequenceNode()
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, 0.))
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, .0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .10, -.3))
    s.append(RobotAction(r, MOVEMENT, 'goto', .3, -.1))
    s.append(RobotAction(r, MOVEMENT, 'goto', .35, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .4, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, .3))
    
    sortCakePhase1(RIGHT, LEFT, MID)
    
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, -.2, True))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.45, -.05))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.45, -.07))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.35, .08))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, .05))

    s.append(Action(lambda: print('\nFinished')))

    sc = Scenario(r, pipe, s)
    sc.main_loop()
    
def scenario_sort_no_blue(pipe):
        
    orderInterProcess.waitingJumper(1)
        
    r.storage = ['R', '', '']
    s = SequenceNode()
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, 0.))
    s.append(RobotAction(r, MOVEMENT, 'goto', .30, .0))
    s.append(RobotAction(r, MOVEMENT, 'goto', .10, .3))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0.3, .1))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0.35, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, 0))
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, -.3))
        
    sortCakePhase1(LEFT, RIGHT, MID)
        
    s.append(RobotAction(r, MOVEMENT, 'goto', 0, .2, True))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -0.45, -.05))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.45, -.07))
    #s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.35, -.8))
    s.append(RobotAction(r, MOVEMENT, 'goto', -.4, -.05))

    s.append(Action(lambda: print('\nFinished')))

    sc = Scenario(r, pipe, s)
    sc.main_loop()
    
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ niveau 1  ------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------


    

################################### SORT ###########################################


def sortCakePhase1(s: SequenceNode, genoise, creme, glacage):
    left = genoise
    mid = creme
    right = glacage
        
    s.append(RobotAction(r, ACTION, 'move_cake', right, left))
        
    s.append(RobotAction(r, ACTION, 'move_cake', mid, left))
    s.append(RobotAction(r, ACTION, 'move_cake', mid, left))     
        
    s.append(RobotAction(r, ACTION, 'move_cake', right, mid))
    s.append(RobotAction(r, ACTION, 'move_cake', right, mid))  
        
    s.append(RobotAction(r, ACTION, 'move_cake', left, right))
    s.append(RobotAction(r, ACTION, 'move_cake', left, right))
        
    s.append(RobotAction(r, ACTION, 'move_cake', left, mid))
        
    s.append(RobotAction(r, ACTION, 'move_cake', left, right))
        
    s.append(RobotAction(r, ACTION, 'move_cake', mid, right))
        
    s.append(RobotAction(r, ACTION, 'move_cake', left, right))
    
def sortCakePhase2(s: SequenceNode, genoise, creme, glacage):
    left = genoise
    mid = creme
    right = glacage
        
    s.append(RobotAction(r, ACTION, 'move_cake', right, left))
    s.append(RobotAction(r, ACTION, 'move_cake', right, left))
    s.append(RobotAction(r, ACTION, 'move_cake', right, left))
        
def sortCakePhase3(s: SequenceNode, genoise, creme, glacage):
    left = genoise
    mid = creme
    right = glacage
        
    s.append(RobotAction(r, ACTION, 'move_cake', mid, left))
    s.append(RobotAction(r, ACTION, 'move_cake', mid, left))
    s.append(RobotAction(r, ACTION, 'move_cake', right, left))


