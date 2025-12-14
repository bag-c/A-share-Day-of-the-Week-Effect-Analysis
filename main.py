import pandas as pd
import pymysql
import tushare as ts
from pyecharts.charts import Line
from pyecharts import options as opts

print("\n" + "="*50)
print("开始执行：周内效应数据获取及可视化")
print("="*50)

#初始化Tushare Pro接口
try:
    token = 'Your token'  
    pro = ts.pro_api(token)
except Exception as e:
    print(f"Tushare初始化失败：{e}")
    exit()

#获取数据
#上证综指:000001.SH，深证成指:399001.SZ，上证50:000016.SH，沪深300:000300.SH，中证500:000905.SH
codes = ['000001.SH','399001.SZ','000016.SH','000300.SH','000905.SH']

#时间数据时间范围：2020-2024年
start_date = '20200101'
end_date = '20241231'

#空列表用于存储数据
df_list = []

#获取指数日线数据（index_daily接口自动过滤休市日，无需额外筛选）
for code in codes:
    try:
        data = pro.index_daily(
            ts_code=code, 
            start_date=start_date, 
            end_date=end_date,
            fields=['ts_code','trade_date','open','high','low','close','pre_close','vol']
            #获取的日指数表格中常含有的字段（仅用于分析）
            )
        df_list.append(data)
        print(f"成功获取{code}数据")
        
    except Exception as e: 
        print(f"!!! 获取{code}数据失败：{e}")
        df_list.append(pd.DataFrame())
        continue

df_all = pd.concat(df_list, ignore_index = True) # 合并数据（重置索引，避免重复）

#连接数据库
try:
    conn =  pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Your password',
                        database='Tushare', charset='utf8mb4') 

    #创建游标
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Tushare.`index_daily`;")

    #创建数据表
    create_table_sql = '''
    CREATE TABLE Tushare.`index_daily` (
    `ts_code` varchar(20) NOT NULL COMMENT '指数代码',
    `trade_date` date NOT NULL COMMENT '交易日期',
    `open` float(10,4) NOT NULL COMMENT '开盘价',
    `high` float(10,4) NOT NULL COMMENT '最高价',
    `low` float(10,4) NOT NULL COMMENT '最低价',
    `close` float(10,4) NOT NULL COMMENT '收盘价',
    `pre_close` float(10,4) NOT NULL COMMENT '昨日收盘价',
    `vol` BIGINT NOT NULL COMMENT '成交量（手）',          #BIGINT是大整数类型
    PRIMARY KEY (`ts_code`, `trade_date`)                              # 联合主键，避免重复数据
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A股指数日线数据';  #InnoDB可读性更高
    '''
    #执行SQL语句
    cur.execute(create_table_sql)
    conn.commit()

    #插入数据
    for index, row in df_all.iterrows():
        insert_SQL = '''
        INSERT INTO tushare.index_daily
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        trade_date = pd.to_datetime(row['trade_date']).strftime('%Y-%m-%d')  # 转为'年-月-日'格式
        row_data = (row['ts_code'], trade_date, row['open'], row['high'], row['low'], row['close'], row['pre_close'], row['vol'])
        cur.execute(insert_SQL, row_data)
    conn.commit()
    
    query_sql = '''
    SELECT 
        ts_code, 
        WEEKDAY(trade_date)+1 as day_of_week, 
        AVG((close-pre_close)/pre_close) AS 平均涨跌幅

    FROM Tushare.index_daily
    GROUP BY ts_code, WEEKDAY(trade_date)+1
    ORDER BY ts_code, day_of_week;
    '''
    cur.execute(query_sql)
    data = list(cur.fetchall())

    #数据可视化

    #创建折线图对象,设置主题颜色
    line = Line(init_opts=opts.InitOpts(theme='light', width='80%', height='600px'))

    #设置图例名称
    name = ["上证综指", "上证50", "沪深300","中证500","深证成指"]

    #设置x轴数据
    week = ['星期一', '星期二', '星期三', '星期四', '星期五']

    #提取每组数据中的第三个数据”涨跌幅“ 作为y轴数据
    y_data = []
    for i in data:
        y_data.append(i[2])

    #添加x轴数据
    line.add_xaxis(xaxis_data=week)

    #添加y轴数据
    for i in range(5):
        y_axis = y_data[i*5:(i+1)*5]
        line.add_yaxis(series_name=name[i], y_axis=y_axis, label_opts=opts.LabelOpts(is_show=False))

    #设置全局配置项
    line.set_global_opts(
        #加入标题
        title_opts=opts.TitleOpts(title='5大指数周内平均涨跌幅趋势', pos_left='center'),
        xaxis_opts = opts.AxisOpts(name='周几'),
        yaxis_opts = opts.AxisOpts(name='平均涨跌幅', 
                                #保留4位小数
                                axislabel_opts=opts.LabelOpts(formatter="{value:4f}")),
        legend_opts = opts.LegendOpts(pos_top='10%', is_show=True)                     
    )

    line.render("./output/line.html")
    print("可视化文件路径：./output/line.html")

except Exception as e:
    print(f'运行失败：{e}')

#即使不报错也不泄露资源
finally:
    #判断游标是否存在
    if 'cur' in locals():
        cur.close()
    #判断连接是否存在
    if 'conn' in locals():
        conn.close()




#验证周内效应，创建策略：在有仓的情况下，逢周二全仓买进指数，逢周三全仓卖出指数，并且进行简单回测
print("\n" + "="*50)
print("开始执行：周二卖、周三买的策略回测")
print("="*50)


try:
    df_strategy = pro.index_daily(
        ts_code='000001.SH',       #选择与上证综指对比
        start_date=start_date,
        end_date=end_date
    )
    if df_strategy.empty:
        raise ValueError("df_strategy 数据为空，无法执行回测")

    #数据准备
    df_strategy['trade_date'] = pd.to_datetime(df_strategy['trade_date'])       #转换时间类型便于计算
    df_strategy = df_strategy.sort_values('trade_date').set_index('trade_date') #重新设置行索引并排序
    df_strategy['weekday'] = df_strategy.index.weekday + 1   #将weekday转化为星期，1=周一，2=周二
    df_strategy['daily_return'] = df_strategy['close'].pct_change()   #使用函数pct_change()获取日涨跌幅

    #开始假设，验证策略
    initial_money = 100000 #假设有10万本金
    remain = initial_money #定义余额变量remain，交易前余额等于本金,动态更新的资金,反映实时资金状态
    hold = True  #是否持仓
    strategy_value = [] #策略净值，动态反映策略在不同时间的累计收益情况

    #遍历行索引，列索引
    for date,row in df_strategy.iterrows():
        weekday = row['weekday']
        ret = row['daily_return']

        #计算当日净值
        #持仓或数据有效的情况下，当日净值等于余额*涨跌幅
        if hold and not pd.isna(ret):          
            current_value = remain * (1 + ret)   
        #不持仓或数据无效，余额不变 
        else:   
            current_value = remain
        strategy_value.append(current_value)

        #交易规则：周二卖，周三买
        if weekday == 2:
            hold = False    #空仓，代表卖出
            remain= current_value*(1-0.0003)   #扣除手续费
        elif weekday == 3:
            hold = True     #持仓，代表买入
            remain = current_value*(1-0.0003)

    #校验策略净值长度与数据行数是否相等
    if len(strategy_value) != len(df_strategy):
        raise ValueError(f"策略净值长度({len(strategy_value)})与数据行数({len(df_strategy)})不匹配")
    
    #整理数据并且对比
    df_strategy['strategy_value'] = strategy_value  #将策略净值存储到DataFrame中
    df_strategy['index_norm'] = df_strategy['close'] / df_strategy['close'].iloc[0]  #代表指数线的纵坐标
    df_strategy['strategy_norm'] = df_strategy['strategy_value'] / initial_money   #代表策略线的纵坐标

    #创建回测折线图对象
    line_strategy = Line(init_opts=opts.InitOpts(width='80%', height='600px'))

    #x轴：每30天取一个点，避免拥挤
    x_axis = []
    for i in df_strategy.index[::30]:
        i_str = i.strftime('%Y-%m-%d')
        x_axis.append(i_str) #转换数据类型为字符串’年-月-日‘，作为x的横坐标
    #指数线纵坐标
    index_val = df_strategy['index_norm'].iloc[::30].round(3).tolist()
    #策略线纵坐标
    strategy_val = df_strategy['strategy_norm'].iloc[::30].round(3).tolist()

    line_strategy.add_xaxis(x_axis)
    line_strategy.add_yaxis(
        '上证综指',
        index_val,
        label_opts=opts.LabelOpts(is_show=False)
    )
    line_strategy.add_yaxis(
        '周二卖周三买策略',
        strategy_val,
        label_opts=opts.LabelOpts(is_show=False)
    )
    line_strategy.set_global_opts(
        title_opts=opts.TitleOpts(title='上证综指 vs 周二卖周三买策略（2020-2024）',
                                    pos_left='50%'),
        legend_opts=opts.LegendOpts(pos_left='20%'),
        yaxis_opts=opts.AxisOpts(name="标准化净值（初始=1）")
    )
    #保存图片
    line_strategy.render("./output/策略对比.html")

    final_index_return = (df_strategy['close'].iloc[-1] / df_strategy['close'].iloc[0] - 1) * 100
    final_strategy_return = (df_strategy['strategy_value'].iloc[-1] / initial_money - 1) * 100

    print("回测周期：2020-2024年")
    print(f"上证综指总收益率：{final_index_return:.2f}%")
    print(f"周二卖周三买策略总收益率：{final_strategy_return:.2f}%")
    print(f"策略是否跑赢指数：{'是' if final_strategy_return > final_index_return else '否'}")
    print("!!!!!  策略对比图表已生成：./output/策略对比.html")

except Exception as e:
    print(f'运行失败{e}')

print("!!!!!  周内效应可视化图文件路径：./output/line.html")
print('!!!!!!!!!!  项目完成  !!!!!!!!!!')