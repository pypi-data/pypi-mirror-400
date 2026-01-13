import asyncio
import logging

from vinted import VintedAuthError, VintedClient, VintedNetworkError

logging.basicConfig(level=logging.DEBUG)

"""

proxies избавится перименовать.

"""


async def main():
    proxies = {
        "http": "http://user:pass@proxy.example.com:8080",
        "https": "http://user:pass@proxy.example.com:8080",
    }

    client = VintedClient(
        locale="fr", proxies=proxies, persist_cookies=True, storage_format="mozilla"
    )

    try:
        items = await client.search_items(
            url="https://www.vinted.fr/catalog?search_text=zara", per_page=20
        )

        print(f"Found {len(items)} items from France")

    except VintedAuthError as e:
        print(f"Authentication failed: {e}")
    except VintedNetworkError as e:
        print(f"Network error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
