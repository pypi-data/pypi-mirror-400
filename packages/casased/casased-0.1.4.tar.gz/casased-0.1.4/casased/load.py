import requests
import pandas as pd
import datetime
from typing import Optional, Union
from .notation import notation_code


_USER_AGENT = {'User-Agent': 'Mozilla/5.0'}


def _resolve_isin(identifier: str) -> str:
    """Return an ISIN string for a given asset name or ISIN.
    If the identifier looks like an ISIN (starts with 'MA' or contains 'MA'), it's returned uppercased.
    Otherwise the notation mapping is used to find the ISIN by name (case-insensitive).
    """
    if not isinstance(identifier, str):
        raise ValueError("identifier must be a string (asset name or ISIN)")
    idu = identifier.strip()
    # simple ISIN heuristic
    if idu.upper().startswith("MA"):
        return idu.upper()
    for action in notation_code():
        if action["name"].lower() == idu.lower():
            return action["ISIN"]
    raise ValueError(f"Unknown asset name or ISIN: {identifier}")


def get_history(identifier: str, start: Optional[Union[str, datetime.date]] = None,
                end: Optional[Union[str, datetime.date]] = None, raise_on_error: bool = False) -> pd.DataFrame:
    """Get historical daily data for a listed asset (by name or ISIN) or for MASI/MSI20.

    If an error occurs while fetching/parsing data, the default behavior is to return an empty
    DataFrame and print a warning. Set ``raise_on_error=True`` to propagate exceptions.

    Returns a pandas DataFrame indexed by date with columns: Value, Min, Max, Variation, Volume
    """
    # Build link depending on identifier
    try:
        if identifier.upper() == "MASI":
            link = "https://medias24.com/content/api?method=getMasiHistory&periode=10y&format=json"
        elif identifier.upper() == "MSI20":
            link = "https://medias24.com/content/api?method=getIndexHistory&ISIN=msi20&periode=10y&format=json"
        else:
            isin = _resolve_isin(identifier)
            # default dates
            if start is None and end is None:
                start = "2011-09-18"
                end = str(datetime.datetime.today().date())
            # accept datetime.date or string
            s = pd.to_datetime(start).strftime("%Y-%m-%d")
            e = pd.to_datetime(end).strftime("%Y-%m-%d")
            link = f"https://medias24.com/content/api?method=getPriceHistory&ISIN={isin}&format=json&from={s}&to={e}"

        # Use centralized fetch helper which implements proxy fallback and SSL retry
        try:
            from .utils import fetch_url
            r = fetch_url(link, method='get', headers=_USER_AGENT, timeout=10)
            try:
                data = r.json()
            except ValueError:
                # Some proxies embed the JSON inside HTML; try to extract it
                import json, re
                m = re.search(r'({.*"result".*})', r.text, flags=re.S)
                if m:
                    data = json.loads(m.group(1))
                else:
                    raise
        except Exception:
            # Let outer try/except decide whether to raise or return empty DataFrame
            raise

        # stock price history: result is a list of records with date/Date etc.
        if "result" in data and isinstance(data["result"], list):
            df = pd.DataFrame(data["result"])
            # Normalize column names to title case for consistency
            df.columns = [c.strip().title() for c in df.columns]
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True).dt.date
                df.set_index("Date", inplace=True)
                return df
        # index history: result contains labels (timestamps)
        if "result" in data and isinstance(data["result"], dict):
            res = data["result"]
            if "labels" in res and isinstance(res["labels"], list):
                labels = [datetime.datetime.fromtimestamp(int(x)).date() for x in res["labels"]]
                values = None
                for k, v in res.items():
                    if k != "labels" and isinstance(v, list):
                        values = v
                        break
                if values is None:
                    return pd.DataFrame(res)
                df = pd.DataFrame(values, index=labels, columns=["Value"]) if not isinstance(values[0], list) else pd.DataFrame(values[0], index=labels, columns=["Value"]) 
                return df

        # parsing failed: return raw DataFrame
        return pd.DataFrame(data)

    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not load history for {identifier}: {e}")
        return pd.DataFrame()


# Backwards-compatible aliases
loadata = get_history


def loadmany(*args, start=None, end=None, feature: str = "Value", raise_on_error: bool = False) -> pd.DataFrame:
    """Load the data of many equities and return a DataFrame with one column per asset.

    Accepts either a list as single argument or multiple string arguments.

    If an individual asset fails to load, the function will insert an empty Series for that asset
    and continue unless ``raise_on_error=True``.
    """
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        assets = args[0]
    else:
        assets = list(args)
    result = pd.DataFrame()
    for asset in assets:
        try:
            df = get_history(asset, start=start, end=end)
        except Exception as e:
            if raise_on_error:
                raise
            print(f"Warning: could not load asset {asset}: {e}")
            result[asset] = pd.Series(dtype=float)
            continue
        if feature not in df.columns:
            if raise_on_error:
                raise ValueError(f"Feature '{feature}' not found for asset '{asset}'. Available: {list(df.columns)}")
            print(f"Warning: feature '{feature}' not found for asset '{asset}'; inserting empty column")
            result[asset] = pd.Series(dtype=float)
            continue
        result[asset] = df[feature]
    return result


def get_intraday(identifier: str, raise_on_error: bool = False) -> pd.DataFrame:
    """Get intraday data for an asset (name or ISIN), or market/index intraday for MASI/MSI20.

    Returns a DataFrame indexed by time (labels) with a 'Value' column. On failure the function
    returns an empty DataFrame unless ``raise_on_error=True``.
    """
    try:
        if identifier.upper() == "MASI":
            link = "https://medias24.com/content/api?method=getMarketIntraday&format=json"
        elif identifier.upper() == "MSI20":
            link = "https://medias24.com/content/api?method=getIndexIntraday&ISIN=msi20&format=json"
        else:
            isin = _resolve_isin(identifier)
            link = f"https://medias24.com/content/api?method=getStockIntraday&ISIN={isin}&format=json"

        # Use centralized fetch helper which implements proxy fallback and SSL retry
        try:
            from .utils import fetch_url
            r = fetch_url(link, method='get', headers=_USER_AGENT, timeout=10)
            try:
                data = r.json()
            except ValueError:
                import json, re
                m = re.search(r'({.*"result".*})', r.text, flags=re.S)
                if m:
                    data = json.loads(m.group(1))
                else:
                    raise
        except Exception:
            # Let outer try/except decide whether to raise or return empty DataFrame
            raise

        if "result" in data:
            res = data["result"]
            # Handle result as list (old format)
            if isinstance(res, list) and len(res) > 0:
                r = res[0]
                if "labels" in r and "data" in r:
                    df = pd.DataFrame(r.get("data") if isinstance(r.get("data"), list) else [r.get("data")], index=r["labels"])
                    df.index = pd.to_datetime(df.index, format='%H:%M').time
                    df.columns = ["Value"]
                    return df
            # Handle result as dict (new format)
            elif isinstance(res, dict) and "labels" in res:
                labels = res["labels"]
                values = res.get("data") or res.get("values")
                if values:
                    df = pd.DataFrame(values, index=labels, columns=["Value"])
                    df.index = pd.to_datetime(df.index, format='%H:%M').time
                    return df
        return pd.DataFrame(data)
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not load intraday for {identifier}: {e}")
        return pd.DataFrame()


# Backwards-compatible alias
getIntraday = get_intraday