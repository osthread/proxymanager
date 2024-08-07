# ProxyManager Library

## Overview

The ProxyManager library provides an efficient and easy-to-use system for managing and utilizing HTTP proxies. It includes functionalities for fetching proxies from an online source, storing them in a SQLite database, rotating proxies for HTTP requests, and handling dead proxies to maintain a healthy proxy pool.

## Features

- **Proxy Fetching**: Retrieves fresh proxies from a public API.
- **Proxy Storage**: Stores active and dead proxies in a SQLite database.
- **Proxy Rotation**: Rotates through available proxies to make HTTP requests.
- **Dead Proxy Reporting**: Detects and reports dead proxies to keep the proxy pool healthy.
- **Asynchronous Operations**: Utilizes asynchronous operations for efficient handling of network requests and database interactions.

## Installation

To install the ProxyManager library, you need to have Python 3.7 or higher installed. You can install the required dependencies using pip:

pip install -r requirements.txt

## Usage

### Initial Setup

First, import the ProxyManager class and initialize the database:

import asyncio
from proxymanager import ProxyManager

async def setup():
    proxy_manager = ProxyManager()
    await proxy_manager.initialize_db()

asyncio.run(setup())

### Making Requests with Proxies

Use the make_request_with_proxy method to make HTTP requests with a rotated proxy:

import asyncio
from proxymanager import ProxyManager

async def main():
    proxy_manager = ProxyManager()
    await proxy_manager.initialize_db()
    response = await proxy_manager.make_request_with_proxy('GET', 'https://example.com')
    print(response)

asyncio.run(main())

### Example Script

An example script to demonstrate the usage of the ProxyManager library:

import asyncio
from proxymanager import ProxyManager

async def main():
    proxy_manager = ProxyManager()
    await proxy_manager.initialize_db()
    
    website = input("Enter a website (Example: https://google.com/): ")
    request_type = input("Enter a request type (Example: GET | POST | PUT): ")
    
    if website.lower() == "exit":
        return
    
    response = await proxy_manager.make_request_with_proxy(request_type.upper(), website)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())

## ProxyManager Class

### Methods

- __init__(self, db_file=None): Initializes the ProxyManager with the database file.
- initialize_db(self): Sets up the SQLite database with required tables.
- fetch_proxies(self, session): Fetches proxies from a public API.
- store_proxies(self, proxies): Stores fetched proxies into the database.
- fetch_active_proxy(self): Retrieves a random active proxy from the database.
- report_dead_proxy(self, ip, port): Reports and moves dead proxies to a separate table.
- make_request_with_proxy(self, method, url, **kwargs): Makes HTTP requests using a proxy, rotating and retrying if necessary.

## Contributing

Contributions are welcome! If you would like to contribute to the project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.