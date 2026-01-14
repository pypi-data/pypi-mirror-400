from apscheduler.schedulers.blocking import BlockingScheduler
import psycopg2

def refresh_option_feeds():
    conn = psycopg2.connect(
        dbname="fudstop3",
        user="chuck",
        password="fud",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO public.option_feeds (
            feed, option_id, option_symbol, ticker, call_put, expiry, strike, insertion_timestamp,
            dte, ask_vol, bid_vol, ask_to_bid_vol_ratio, net_buy_vol, net_sell_vol,
            net_buy_notional, net_sell_notional, change_pct, close, high, low, range_pos,
            delta, gamma, iv, spread_pct_of_mid
        )
        SELECT
            feed, option_id, option_symbol, ticker, call_put, expiry, strike, insertion_timestamp,
            dte, ask_vol, bid_vol, ask_to_bid_vol_ratio, net_buy_vol, net_sell_vol,
            net_buy_notional, net_sell_notional, change_pct, close, high, low, range_pos,
            delta, gamma, iv, spread_pct_of_mid
        FROM public.option_feeds_live
        ON CONFLICT (feed, option_id) DO UPDATE
        SET
            insertion_timestamp = EXCLUDED.insertion_timestamp,
            dte               = EXCLUDED.dte,
            ask_vol           = EXCLUDED.ask_vol,
            bid_vol           = EXCLUDED.bid_vol,
            ask_to_bid_vol_ratio = EXCLUDED.ask_to_bid_vol_ratio,
            net_buy_vol       = EXCLUDED.net_buy_vol,
            net_sell_vol      = EXCLUDED.net_sell_vol,
            net_buy_notional  = EXCLUDED.net_buy_notional,
            net_sell_notional = EXCLUDED.net_sell_notional,
            change_pct        = EXCLUDED.change_pct,
            close             = EXCLUDED.close,
            high              = EXCLUDED.high,
            low               = EXCLUDED.low,
            range_pos         = EXCLUDED.range_pos,
            delta             = EXCLUDED.delta,
            gamma             = EXCLUDED.gamma,
            iv                = EXCLUDED.iv,
            spread_pct_of_mid = EXCLUDED.spread_pct_of_mid,
            created_at        = now(),
            expires_at        = now() + interval '10 minutes';

        DELETE FROM public.option_feeds WHERE expires_at < now();
    """)
    conn.commit()
    cur.close()
    conn.close()

scheduler = BlockingScheduler()
scheduler.add_job(refresh_option_feeds, 'interval', minutes=1)
scheduler.start()
