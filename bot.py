from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from bs4 import BeautifulSoup
from colorama import *
import asyncio, json, time, os, pytz, base64, random

wib = pytz.timezone('Asia/Jakarta')

class NexyAi:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://point.nexyai.io",
            "Referer": "https://point.nexyai.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.nexyai.io/client"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.update_frequiency = random.randint(60, 65)

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Nexy Ai - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            x_name = parsed_payload.get("user", {}).get("metadata", {}).get("name", "Unknown")
            exp_time = parsed_payload.get("exp", None)
            
            return x_name, exp_time
        except Exception as e:
            return None, None
        
    def clear_desc(self, description: str):
        try:
            desc = BeautifulSoup(description, 'html.parser').get_text()
            return desc
        except Exception as e:
            return "No Description"
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=self.BASE_API, headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
            
    async def rewards_statistic(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/rewards/statistic"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def task_lists(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/tasks"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def completed_tasks(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user-tasks/completed"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def verify_tasks(self, token: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user-tasks/verify/{task_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_tasks(self, token: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user-tasks/claim/{task_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 400:
                            return None
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def process_check_connection(self, token: str, use_proxy: bool, rotate_proxy: bool):
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(token) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(token) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )
                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK {Style.RESET_ALL}          "
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )

        return True

    async def process_accounts(self, token: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(token, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
        
            total_pts = "N/A"
            balance = await self.rewards_statistic(token, proxy)
            if balance:
                social_pts = balance.get("data", {}).get("social",0)
                ref_pts = balance.get("data", {}).get("ref",0)
                follower_pts = balance.get("data", {}).get("follower",0)

                total_pts = social_pts + ref_pts + follower_pts

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {total_pts} PTS {Style.RESET_ALL}"
            )

            task_lists = await self.task_lists(token, proxy)
            if task_lists:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}")

                tasks = task_lists.get("data", [])
                if tasks:
                    for task in tasks:
                        if task:
                            task_id = task["id"]
                            title = task["title"]
                            description = task["description"]
                            reward = task["points"]

                            desc = self.clear_desc(description)

                            self.log(
                                f"{Fore.GREEN+Style.BRIGHT}  ● {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{desc}{Style.RESET_ALL}"
                            )

                            verify = await self.verify_tasks(token, task_id, proxy)
                            if verify:
                                status = verify.get("data", {}).get("status")

                                if status == "completed":
                                    claim = await self.claim_tasks(token, task_id, proxy)

                                    if claim:
                                        self.log(
                                            f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                            f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                                            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                                            f"{Fore.WHITE+Style.BRIGHT} {reward} PTS {Style.RESET_ALL}"
                                        )
                                    else:
                                        self.log(
                                            f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                            f"{Fore.YELLOW+Style.BRIGHT}Already Claimed{Style.RESET_ALL}"
                                        )

                                elif status == "in_progress":
                                    for remaining in range(self.update_frequiency, 0, -1):
                                        print(
                                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}     > {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}Wait for{Style.RESET_ALL}"
                                            f"{Fore.YELLOW + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}Seconds...{Style.RESET_ALL}",
                                            end="\r",
                                            flush=True
                                        )
                                        await asyncio.sleep(1)
                                        
                                    re_verify = await self.verify_tasks(token, task_id, proxy)
                                    if re_verify:
                                        current_status = re_verify.get("data", {}).get("status")

                                        if current_status == "completed":
                                            claim = await self.claim_tasks(token, task_id, proxy)
                                            if claim:
                                                self.log(
                                                    f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                                    f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                                    f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                                                    f"{Fore.WHITE+Style.BRIGHT} {reward} PTS {Style.RESET_ALL}"
                                                )
                                            else:
                                                self.log(
                                                    f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                                    f"{Fore.RED+Style.BRIGHT}Not Claimed{Style.RESET_ALL}                         "
                                                )
                                        else:
                                            self.log(
                                                f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                                f"{Fore.YELLOW+Style.BRIGHT}Not Ready to Claim{Style.RESET_ALL}               "
                                            )
                                    
                                    else:
                                        self.log(
                                            f"{Fore.MAGENTA+Style.BRIGHT}     > {Style.RESET_ALL}"
                                            f"{Fore.RED+Style.BRIGHT}GET Task Status Failed{Style.RESET_ALL}              "
                                        )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Lists Data Failed {Style.RESET_ALL}"
                )             

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 27
                for idx, token in enumerate(tokens, start=1):
                    if token:
                        x_name, exp_time = self.decode_token(token)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(tokens)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if x_name and exp_time:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Account   :{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {x_name} {Style.RESET_ALL}"
                            )
                            if int(time.time()) > exp_time:
                                self.log(
                                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT} Access Token Already Expired {Style.RESET_ALL}"
                                )
                                continue
                            
                            await self.process_accounts(token, use_proxy, rotate_proxy)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*64)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = NexyAi()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Nexy Ai - BOT{Style.RESET_ALL}                                       "                              
        )