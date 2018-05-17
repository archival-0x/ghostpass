# Define a class that inherits Exception
class GhostpassException(Exception):
    pass

'''
Initalization Process

1. Initialize new object
2. Initalize new state with master password and corpus file
3. Perform preemptive password encryption with master password and corpus
4. Save state as JSON in .config/ghostpass TODO: maybe merkle tree??

'''
class Ghostpass(object):

    # initializes the state of the new object, and creates the instance variables
    # we need
    def __init__():
        self.state = 1 # activation state
        self.uuid = None # represents pseudorandom identifying ID for session
        self.password = None # represents master password
        self.corpus = [] # represents list of all words in a corpus after file IO

    # prints out object as string
    def __repr__():
        return 0

    # decorator method that encapsulates other instance methods, checking to see
    # if the activation state permits execution
    def _decorator(func):
      def state_check(self, *params):
          if self.state != 1:
              return None
          # pass positional args, since instance methods all have different parameters
          return func(self, *params)
      return state_check

     @_decorator
    def init_state(self, password, corpus_path):
        return 0

    @_decorator
    def _init_preempt_pass_encryption(self):
        return 0

    @_decorator
    def create_output(self):
        return 0
