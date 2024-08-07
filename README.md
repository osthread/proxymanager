# ProxyManager Library

## Overview
ProxyManager is a Python library for efficiently managing and using HTTP proxies. It fetches, stores, rotates, and handles proxies for making HTTP requests.

## Features
- Fetch proxies from public APIs
- Store proxies in SQLite database
- Rotate proxies for HTTP requests
- Handle dead proxies
- Asynchronous operations

## Installation
Requires Python 3.7+. Install dependencies:
```
cd proxymanager
pip install .
```

### Usage
```
from proxymanager import ProxyManager

import asyncio

async def main():
    proxy_manager = ProxyManager()
    await proxy_manager.initialize_db()
    website = input("Enter a website (Example: https://google.com/): ")
    request_type = input("Enter a request type (Example: GET | POST | PUT): ")
    if website.lower() == "exit":
        quit()
        return
    
    response = await proxy_manager.make_request_with_proxy(request_type.upper(), website)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())
```

## ProxyManager Class

### Key Methods
- initialize_db(): Set up SQLite database
- fetch_proxies(session): Get proxies from API
- store_proxies(proxies): Save proxies to database
- fetch_active_proxy(): Get random active proxy
- report_dead_proxy(ip, port): Mark proxy as dead
- make_request_with_proxy(method, url, **kwargs): Make HTTP request using proxy

## Contributing
Fork the repository and submit a pull request.

## License
GNU3 License
