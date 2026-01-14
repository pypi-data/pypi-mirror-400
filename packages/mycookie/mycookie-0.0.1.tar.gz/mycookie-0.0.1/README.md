# MyCookie

A lightweight Python package for extracting and analyzing cookies from any URL.

## Installation

```bash
pip install mycookie
```

## Quick Start

### Basic Usage
```python
import mycookie

# Get cookie names from a URL
cookie_names = mycookie.url("https://example.com")
print(cookie_names)
# Output: ['sessionid', 'csrftoken', 'auth_token']

# Alternative function
cookie_names = mycookie.find_cookies("https://example.com")
```

### Advanced Usage
```python
from mycookie import CookieFinder

# Create a custom finder
finder = CookieFinder(user_agent="MyBot/1.0", timeout=30)

# Get just cookie names
names = finder.from_url("https://example.com")

# Get detailed cookie information
details = finder.from_url_with_details("https://example.com")
```

## Usage Examples

### Example 1: Basic Cookie Extraction
```python
import mycookie

url = "https://httpbin.org/cookies/set/session/abc123"
cookies = mycookie.url(url)
print(cookies)
```
**Output:**
```
['session']
```

### Example 2: Multiple Cookies
```python
from mycookie import CookieFinder

finder = CookieFinder()
result = finder.from_url_with_details("https://httpbin.org/cookies/set?session=abc123&token=xyz789&user=john")

if result['success']:
    for cookie in result['cookies']:
        print(f"Name: {cookie['name']}")
        print(f"Value: {cookie['value']}")
        print(f"Domain: {cookie['domain']}")
        print(f"Secure: {cookie['secure']}")
        print("-" * 20)
    
    print(f"All cookie names: {result['cookie_names']}")
```
**Output:**
```
Name: session
Value: abc123
Domain: httpbin.org
Secure: False
--------------------
Name: token
Value: xyz789
Domain: httpbin.org
Secure: False
--------------------
Name: user
Value: john
Domain: httpbin.org
Secure: False
--------------------
All cookie names: ['session', 'token', 'user']
```

### Example 3: Error Handling
```python
import mycookie

try:
    cookies = mycookie.url("https://invalid-site-12345.com")
    print(cookies)
except Exception as e:
    print(f"Failed to fetch cookies: {type(e).__name__}")
```
**Output:**
```
Failed to fetch cookies: ConnectionError
```

### Example 4: With Custom Headers
```python
from mycookie import CookieFinder

finder = CookieFinder()
cookies = finder.from_url(
    "https://example.com",
    custom_headers={
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'value'
    }
)
print(cookies)
```

### Example 5: Real Website Example
```python
import mycookie

# Test on a real website
websites = [
    "https://github.com",
    "https://stackoverflow.com",
    "https://httpbin.org"
]

for site in websites:
    try:
        cookies = mycookie.url(site)
        print(f"{site}: {len(cookies)} cookie(s) found")
        if cookies:
            print(f"  Cookies: {', '.join(cookies)}")
    except Exception as e:
        print(f"{site}: Error - {type(e).__name__}")
```


## Use Cases

1. **Security Testing**: Check what cookies a website sets
2. **Web Scraping**: Extract session cookies for authenticated scraping
3. **Monitoring**: Track cookie changes on websites
4. **Debugging**: Analyze cookie behavior during development
5. **Compliance**: Check for secure cookie settings

## License

MIT License

## Links

- [PyPI Package](https://pypi.org/project/mycookie/)
- [GitHub Repository](https://github.com/bytebreach/mycookie)
- [Issue Tracker](https://github.com/bytebreach/mycookie/issues)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
1. Check the [GitHub Issues](https://github.com/bytebreach/mycookie/issues)
2. Create a new issue if needed

