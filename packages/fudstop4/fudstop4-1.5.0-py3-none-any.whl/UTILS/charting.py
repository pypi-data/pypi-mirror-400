import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from imports import *
def generate_capital_flow_image(df: pd.DataFrame, ticker: str) -> bytes:
    if df.empty:
        raise ValueError("No data to plot.")

    # Color bars: green if value ≥ 0, red otherwise
    colors = ['limegreen' if v >= 0 else 'red' for v in df['value']]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4), facecolor='#111', dpi=150)
    ax.set_facecolor('#111')

    # Draw bars manually
    bars = ax.bar(df['category'], df['value'], color=colors, edgecolor='white', linewidth=0.6)

    ax.axhline(0, color='white', linewidth=0.8, linestyle='--')

    # Add labels to each bar
    for bar, value in zip(bars, df['value']):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + (0.02 * max(df['value'].abs())),
            f'{value:,.0f}',
            ha='center',
            va='bottom' if value >= 0 else 'top',
            fontsize=8,
            color='white'
        )

    ax.set_title(f"Capital Flow Breakdown - {ticker}", fontsize=12, color='white')
    ax.set_ylabel("Net Value ($)", color='white')
    ax.set_xlabel("Flow Type", color='white')

    ax.tick_params(colors='white', labelsize=8)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', color='gray', alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


async def store_capital_flow_image(ticker: str, date: str, image_bytes: bytes):
    query = """
    INSERT INTO capital_flow_images (ticker, date, image)
    VALUES ($1, $2, $3)
    ON CONFLICT (ticker, date) DO UPDATE SET image = EXCLUDED.image;
    """
    await db.execute(query, ticker, date, image_bytes)


def reshape_capital_flow_df(df: pd.DataFrame) -> pd.DataFrame:
    flow_columns = [
        'super_netflow', 'large_netflow', 'medium_netflow',
        'small_netflow', 'retail_inflow', 'retail_outflow',
        'major_netflow'
    ]

    existing_cols = [col for col in flow_columns if col in df.columns]
    if not existing_cols:
        return pd.DataFrame(columns=['category', 'value'])

    row = df.iloc[0]  # assume single row per ticker/date
    reshaped = pd.DataFrame({
        'category': existing_cols,
        'value': pd.to_numeric(row[existing_cols], errors='coerce')
    })

    reshaped = reshaped.dropna(subset=['value'])
    return reshaped