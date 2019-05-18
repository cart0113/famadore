
def do_it_now(x, y):

    for index in xrange(x):
        if index == 4:
           do_it_now(x - 1, y - 1)
           
    import time
    
    if y == 4 or y == 2:
        time.sleep(3.0)
        
    import json
    json.dumps({'x': x, 'y': y})
           


if __name__ == '__main__':

    import sys
    sys.path.insert(0, '/home/ajcarter/workspace/GIT_FAMADORE')

    import test_setup
    
    from famadore import attach, detach
    
    famadore_controller = attach(modules=[test_setup])
    
    do_it_now(10, 6)
    
    detach()
    
    for call in famadore_controller.calls:
        print call.walltime, call.runtime
    
            