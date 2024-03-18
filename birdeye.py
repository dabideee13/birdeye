import os
from typing import NamedTuple

import requests
from dotenv import load_dotenv

load_dotenv()


class Config:
    BIRD_EYE_TOKEN: str = os.environ['BIRD_EYE_TOKEN']


class PriceInfo(NamedTuple):
    price: float


class TokenOverview(NamedTuple):
    address: str
    decimals: int
    liquidity: float
    logoURI: str
    mc: float
    symbol: str
    v24hChangePercent: float
    v24hUSD: float
    name: str
    lastTradeUnixTime: int


class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": Config.BIRD_EYE_TOKEN,
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(self, token_addresses: list[str]) -> dict[str, PriceInfo]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
        if not token_addresses:
            raise ValueError("No tokens provided.")

        prices = {}

        for address in token_addresses:
            url = f"https://public-api.birdeye.so/public/price?address={address}"
            try:
                resp = self._make_api_call("GET", url)
                data = resp.json()
                prices[address] = PriceInfo(price=data['value'])
            except (ValueError, KeyError):
                raise ValueError(f"Invalid response received for token: {address}")

        return prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
        """
        url = f"https://public-api.birdeye.so/defi/token_overview?address={address}"
        try:
            resp = self._make_api_call("GET", url)
            data = resp.json()
            return TokenOverview(
                address=data['address'],
                decimals=data['decimals'],
                liquidity=data['liquidity'],
                logoURI=data['logoURI'],
                mc=data['mc'],
                symbol=data['symbol'],
                v24hChangePercent=data['v24hChangePercent'],
                v24hUSD=data['v24hUSD'],
                name=data['name'],
                lastTradeUnixTime=data['lastTradeUnixTime']
            )
        except (ValueError, KeyError):
            raise ValueError(f"Invalid response received for token overview: {address}")