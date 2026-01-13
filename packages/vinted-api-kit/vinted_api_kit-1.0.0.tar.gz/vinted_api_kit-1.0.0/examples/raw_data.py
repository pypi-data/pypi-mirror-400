import asyncio

from vinted import VintedClient


async def main():
    async with VintedClient() as client:
        raw_items = await client.search_items(
            url="https://www.vinted.com/catalog?brand_ids[]=53", raw_data=True
        )

        print(f"Raw data type: {type(raw_items)}")
        print(f"First item keys: {raw_items[0].keys()}")

        raw_details = await client.item_details(
            url="https://www.vinted.com/items/1234-test", raw_data=True
        )

        print(f"Raw details keys: {raw_details.keys()}")


if __name__ == "__main__":
    asyncio.run(main())
