import pandas as pd
from sqlalchemy import text
from db.session import get_engine


def load_price_feature_matrix(symbol: str = "ZL=F") -> pd.DataFrame:
    engine = get_engine()
    with engine.begin() as conn:
        df = pd.read_sql(
            text(
                """
                SELECT p.ds, p.close,
                       t.rsi, t.ma7, t.ma30, t.ma90, t.vol_z
                FROM curated.prices_daily p
                LEFT JOIN features.technical t USING (ds, symbol)
                WHERE p.symbol = :sym
                ORDER BY p.ds
                """
            ),
            conn,
            params={"sym": symbol},
        )
    return df
