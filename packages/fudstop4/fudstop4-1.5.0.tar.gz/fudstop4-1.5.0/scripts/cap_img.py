import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import io
import asyncio
from PIL import Image
from datetime import datetime
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from UTILS.ticker_dicts import ticker_hooks_dict
from imports import *
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
import asyncpg

# Database config and connection
DB_CONFIG = {
    "user": "chuck",
    "password": "fud",
    "database": "fudstop3",
    "host": "localhost",
    "port": 5432,
}

db_pool = None  # Global connection pool

async def init_db():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(**DB_CONFIG)

# Load image from DB and return PIL.Image
async def get_cap_flow_img(ticker: str, date: str):
    await init_db()

    parsed_date = datetime.strptime(date, "%Y%m%d").date()

    async with db_pool.acquire() as conn:
        query = """
            SELECT image FROM capital_flow_images
            WHERE ticker = $1 AND date = $2
            LIMIT 1
        """
        row = await conn.fetchrow(query, ticker, parsed_date)

    if row is None:
        print(f"[ERROR] No image found for {ticker} on {date}")
        return None

    image_bytes = row['image']
    image = Image.open(io.BytesIO(image_bytes))
    return image  # Return PIL image

# Main function to fetch date, get image, and post to Discord
from more_itertools import chunked 
async def main(ticker):
    await db.connect()
    try:
        query = f"""
            SELECT latest FROM capital_flow
            WHERE ticker = '{ticker}'
            ORDER BY insertion_timestamp DESC LIMIT 1
        """
        results = await db.fetch(query)
        date = [i.get('latest') for i in results][0]

        image = await get_cap_flow_img(ticker, date=date)
        if image is None:
            return

        # Convert image to PNG bytes
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        image_bytes = buf.read()

        # Send to Discord
        hook_url = ticker_hooks_dict.get(ticker)
        webhook = AsyncDiscordWebhook(url=hook_url)
        webhook.add_file(image_bytes, filename='flow.png')

        embed = DiscordEmbed(
            title=f"Capital Flow Chart: {ticker}",
            description=f"Latest data as of **{date}**",
            color='03b2f8'
        )
        embed.set_image(url='attachment://flow.png')

        webhook.add_embed(embed)
        await webhook.execute()
    except Exception as e:
        print(e)
async def run_main():
    """
    Entry point for posting capital flow images.  A single database
    connection is opened and reused for the duration of the run.  The
    function iterates through batches of tickers and dispatches tasks to
    send images to Discord.  A short sleep between batches helps to
    prevent hitting rate limits on the Discord webhook API.
    """
    batch_size = 7
    await db.connect()
    try:
        for batch in chunked(most_active_tickers, batch_size):
            tasks = [main(ticker) for ticker in batch]
            await asyncio.gather(*tasks)
            # optional cooldown to avoid hitting Discord API limits
            await asyncio.sleep(2)
    finally:
        # Always disconnect from the database when finished
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_main())