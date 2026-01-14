import sys
from pathlib import Path
import asyncio
import aiohttp
import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *

from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

url = "https://quotes-gw.webullfintech.com/api/wlas/screener/ng/query"

import json
import aiohttp

async def build_query(
    metric, metric_gte, metric_lte,
    pattern, term, sentiment,
    fetch=200,
    region="securities.region.name.6",
    sort_rule="wlas.screener.rule.price",
    sort_desc=True,
    brokerId=8,
    hkexPrivilege=False,
    extra_technicals=None  # Optional dict {pattern: {"term": [], "sentiment": []}}
):
    """
    Build and send a screener query for a metric and a technical pattern+term+sentiment.
    Pass extra_technicals to add more technical patterns, e.g. {"macd": {"term": ["long"], "sentiment": ["bull"]}}
    """
    rules = {
        "wlas.screener.rule.region": region,
        f"wlas.screener.rule.{metric}": f"gte={metric_gte}&lte={metric_lte}",
        f"wlas.screener.rule.{pattern}": json.dumps({
            "wlas.screener.value.term": [f"wlas.screener.value.term.{term}"],
            "wlas.screener.value.bullbear": [f"wlas.screener.value.bullbear.{sentiment}"]
        })
    }

    if extra_technicals:
        for patt, conf in extra_technicals.items():
            if (
                "term" in conf and conf["term"] and
                "sentiment" in conf and conf["sentiment"]
            ):
                rules[f"wlas.screener.rule.{patt}"] = json.dumps({
                    "wlas.screener.value.term": [f"wlas.screener.value.term.{t}" for t in conf["term"]],
                    "wlas.screener.value.bullbear": [f"wlas.screener.value.bullbear.{s}" for s in conf["sentiment"]]
                })
    
    payload = {
        "fetch": fetch,
        "rules": rules,
        "sort": {"rule": sort_rule, "desc": sort_desc},
        "attach": {"brokerId": brokerId, "hkexPrivilege": hkexPrivilege}
    }




    return payload


technical_patterns = [
    "boll", "fsto", "macd", "cci", "kst", "mom", "slowstach", "rsitech", "william",
    "classicsindicator", "adct", "cd", "flag", "dbt", "bttt", "hasbt", "pennant",
    "doublebt", "sct", "cw", "mbt", "tbt", "db", "rbt", "el", "eb", "hhm", "ihss",
    "ibt", "gravestone", "insidebar", "krb", "tbr", "outsidebar", "gud"
]
terms = ['inter', 'long', 'short']
sentiments = ['bull', 'bear']




id_to_ticker_map = {v: k for k, v in wb_opts.ticker_to_id_map.items()}
async def fetch_combo(session, pattern, term, sentiment):
    payload = await build_query(
        metric="volume", metric_gte="1", metric_lte="10000000000",
        pattern=pattern, term=term, sentiment=sentiment
    )
    async with session.post(url, json=payload) as resp:
        data = await resp.json()
        ticker_ids = data.get('tickerIdList', [])
        tickers = [id_to_ticker_map.get(i) for i in ticker_ids]
        # DataFrame for this combo
        df = pd.DataFrame({
            'pattern': [pattern] * len(tickers),
            'term': [term] * len(tickers),
            'sentiment': [sentiment] * len(tickers),
            'ticker_id': ticker_ids,
            'ticker': tickers
        })
        return df

async def main():
    dfs = []
    await db.connect()
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_combo(session, pattern, term, sentiment)
            for pattern in technical_patterns
            for term in terms
            for sentiment in sentiments
        ]
        results = await asyncio.gather(*tasks)
        dfs.extend(results)
    # Concatenate all into one DataFrame
    final_df = pd.concat(dfs, ignore_index=True)
    final_df = final_df[final_df['ticker'].notnull() & (final_df['ticker'] != None)]

    # Filter by active tickers
    final_df = final_df[final_df['ticker'].isin(most_active_tickers)]
    await db.batch_upsert_dataframe(final_df, table_name='wb_query', unique_columns=['pattern', 'term', 'sentiment', 'ticker'])
    # You can now save or use final_df as needed
    # final_df.to_csv('pattern_term_sentiment_results.csv', index=False)

# Run the async main
asyncio.run(main())







