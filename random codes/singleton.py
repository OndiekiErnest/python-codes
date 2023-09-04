""" singleton design pattern implementation """


# decorator
def singleton(cls):
    instance = [None]

    def wrapper(*args, **kwargs):
        try:
            if instance[0] is None:
                instance[0] = cls(*args, **kwargs)
            return instance[0]
        except Exception as e:
            print(e)

    return wrapper


# base class
class SingletonBase(object):
    instc = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instc, cls):
            cls.instc = object.__new__(cls, *args, **kwargs)
        return cls.instc
