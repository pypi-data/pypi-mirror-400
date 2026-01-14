from .core import CookieFinder

__version__ = "0.0.1"
__all__ = ['url', 'find_cookies', 'CookieFinder']

def url(target_url):
    finder = CookieFinder()
    return finder.from_url(target_url)

def find_cookies(target_url):
    return url(target_url)