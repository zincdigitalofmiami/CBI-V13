"""
Features Pipeline - Institutional Grade Replacement

This module now uses the InstitutionalFeatureEngine for Wall Street-level
feature engineering instead of basic technical indicators.

Legacy compatibility maintained while providing:
- Real crush margin calculations
- BOPO spread analytics
- CFTC positioning sentiment
- Weather impact scoring
- Cross-category correlations
- Regime detection signals

Uses FREE_DATA_SOURCES for zero-cost institutional intelligence
"""

from datetime import datetime
import json
import logging

# Import the new institutional-grade feature engine
from pipelines.features_institutional import InstitutionalFeatureEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run():
    """
    Main feature engineering pipeline - now institutional grade

    Replaces basic indicators with Wall Street-level features:
    - Crush margins vs placeholder RSI=50
    - BOPO spreads vs simple moving averages
    - CFTC sentiment vs basic volume indicators
    - Multi-region weather scoring
    - Cross-category correlation analysis
    """

    logger.info("=" * 60)
    logger.info("SWITCHING TO INSTITUTIONAL-GRADE FEATURES")
    logger.info("Replacing placeholder indicators with Wall Street analytics")
    logger.info("=" * 60)

    try:
        # Use the new institutional feature engine
        engine = InstitutionalFeatureEngine()
        engine.run()

        logger.info("✓ Successfully completed institutional feature engineering")

    except Exception as e:
        logger.error(f"✗ Institutional features failed, falling back to basic indicators: {e}")

        # Fallback to basic features if institutional fails
        _run_basic_features()

        print(json.dumps({
            "status": "ok_fallback",
            "stage": "features",
            "note": "Used basic features as fallback",
            "ts": datetime.utcnow().isoformat()
        }))


def _run_basic_features():
    """
    Fallback to basic features if institutional engine fails
    Maintains backward compatibility
    """
    import pandas as pd
    from sqlalchemy import text
    from db.session import get_engine

    logger.info("Running basic feature fallback...")

    engine = get_engine()
    with engine.begin() as conn:
        prices = pd.read_sql(text("SELECT ds, symbol, close, volume FROM curated.prices_daily WHERE symbol = 'ZL=F' ORDER BY ds"), conn)

    if not prices.empty:
        # Improved basic indicators (real RSI instead of placeholder 50)
        tech = _compute_technical_improved(prices)

        with engine.begin() as conn:
            for _, r in tech.iterrows():
                conn.execute(
                    text(
                        """
                        INSERT INTO features.technical(ds, symbol, rsi, ma7, ma30, ma90, vol_z)
                        VALUES (:ds, :symbol, :rsi, :ma7, :ma30, :ma90, :vol_z)
                        ON CONFLICT (ds, symbol) DO UPDATE SET
                            rsi = EXCLUDED.rsi,
                            ma7 = EXCLUDED.ma7,
                            ma30 = EXCLUDED.ma30,
                            ma90 = EXCLUDED.ma90,
                            vol_z = EXCLUDED.vol_z
                        """
                    ),
                    {
                        "ds": r["ds"].date() if hasattr(r["ds"], "date") else r["ds"],
                        "symbol": r["symbol"],
                        "rsi": float(r["rsi"]),
                        "ma7": float(r["ma7"]) if pd.notna(r["ma7"]) else None,
                        "ma30": float(r["ma30"]) if pd.notna(r["ma30"]) else None,
                        "ma90": float(r["ma90"]) if pd.notna(r["ma90"]) else None,
                        "vol_z": float(r["vol_z"]) if pd.notna(r["vol_z"]) else None,
                    },
                )

    logger.info("✓ Basic features fallback completed")


def _compute_technical_improved(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Improved basic technical indicators - real calculations vs placeholders
    """
    df = prices.sort_values("ds").copy()

    # Real RSI calculation instead of placeholder 50
    df["rsi"] = _calculate_rsi(df["close"])

    # Moving averages
    df["ma7"] = df["close"].rolling(7).mean()
    df["ma30"] = df["close"].rolling(30).mean()
    df["ma90"] = df["close"].rolling(90).mean()

    # Volume z-score
    df["vol_z"] = (df["volume"] - df["volume"].rolling(60).mean()) / (df["volume"].rolling(60).std() + 1e-9)

    return df[["ds", "symbol", "rsi", "ma7", "ma30", "ma90", "vol_z"]].dropna()


def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate real RSI indicator - replaces placeholder RSI=50
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


if __name__ == "__main__":
    run()