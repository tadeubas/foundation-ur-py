# STAY
class BasicDecoder:
    def __init__(self):
        self.result = None

    def is_success(self):
        result = self.result
        return result if not isinstance(result, Exception) else False

    def is_complete(self):
        return self.result is not None
