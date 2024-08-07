import aiohttp, asyncio, aiosqlite, random, os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, db_file=None, proxy_url=None, timeout=5, retries=3):
        if db_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_file = os.path.join(base_dir, 'proxies.db')
        self.db_file = db_file
        self.proxy_url = proxy_url or "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        self.timeout = timeout
        self.retries = retries
        
    async def initialize_db(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS active_proxies (
                    id INTEGER PRIMARY KEY,
                    ip TEXT,
                    port TEXT UNIQUE
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS dead_proxies (
                    id INTEGER PRIMARY KEY,
                    ip TEXT,
                    port TEXT UNIQUE
                )
            ''')
            await db.commit()
            logger.info("Database initialized")

    async def fetch_proxies(self, session):
        for attempt in range(self.retries):
            try:
                async with session.get(self.proxy_url) as response:
                    text = await response.text()
                    proxies = text.strip().split()
                    logger.info(f"Fetched {len(proxies)} proxies")
                    return proxies
            except Exception as e:
                logger.error(f"Error fetching proxies (Attempt {attempt + 1}/{self.retries}): {e}")
                await asyncio.sleep(1)
        return []

    async def filter_dead_proxies(self, proxies):
        async with aiosqlite.connect(self.db_file) as db:
            dead_proxies = await db.execute_fetchall('SELECT ip, port FROM dead_proxies')
            dead_proxies_set = {f"{ip}:{port}" for ip, port in dead_proxies}
            filtered_proxies = [proxy for proxy in proxies if proxy not in dead_proxies_set]
            logger.info(f"Filtered out {len(proxies) - len(filtered_proxies)} dead proxies")
        return filtered_proxies

    async def store_proxies(self, proxies):
        async with aiosqlite.connect(self.db_file) as db:
            for proxy in proxies:
                ip, port = proxy.split(':')
                await db.execute('INSERT OR IGNORE INTO active_proxies (ip, port) VALUES (?, ?)', (ip, port))
            await db.commit()
            logger.info(f"Stored {len(proxies)} active proxies")

    async def fetch_active_proxy(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute('SELECT ip, port FROM active_proxies') as cursor:
                proxies = await cursor.fetchall()
                return random.choice(proxies) if proxies else None

    async def report_dead_proxy(self, ip, port):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('DELETE FROM active_proxies WHERE ip = ? AND port = ?', (ip, port))
            await db.execute('INSERT INTO dead_proxies (ip, port) VALUES (?, ?)', (ip, port))
            await db.commit()
            logger.info(f"Reported dead proxy {ip}:{port}")

    async def validate_proxy(self, session, proxy):
        ip, port = proxy.split(':')
        proxy_url = f"http://{ip}:{port}"
        try:
            async with session.get('https://httpbin.org/ip', proxy=proxy_url, timeout=self.timeout) as response:
                if response.status == 200:
                    return proxy
        except Exception:
            pass
        return None

    async def refresh_proxies(self):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            proxies = await self.fetch_proxies(session)
            filtered_proxies = await self.filter_dead_proxies(proxies)
            validated_proxies = await asyncio.gather(*(self.validate_proxy(session, proxy) for proxy in filtered_proxies))
            validated_proxies = [proxy for proxy in validated_proxies if proxy is not None]
            await self.store_proxies(validated_proxies)

    async def make_request_with_proxy(self, method, url, **kwargs):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            proxy = await self.fetch_active_proxy()
            if not proxy:
                logger.info("No active proxies available, refreshing proxy list")
                await self.refresh_proxies()
                proxy = await self.fetch_active_proxy()
                if not proxy:
                    raise Exception("No proxies available after refresh")
            ip, port = proxy
            proxy_url = f"http://{ip}:{port}"
            try:
                async with session.request(method, url, proxy=proxy_url, **kwargs) as response:
                    if response.status == 200:
                        if response.headers.get('Content-Type', '').lower() == 'application/json':
                            return await response.json()
                        else:
                            return await response.text()
                    else:
                        logger.warning(f"Bad response status {response.status} with proxy {ip}:{port}")
            except Exception as e:
                logger.error(f"Dead Proxy {ip}:{port} - Retrying... Error: {e}")
                await self.report_dead_proxy(ip, port)
                return await self.make_request_with_proxy(method, url, **kwargs)