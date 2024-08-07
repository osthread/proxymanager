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