
class CommonException(Exception):
    def __init__(self, e, msg):
        self.e = e
        self.msg = msg
