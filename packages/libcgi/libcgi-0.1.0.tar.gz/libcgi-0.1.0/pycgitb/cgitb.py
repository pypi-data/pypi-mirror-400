import os, sys, io

class enable:
    def __init__(
        self, 
        logdir      = sys.stderr
    ):
        self.logdir = logdir

    def handler(
        self, 
        message, 
        logdir      = None
    ):
        

        if logdir is None:
            print(message, file = self.io_set(self.logdir))
        else:
            
            print(message, file = self.io_set(logdir))
    
    def io_set(self, logdir):
        if os.name == "nt": 
            if logdir is sys.stderr:
                if isinstance(sys.stderr, io.TextIOWrapper): 
                    return sys.stderr
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, 
                    encoding="UTF-8", 
                    errors="replace",
                    newline="\n"
                )
                return sys.stderr
        
        return logdir
