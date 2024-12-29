import pandas as pd
import numpy as np
import yfinance as yf
import holidays

# 한국의 공휴일 설정
kr_holidays = holidays.KR(years=range(2010, 2024))

# 실제 삼성전자의 주식 데이터 가져오기
ticker = '005930.KS'
start_date = '2010-01-01'
data = yf.download(ticker, start=start_date)

# 종가 데이터 확인
closing_prices = data['Close'].dropna()  # NaN 값 제거

# 공휴일 제거
closing_prices = closing_prices[~closing_prices.index.isin(kr_holidays)]

# 1. 일별 수익률 계산
daily_returns = closing_prices.pct_change().dropna()  # NaN 값 제거

# 2. 가장 수익률이 높은 10개의 날짜 찾기
if len(daily_returns) >= 10:
    top_10_returns = daily_returns.nlargest(10)
else:
    print("Not enough data to calculate top 10 returns.")
    top_10_returns = daily_returns

# 3. 해당 날짜의 종가에 매수하고 다음 거래일 종가에 매도
def calculate_trade_performance(dates, prices, returns):
    performances = []
    for date in dates:
        try:
            buy_price = prices.loc[date]
            next_day_index = prices.index.get_loc(date) + 1
            if next_day_index < len(prices):
                sell_price = prices.iloc[next_day_index]
                performance = (sell_price - buy_price) / buy_price
                daily_return = returns.loc[date] * 100  # 퍼센트로 변환
                performances.append((date.strftime('%Y-%m-%d'), buy_price, sell_price, performance, daily_return))
        except (IndexError, KeyError):
            # Skip if no next day exists
            continue
    return performances

if not top_10_returns.empty:
    trade_performances = calculate_trade_performance(top_10_returns.index, closing_prices, daily_returns)
else:
    trade_performances = []

# 4. 성과 정리
trade_summary = pd.DataFrame(trade_performances, columns=['Date', 'Buy Price', 'Sell Price', 'Return', 'Daily Return'])

if not trade_summary.empty:
    # 소수점 1자리로 양식 변경
    trade_summary['Buy Price'] = trade_summary['Buy Price'].round(1)
    trade_summary['Sell Price'] = trade_summary['Sell Price'].round(1)
                  trade_summary['Return'] = (trade_summary['Return'] * 100).round(1)  # 퍼센트로 변환
    trade_summary['Daily Return'] = trade_summary['Daily Return'].round(1)

    # 평균 수익률 계산 및 추가
    average_return = trade_summary['Return'].mean()
    average_row = pd.DataFrame([['Average', None, None, average_return, None]], columns=trade_summary.columns)
    trade_summary = pd.concat([trade_summary, average_row], ignore_index=True)

# 성과 출력
print(trade_summary)

# CSV로 저장하기 (선택 사항)
if not trade_summary.empty:
    trade_summary.to_csv('trade_summary.csv', index=False)
