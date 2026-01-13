from functools import wraps

def validate(expected_type):
    def decorator(func):
        @wraps(func)
        def wrapper(self,words_string,*args,**kwargs):
            if not isinstance(words_string,expected_type):
                raise TypeError(
                    f"Expected str, got {type(words_string).__name__}"
                )
            return func(self,words_string,*args,**kwargs)
        return wrapper
    return decorator

