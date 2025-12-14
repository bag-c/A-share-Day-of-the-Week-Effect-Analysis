# A股指数周内效应分析及策略回测
## 项目简介
【声明：本项目仅作探讨分析使用，不构成任何实质性投资建议。】
周内效应（Day-of-the-Week Effect）指股票市场在一周内某一天的平均收益率，相较于其他交易日存在统计上显著的高低差异。
本项目基于 Tushare 获取 2020-2024 年 A 股“上证综指”“上证 50”“沪深 300”“中证 500”“深证成指”5 大指数日线数据，分析指数周内涨跌幅效应，并回测“周二卖、周三买”极简交易策略，对比策略与上证综指的收益表现。

## 策略回测思路
1. 策略逻辑：基于周内效应分析结论，设计以上证综指为标的的“周二全仓卖出、周三全仓买入”单向交易策略；
2. 回测规则：初始本金 10 万元，交易时扣除 0.03% 手续费；以收盘价（close）作为买卖价格（不考虑开盘价），持仓期间跟随指数涨跌幅计算净值，空仓期间资金无收益；
3. 对比维度：将策略净值标准化后，与上证综指同期标准化净值对比，通过总收益率判断策略是否跑赢指数。
【拓展】若有兴趣，可基于本思路优化策略（如加入止损、多标的适配等）。

## 环境依赖
- 系统环境：Windows/macOS/Linux（需预装 Python 环境）；
- Python 版本：3.8 及以上；
- 数据库：本地安装并启动 MySQL 服务；
- 依赖包：pandas、pymysql、tushare、pyecharts；
- 安装命令：`pip install pandas pymysql tushare pyecharts`；
- 额外要求：Tushare Pro 账号需≥2000 积分（无积分会导致指数数据获取失败）。

## 运行步骤
1. 注册 Tushare Pro 账号并获取个人 Token（https://tushare.pro/），替换代码中的 `Your token`；
2. 本地安装 MySQL 并创建名为 `Tushare` 的数据库，替换代码中的 `Your password` 为本地 MySQL root 密码；
3. 确保 MySQL 服务已启动，运行 `main.py`，自动完成数据获取、存储、分析、可视化；
4. 可视化结果输出路径：
   - 周内效应折线图：`./output/line.html`；
   - 策略回测对比图：`./output/策略对比.html`。

## 核心功能
- 数据层：获取 5 大指数日线数据，自动存储至 MySQL 数据库；
- 分析层：通过 SQL 计算指数周一至周五的平均涨跌幅；
- 可视化层：生成周内效应趋势图、策略与指数净值对比图；
- 回测层：验证“周二卖、周三买”策略的收益及跑赢指数的效果。

## 结果说明
- 周内效应分析：输出 5 大指数周一至周五的平均涨跌幅趋势，直观展示周内收益差异；
- 策略回测结果：输出 2020-2024 年上证综指总收益率、策略总收益率，并明确策略是否跑赢指数。

## 结果分析与拓展
### 1. 策略未跑赢指数的核心原因
- 市场环境层面：2020-2024年A股整体呈震荡上行趋势，“频繁买卖（周二卖、周三买）”会产生额外手续费（0.03%/次），且空仓期间错过指数上涨收益，长期累积导致收益低于“持有不动”；
- 策略设计层面：仅基于“周内效应”单维度设计策略，未考虑宏观经济、行业轮动、成交量等核心因子，策略逻辑过于简单；
- 数据层面：Tushare指数数据为日线级别（收盘价），未考虑盘中波动，实际交易中买卖价格可能偏离收盘价，进一步影响收益。

### 2. 策略优化方向
- 手续费优化：降低交易频率（如改为“每周一次”而非“每周两次”），减少手续费损耗；
- 因子补充：加入成交量、均线等技术指标，筛选“周内效应+量能匹配”的交易日交易；
- 止损止盈：新增止损（如亏损5%平仓）、止盈（如盈利8%平仓）规则，控制风险；
- 多标的适配：将策略拓展至“中证500”等波动更大的指数，测试周内效应的适用性。


---  ---  ---


# Analysis and Strategy Backtesting of A-share Index Day-of-the-Week Effect
## Project Overview
【Disclaimer: This project is for research and analysis purposes only and does not constitute any substantive investment advice.】
The Day-of-the-Week Effect refers to the statistically significant difference in the average rate of return of the stock market on a specific day of the week compared to other trading days.
Based on Tushare, this project obtains daily data of 5 major A-share indices ("SSE Composite Index", "SSE 50 Index", "CSI 300 Index", "CSI 500 Index", "SZSE Component Index") from 2020 to 2024. It analyzes the day-of-the-week return rate effect of the indices, backtests the minimalist trading strategy of "Sell on Tuesday, Buy on Wednesday", and compares the return performance of the strategy with the SSE Composite Index.

## Strategy Backtesting Logic
1. Strategy Logic: Based on the conclusions of the day-of-the-week effect analysis, design a one-way trading strategy targeting the SSE Composite Index – "full position sell on Tuesday, full position buy on Wednesday";
2. Backtesting Rules: Initial principal of 100,000 CNY, with 0.03% handling fee deducted per transaction; use closing price as the trading price (opening price not considered); calculate net value based on index fluctuations during holding periods, with no return on funds during short positions;
3. Comparison Dimension: After normalizing the strategy's net value, compare it with the normalized net value of the SSE Composite Index over the same period, and judge whether the strategy outperforms the index through total return rate.
【Extension】For those interested, the strategy can be optimized based on this logic (e.g., adding stop-loss, multi-target adaptation, etc.).

## Environment Dependencies
- System Environment: Windows/macOS/Linux (Python environment pre-installed);
- Python Version: 3.8 or above;
- Database: Local MySQL service installed and running;
- Dependent Packages: pandas, pymysql, tushare, pyecharts;
- Installation Command: `pip install pandas pymysql tushare pyecharts`;
- Additional Requirement: Tushare Pro account with ≥2000 points (insufficient points will result in failure to obtain index data).

## Running Steps
1. Register a Tushare Pro account and obtain your personal Token (https://tushare.pro/), then replace `Your token` in the code;
2. Install MySQL locally, create a database named `Tushare`, and replace `Your password` in the code with your local MySQL root password;
3. Ensure the MySQL service is running, then run `main.py` to automatically complete data acquisition, storage, analysis, and visualization;
4. Output Path of Visualization Results:
   - Day-of-the-Week Effect Line Chart: `./output/line.html`;
   - Strategy Backtesting Comparison Chart: `./output/strategy_comparison.html`.

## Core Functions
- Data Layer: Obtain daily data of 5 major indices and automatically store it in the MySQL database;
- Analysis Layer: Calculate the average daily return rates of indices from Monday to Friday via SQL;
- Visualization Layer: Generate trend charts of the day-of-the-week effect and comparison charts of net values between the strategy and the index;
- Backtesting Layer: Verify the return of the "Sell on Tuesday, Buy on Wednesday" strategy and its effect of outperforming the index.

## Result Explanation
- Day-of-the-Week Effect Analysis: Output the trend of average daily return rates of 5 major indices from Monday to Friday, intuitively showing the intra-week return differences;
- Strategy Backtesting Result: Output the total return rate of the SSE Composite Index and the strategy from 2020 to 2024, and clearly indicate whether the strategy outperforms the index.

## Result Analysis and Extension
### 1. Core Reasons Why the Strategy Failed to Outperform the Index
- Market Environment: The A-share market showed an oscillating upward trend from 2020 to 2024. "Frequent trading (sell on Tuesday, buy on Wednesday)" generated additional handling fees (0.03% per transaction), and missing index rising returns during short positions led to lower long-term cumulative returns compared to "buy and hold";
- Strategy Design: The strategy was designed only based on the single dimension of "day-of-the-week effect", without considering core factors such as macroeconomics, industry rotation, and trading volume, resulting in overly simplistic logic;
- Data Layer: Tushare index data is at the daily level (closing price), without considering intraday fluctuations. In actual trading, trading prices may deviate from closing prices, further affecting returns.

### 2. Strategy Optimization Directions
- Handling Fee Optimization: Reduce trading frequency (e.g., once a week instead of twice a week) to reduce handling fee losses;
- Factor Supplement: Add technical indicators such as trading volume and moving averages to screen trading days that match "day-of-the-week effect + volume";
- Stop-Loss and Take-Profit: Add stop-loss (e.g., close position when loss reaches 5%) and take-profit (e.g., close position when profit reaches 8%) rules to control risks;
- Multi-Target Adaptation: Extend the strategy to more volatile indices such as the CSI 500 to test the applicability of the day-of-the-week effect.