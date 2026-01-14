amarket
=======

Abstract Market (or "Any Market", or just "A Market") is a high-level implementation of market entities like Orders, Positions, etc. (Abstract market functions/classes, that works on any market.)

This module use only standard Python library and contain no external dependencies from anywhere, except OHLC-related parts of it, that requires `numpy` and `pandas` (and also `TA-Lib` for calculating technical analysis features over OHLC data)

## Overview

The `amarket` package provides a comprehensive framework for working with financial markets in a standardized way, abstracting away the specifics of different exchanges and trading platforms. It's designed to work with various market data sources while providing consistent interfaces for:

- Market representation (symbols, exchanges, timeframes)
- OHLC (Open-High-Low-Close) data handling
- Trading positions and orders
- Portfolio management and rebalancing
- Market data providers

## Key Components

### Core Interfaces
- `IMarket`: Abstract interface representing any trading market with specific symbol and timeframe
- `IOhlc`: Interface for OHLC data management
- `ITradingAccount`: Interface for trading account operations

### Base Classes
- `MarketBase`: Base class for implementing specific market functionality
- `Ohlc`: Class for managing OHLC time-series data with support for current and closed candles
- `Portfolio`: Class for portfolio management, including rebalancing and value calculation

### Modules
- **base/**: Core abstract classes and interfaces
- **interfaces/**: Abstract interfaces defining the contract for market components
- **ohlc/**: OHLC data handling and processing functionality
- **portfolio/**: Portfolio management capabilities
- **types/**: Type definitions used throughout the package

## Features

1. **Exchange Agnostic**: Designed to work with any exchange or trading platform through abstraction
2. **OHLC Data Management**: Robust handling of time-series market data with configurable timeframes
3. **Portfolio Management**: Tools for portfolio construction, rebalancing, and value tracking
4. **Singleton Pattern**: Market instances are managed as singletons to ensure consistency
5. **Thread Safety**: Built-in locking mechanisms for concurrent access

## Dependencies

The project requires standard Python libraries plus:
- `numpy>=2.3.1` (for amarket.ohlc and amarket.portfolio packages)
- `pandas>=2.3.0` (for amarket.ohlc)
- `TA-Lib>=0.6.4` (for amarket.ohlc.Featurizer)

## Usage

The package is designed to be extended by specific implementations for different exchanges or trading platforms, providing a consistent API while allowing for exchange-specific behavior.
