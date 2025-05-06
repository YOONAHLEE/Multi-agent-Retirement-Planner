from pykis import KisAuth, KisQuote, PyKis
# 10 만원 입금 완료



# 실전투자용 한국투자증권 API를 생성합니다.
kis = PyKis(
    id="@2528895",  # HTS 로그인 ID
    account="43000733-01",  # 계좌번호
    appkey="PS9FErOojH7S1zPxQlrHKtDKbbBeNyb8XX48",  # AppKey 36자리
    secretkey="GWuMBYnOXQPh4usdzMPwLepuDgneV3VbP7Y1xR9NdsO+7kX4VtzgAMXNy3NCT82E9uAiC//5Lx/lO2DyeFeR9p222aENc8kQBzMn8fDMICvgAizrqCpeCZ81mgSJqMdbdfy8jaT5fDWRVz1VtA+38PfPzRBImt130JzWroy1DJSus2oj4io=",  # SecretKey 180자리
    keep_token=True,  # API 접속 토큰 자동 저장
)



# 엔비디아의 상품 객체를 가져옵니다.
stock = kis.stock("005930")

quote: KisQuote = stock.quote()
quote: KisQuote = stock.quote(extended=True) # 주간거래 시세

# PyKis의 모든 객체는 repr을 통해 주요 내용을 확인할 수 있습니다.
# 데이터를 확인하는 용도이므로 실제 프로퍼티 타입과 다를 수 있습니다.
print(quote)

from pykis import KisBalance

# 주 계좌 객체를 가져옵니다.
account = kis.account()

balance: KisBalance = account.balance()

print(repr(balance)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.