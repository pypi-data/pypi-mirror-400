import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import os
from dotenv import load_dotenv
load_dotenv()
from fudstop4.apis.nasdaq.nasdaq_sdk import Nasdaq
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
sdk = Nasdaq()




async def main():


    await db.connect()


    indicators = sdk.economic_indicators()


    print(indicators)


asyncio.run(main())