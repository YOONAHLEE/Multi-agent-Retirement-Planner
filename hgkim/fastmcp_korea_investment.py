from mcp.server.fastmcp import FastMCP
from pykis import PyKis, KisQuote, KisBalance

# 실전투자용 한국투자증권 API를 생성합니다.
kis = PyKis(
    id="@2528895",  # HTS 로그인 ID
    account="43000733-01",  # 계좌번호
    appkey="PS9FErOojH7S1zPxQlrHKtDKbbBeNyb8XX48",  # AppKey 36자리
    secretkey="GWuMBYnOXQPh4usdzMPwLepuDgneV3VbP7Y1xR9NdsO+7kX4VtzgAMXNy3NCT82E9uAiC//5Lx/lO2DyeFeR9p222aENc8kQBzMn8fDMICvgAizrqCpeCZ81mgSJqMdbdfy8jaT5fDWRVz1VtA+38PfPzRBImt130JzWroy1DJSus2oj4io=",  # SecretKey 180자리
    keep_token=True,  # API 접속 토큰 자동 저장
)

mcp = FastMCP(
    "KoreaInvestment",  # Name of the MCP server
    instructions="한국투자증권 API를 통해 주식 시세와 계좌 잔고를 조회하는 도구입니다.",
    host="0.0.0.0",
    port=8010,
)

@mcp.tool()
async def get_stock_quote(stock_code: str, extended: bool = False) -> str:
    """
    주어진 종목 코드의 시세를 조회합니다.
    Args:
        stock_code (str): 종목 코드 (예: '005930')
        extended (bool): 주간거래 시세 여부
    Returns:
        str: 시세 정보 (repr)
    """
    stock = kis.stock(stock_code)
    quote: KisQuote = stock.quote(extended=extended)
    return repr(quote)

@mcp.tool()
async def get_account_balance() -> str:
    """
    계좌의 잔고를 조회합니다.
    Returns:
        str: 잔고 정보 (repr)
    """
    account = kis.account()
    balance: KisBalance = account.balance()
    return repr(balance)

if __name__ == "__main__":
    mcp.run(transport="stdio")
