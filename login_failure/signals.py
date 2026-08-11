from django.dispatch import Signal

class UnauthorizedSignalReceiver(Exception):
    pass

class SingleHandlerSignal(Signal):

    allowed_receiver = 'login_failure.middleware.RequestProvider'

    def __init__(self):
        super().__init__()

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        cls = getattr(receiver, '__self__', receiver).__class__
        receiver_name = '.'.join([cls.__module__, cls.__name__])

        if receiver_name != self.allowed_receiver:
            raise UnauthorizedSignalReceiver()

        Signal.connect(self, receiver, sender, weak, dispatch_uid)

request_accessor = SingleHandlerSignal()

def get_request():
    """ Sender=None, sent to all receivers
    so [0] indicates the response of the first receiver,
    in our case the middleware that sends us back the 
    request object.Responses are sent back as a tuple of
    (receiver,response), so [1] indicates the response
    of this particular receiver.
    """
    return request_accessor.send(None)[0][1]