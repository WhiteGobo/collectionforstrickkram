import multiprocessing as mp
import time
import os

class TimeLimitExceeded( Exception ):
    pass

class NoDataProduced( Exception ):
    pass

def _limit_calculation_minion( function, myqueue, argv, *args ):
    try:
        retval = function( *args, **argv )
        myqueue.put( retval )
    except Exception as err:
        myqueue.put( err )

def limit_calctime( function, calctime,dt=5 ):
    def limited_function( *args, **argv ):
        mp_ctx = mp.get_context( 'spawn' )
        myqueue = mp_ctx.Queue( 1 )
        mpid = mp_ctx.Process( target=_limit_calculation_minion, \
                                args=( function, myqueue, argv, *args ) )
        mpid.start()
        for i in range( 0, calctime, dt ):
            if myqueue.empty() and mpid.is_alive():
                time.sleep( dt )
            else:
                break
        if mpid.is_alive():
            mpid.terminate()
            mpid.join()
            raise TimeLimitExceeded()
        try:
            retval = myqueue.get( block=False )
        except Exception as err:
            mpid.join()
            raise NoDataProduced() from err
        mpid.join()
        if isinstance( retval, Exception ):
            raise retval
        return retval
    return limited_function
