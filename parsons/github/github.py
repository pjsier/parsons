import logging
from functools import partial, wraps

from github import Github as PyGithub

from parsons.etl.table import Table
from parsons.utilities import check_env


logger = logging.getLogger(__name__)


def _wrap_method(decorator, method):
    def _wrapper(self, *args, **kwargs):
        bound_method = partial(method.__get__(self, type(self)))
        return decorator(bound_method)(*args, **kwargs)
    return _wrapper


def decorate_methods(decorator, methods=[]):
    # Based on Django's django.utils.decorators.method_decorator
    def decorate(cls):
        for method in methods:
            cls_method = getattr(cls, method)
            if callable(cls_method):
                setattr(cls, method, _wrap_method(decorator, cls_method))
        return cls
    return decorate


def as_dict(func):
    @wraps(func)
    def _wrapped_func(*args, **kwargs):
        return (func)(*args, **kwargs).raw_data
    return _wrapped_func


def as_table(func):
    @wraps(func)
    def _wrapped_func(*args, page=0, **kwargs):
        paginated_list = (func)(*args, **kwargs)
        return Table([i.raw_data for i in paginated_list.get_page(page)])
    return _wrapped_func


@decorate_methods(as_dict, methods=['get_user', 'get_repo'])
@decorate_methods(as_table, methods=['search_users'])
class GitHub(PyGithub):
    """[summary]
    """

    def __init__(self, username=None, password=None, access_token=None):

        self.username = check_env.check('GITHUB_USERNAME', username, optional=True)
        self.password = check_env.check('GITHUB_PASSWORD', password, optional=True)
        self.access_token = check_env.check('GITHUB_ACCESS_TOKEN', access_token, optional=True)

        if self.username and self.password:
            super().__init__(self.username, self.password)
        else:
            super().__init__(self.access_token)
