"""Small helper module for foked process, to limit runtime

:todo: Exception that are raised will lose their traceback
"""
import multiprocessing as mp
import time
import os
import logging
import traceback
import numpy as np
logger = logging.getLogger( __name__ )

class TimeLimitExceeded( Exception ):
    pass

class NoDataProduced( Exception ):
    pass

def _limit_calculation_minion( function, myqueue, argv, *args, \
                                expected_errors=[], loglevel=logging.WARNING):
    logging.basicConfig( level=loglevel )
    try:
        retval = function( *args, **argv )
        myqueue.put( retval )
    except Exception as err:
        if type( err ) in expected_errors:
            logfoo = logger.debug
        else:
            logfoo = logger.error
        logfoo( "caught error while running fork" )
        logfoo( "".join( traceback.format_tb(err.__traceback__)))
        myqueue.put( err )

def limit_calctime( function, calctime, dt=.05, expected_errors=[] ):
    loglevel = logging.getLogger().getEffectiveLevel()
    def limited_function( *args, **argv ):
        mp_ctx = mp.get_context( 'spawn' )
        myqueue = mp_ctx.Queue( 1 )
        mpid = mp_ctx.Process( target=_limit_calculation_minion, \
                                args=( function, myqueue, argv, *args ), \
                                kwargs={"expected_errors": expected_errors,\
                                "loglevel": loglevel} )
        mpid.start()
        pasttime = 0
        for t in np.logspace( -2, np.log(calctime)/np.log(10) ):
            dt = t - pasttime
            pasttime = t
            time.sleep( dt )
            if not mpid.is_alive():
                break
        if mpid.is_alive():
            mpid.terminate()
            mpid.join()
            raise TimeLimitExceeded()
        #check missing myqueue.empty()
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
