import hashlib
import random
import string
import time
import os
from dotenv import load_dotenv
load_dotenv()
def generate_webull_headers():
    """
    Dynamically generates headers for a Webull request.
    Offsets the current system time by 6 hours (in milliseconds) for 't_time'.
    Creates a randomized 'x-s' value each time.
    Adjust these methods of generation if you have more info on Webull's official approach.
    """
    # Offset by 6 hours
    offset_hours = 6
    offset_millis = offset_hours * 3600 * 1000

    # Current system time in ms
    current_millis = int(time.time() * 1000)
    t_time_value = current_millis - offset_millis

    # Generate a random string to feed into a hash
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    # Create an x-s value (example: SHA256 hash of random_str + t_time_value)
    x_s_value = hashlib.sha256(f"{random_str}{t_time_value}".encode()).hexdigest()

    # Build and return the headers
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "access_token": os.environ.get('access_token'),
        "app": "global",
        "app-group": "broker",
        "appid": "wb_web_app",
        "cache-control": "no-cache",
        "device-type": "Web",
        "did": "3uiar5zgvki16rgnpsfca4kyo4scy00a",
        "dnt": "1",
        "hl": "en",
        "origin": "https://app.webull.com",
        "os": "web",
        "osv": "i9zh",
        "platform": "web",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.webull.com/",
        "reqid": "kyiyrlq2kxig1vcwrdhcxvp3h5lc0_45",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "t_time": str(t_time_value),
        "tz": "America/Chicago",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "ver": "5.3.4",
        "x-s": x_s_value,
        "x-sv": "xodp2vg9"
    }

    return headers
