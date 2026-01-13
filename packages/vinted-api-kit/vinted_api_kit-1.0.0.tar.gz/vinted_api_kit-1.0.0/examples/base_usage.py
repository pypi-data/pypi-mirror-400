import asyncio
import logging

from vinted import VintedClient, VintedError

logging.basicConfig(level=logging.INFO)


async def main():
    async with VintedClient(persist_cookies=True, storage_format="json") as client:
        try:
            items = await client.search_items(
                url="https://www.vinted.com/catalog?search_text=nike",
                per_page=10,
                order="newest_first",
            )

            print(f"Found {len(items)} items")

            for item in items[:3]:
                print(f"- {item.title} | {item.price} {item.currency}")

            if items:
                details = await client.item_details(items[0].url)
                print(f"\nFirst item details: {details.raw_data.keys()}")

        except VintedError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
