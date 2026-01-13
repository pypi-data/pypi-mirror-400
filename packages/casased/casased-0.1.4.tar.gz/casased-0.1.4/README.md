# casased

<p align="center">
<img src="media/casased.png" alt="casased logo">
</p>

**casased** — Casablanca Stock Exchange Data Retriever

A Python library to retrieve historical and intraday data from the Casablanca Stock Exchange (Bourse de Casablanca) using the [Medias24 API](https://medias24.com/bourse).

[![PyPI version](https://badge.fury.io/py/casased.svg)](https://pypi.org/project/casased/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 📈 **Historical Data**: Daily OHLCV data for all listed stocks
- 📊 **Index Data**: MASI and MSI20 historical data
- ⏱️ **Intraday Data**: Real-time intraday prices
- 🏦 **Multiple Assets**: Load data for multiple stocks at once
- 📋 **Company Info**: Session data, key indicators, dividends
- 📉 **Market Overview**: Index summaries and weights

## Installation

```bash
pip install casased
```

## Quick Start

```python
import casased as cas

# List available assets
assets = cas.notation()

# Get historical data for a stock
df = cas.get_history('BCP', start='2024-01-01', end='2024-12-31')

# Get MASI index history
masi = cas.get_history('MASI')

# Load multiple assets
banks = cas.loadmany(['BCP', 'CIH', 'Attijariwafa'], start='2024-01-01', end='2024-12-31')

# Get intraday data
intraday = cas.get_intraday('BCP')
```

## API Reference

### Historical Data

#### `get_history(identifier, start=None, end=None)`

Get historical daily data for a stock or index.

```python
# Stock data
df = cas.get_history('Addoha', start='2024-01-01', end='2024-06-30')

# Index data
masi = cas.get_history('MASI')
msi20 = cas.get_history('MSI20')
```

**Returns**: DataFrame with columns: `Value`, `Min`, `Max`, `Variation`, `Volume`

#### `loadmany(*assets, start=None, end=None, feature='Value')`

Load data for multiple assets.

```python
# Load closing prices
df = cas.loadmany(['BCP', 'CIH', 'BOA'], start='2024-01-01', end='2024-12-31')

# Load volumes
volumes = cas.loadmany(['BCP', 'CIH'], feature='Volume')
```

### Intraday Data

#### `get_intraday(identifier)`

Get intraday prices for a stock or index.

```python
# Stock intraday
intraday = cas.get_intraday('BCP')

# Market intraday
market = cas.get_intraday('MASI')
```

### Company Information

#### `getCours(name)`

Get session data, latest transactions, and order book.

```python
cours = cas.getCours('BOA')
# Returns: {'Données_Seance', 'Meilleur_limit', 'Dernieres_Tansaction', 'Seance_prec'}
```

#### `getKeyIndicators(name)`

Get company key indicators and financial ratios.

```python
indicators = cas.getKeyIndicators('Attijariwafa')
# Returns: {'Info_Societe', 'Actionnaires', 'Chiffres_cles', 'Ratio'}
```

#### `getDividend(name)`

Get dividend history.

```python
dividends = cas.getDividend('BOA')
```

### Market Overview

#### `getIndex()`

Get all index summaries.

```python
index = cas.getIndex()
# Returns: {'Resume indice', 'Indice rentabilite', 'Indices en devises', 'Indice FTSE', 'Indices sectoriels'}
```

#### `getPond()`

Get index weights (pondération).

```python
weights = cas.getPond()
```

#### `getIndexRecap()`

Get session recap with top gainers/losers.

```python
recap = cas.getIndexRecap()
```

### Utilities

#### `notation()`

Get list of all available asset names.

```python
assets = cas.notation()
```

#### `get_isin_by_name(name)`

Get ISIN code for an asset.

```python
isin = cas.get_isin_by_name('BCP')  # Returns 'MA0000011884'
```

## Data Sources

- **Historical & Intraday Data**: [Medias24 API](https://medias24.com/bourse)
- **Company Info & Market Data**: [Bourse de Casablanca](https://www.casablanca-bourse.com)

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- pandas
- lxml

## Example Notebook

See [casased_exemple.ipynb](casased_exemple.ipynb) for a complete demonstration of all features.

## Release Notes

- **v0.1.2** — 2026-01-06 — Documentation cleanup, branding updates
- **v0.1.1** — 2026-01-06 — Remove demo videos, update branding
- **v0.1.0** — Initial release

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

- GitHub: [QuantBender/casased](https://github.com/QuantBender/casased)
- Twitter: [@AmineAndam](https://twitter.com/AmineAndam)
- LinkedIn: [ANDAM AMINE](https://www.linkedin.com/in/amineandam/)
