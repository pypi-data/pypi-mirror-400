def normalise_ticker(ticker: str) -> str:
    if not ticker.endswith(".NS"):
        return ticker + ".NS"
    return ticker