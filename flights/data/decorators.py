from django.core.cache import cache


def crop_request(func):
    def wrapper(self, operation, *args, **kwargs):
        r = func(self, operation, *args, **kwargs)
        try:
            r = r[operation + 'Result'][operation.lower()]
            self.data = r
            return r
        except:
            return r
    return wrapper


def cache_operation(func):
    def wrapper(self, operation, *args, **kwargs):
        r = func(self, operation, *args, **kwargs)
        if type(r) != str:
            try:
                airport = args[0]['airport']
            except:
                pass
            cache.set('{}_{}'.format(operation.lower(), airport), r, None)
            return r
        return r
    return wrapper
