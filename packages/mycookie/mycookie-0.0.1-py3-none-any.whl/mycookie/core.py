import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

class CookieFinder:
    
    def __init__(self, user_agent=None, timeout=10):
        self.user_agent = user_agent or "MyCookie/1.0"
        self.timeout = timeout
        self.session = requests.Session()
    
    def from_url(self, target_url, verify_ssl=False, custom_headers=None):
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        try:
            response = self.session.get(
                target_url,
                verify=verify_ssl,
                timeout=self.timeout,
                headers=headers
            )
            
            cookies = response.cookies
            cookie_names = [cookie.name for cookie in cookies]
            
            return cookie_names
            
        except requests.exceptions.RequestException as e:
            raise
    
    def from_url_with_details(self, target_url, verify_ssl=False, custom_headers=None):
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        result = {
            'status_code': None,
            'success': False,
            'cookies': [],
            'cookie_names': [],
            'error': None
        }
        
        try:
            response = self.session.get(
                target_url,
                verify=verify_ssl,
                timeout=self.timeout,
                headers=headers
            )
            
            result['status_code'] = response.status_code
            result['success'] = True
            
            cookies = response.cookies
            cookie_names = []
            
            for cookie in cookies:
                cookie_info = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure
                }
                
                httponly = False
                if hasattr(cookie, '_rest'):
                    httponly = 'HttpOnly' in cookie._rest.keys()
                cookie_info['httponly'] = httponly
                
                result['cookies'].append(cookie_info)
                cookie_names.append(cookie.name)
            
            result['cookie_names'] = cookie_names
            
            return result
            
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            return result