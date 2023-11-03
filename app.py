import plotly.graph_objs as go
from flask import Flask, render_template
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask import Response, json, jsonify, send_file, render_template_string
from flask_mysqldb import MySQL
# plot
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
from plotly.subplots import make_subplots
import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
app = Flask(__name__)
app.secret_key = 'Duong Nam'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_PORT'] = 3333
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '1234abC@'
# app.config['MYSQL_DB'] = 'stock_db'
# app.config['MYSQL_DATABASE_AUTH_PLUGIN'] = 'mysql_native_password'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3308
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stock_db'
app.config['MYSQL_DATABASE_AUTH_PLUGIN'] = 'mysql_native_password'
mysql = MySQL(app)

#D1

# @app.route("/")
# @app.route('/cand/<timeframe>/<ticker>', methods=['GET', 'POST'])
# def create_cand_chart(timeframe="d1", ticker="TCH"):
#     cur = mysql.connection.cursor()

#     if timeframe == "m1":
#         table_name = "m1"
#     elif timeframe == "m15":
#         table_name = "m15"
#     elif timeframe == "m30":
#         table_name = "m30"
#     elif timeframe == "h1":
#         table_name = "h1"
#     elif timeframe == "d1":
#         table_name = "d1"
#     else:
#         return "Khung giờ không hợp lệ"

#     # Truy vấn SQL để lấy giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch của ngày mới nhất
#     cur.execute(f"SELECT open, close, high, low, volume FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 1", (ticker,))
#     latest_data = cur.fetchone()

#     if latest_data:
#         open_price, close_price, high_price, low_price, volume = latest_data
#     else:
#         open_price, close_price, high_price, low_price, volume = None, None, None, None, None

#     # cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 100", (ticker,))
#     cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s" , (ticker,))
#     records = cur.fetchall()

#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # df = df.sort_values(by='time', ascending=True).reset_index(drop=True)

#     fig = go.Figure(data=[go.Candlestick(
#         x=df['time'],
#         open=df['open'],
#         high=df['high'],
#         low=df['low'],
#         close=df['close']
#     )])

#     fig.update_layout(
#         xaxis_title='Thời gian',
#         yaxis_title='Giá',
#         plot_bgcolor='#363636',
#         xaxis_gridcolor='gray',
#         yaxis_gridcolor='gray',
#         xaxis_rangeslider_visible=True
#     )

#     plot_html = fig.to_html(full_html=False)

#     cur.execute("SELECT DISTINCT ticker FROM d1")
#     stock_codes = [code[0] for code in cur.fetchall()]

#     return render_template("/chart/cand/cand.html", plot_cand=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe, open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price, volume=volume)
# @app.route("/")
@app.route('/cand/<timeframe>/<ticker>/<start_year>/<end_year>', methods=['GET', 'POST'])
def create_cand1Y_chart(timeframe="d1", ticker="TCH", start_year = 2016, end_year = 2023):
    cur = mysql.connection.cursor()

    if timeframe == "m1":
        table_name = "m1"
    elif timeframe == "m15":
        table_name = "m15"
    elif timeframe == "m30":
        table_name = "m30"
    elif timeframe == "h1":
        table_name = "h1"
    elif timeframe == "d1":
        table_name = "d1"
    else:
        return "Khung giờ không hợp lệ"

    # Truy vấn SQL để lấy giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch của ngày mới nhất
    cur.execute(f"SELECT open, close, high, low, volume FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 1", (ticker,))
    latest_data = cur.fetchone()

    if latest_data:
        open_price, close_price, high_price, low_price, volume = latest_data
    else:
        open_price, close_price, high_price, low_price, volume = None, None, None, None, None
    start_time = start_year
    end_time = end_year 
    start_year = datetime(int(start_year), 1, 1, 7, 0, 0).timestamp()
    end_year = datetime(int(end_year), 1, 1, 7, 0, 0).timestamp()

    # cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 100", (ticker,))
    cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s AND time_stamp >= {str(start_year)} AND time_stamp <= {str(end_year)}" , (ticker,))
    records = cur.fetchall()

    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df = pd.DataFrame.from_records(records, columns=columnName)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
    df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    # df = df.sort_values(by='time', ascending=True).reset_index(drop=True)

    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])

    fig.update_layout(
        xaxis_title='Thời gian',
        yaxis_title='Giá',
        plot_bgcolor='#363636',
        xaxis_gridcolor='gray',
        yaxis_gridcolor='gray',
        xaxis_rangeslider_visible=True
    )

    plot_html = fig.to_html(full_html=False)

    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/cand/cand.html", plot_cand=plot_html, ticker=ticker, stock_codes=stock_codes, start_time = start_time, end_time = end_time,
                           selected_timeframe=timeframe, open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price, volume=volume)


#get 3month
@app.route('/cand3M/<timeframe>/<ticker>', methods=['GET', 'POST'])
def create_cand_chart_100(timeframe="d1", ticker="TCH"):
    cur = mysql.connection.cursor()

    if timeframe == "m1":
        table_name = "m1"
    elif timeframe == "m15":
        table_name = "m15"
    elif timeframe == "m30":
        table_name = "m30"
    elif timeframe == "h1":
        table_name = "h1"
    elif timeframe == "d1":
        table_name = "d1"
    else:
        return "Khung giờ không hợp lệ"

    # Truy vấn SQL để lấy giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch của ngày mới nhất
    cur.execute(f"SELECT open, close, high, low, volume FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 1", (ticker,))
    latest_data = cur.fetchone()

    if latest_data:
        open_price, close_price, high_price, low_price, volume = latest_data
    else:
        open_price, close_price, high_price, low_price, volume = None, None, None, None, None

    cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 66", (ticker,))
    # cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s", (ticker,))
    records = cur.fetchall()

    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df = pd.DataFrame.from_records(records, columns=columnName)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
    df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    df = df.sort_values(by='time', ascending=True).reset_index(drop=True)

    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])

    fig.update_layout(
        xaxis_title='Thời gian',
        yaxis_title='Giá',
        plot_bgcolor='#363636',
        xaxis_gridcolor='gray',
        yaxis_gridcolor='gray',
        xaxis_rangeslider_visible=True
    )

    plot_html = fig.to_html(full_html=False)

    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/cand/cand3M.html", plot_cand=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe, open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price, volume=volume)
# @app.route("/")
@app.route("/analyst/d1/<ticker>", methods=['GET', 'POST'])
def analyst(ticker = "TCH"):
    cur = mysql.connection.cursor()
    
    # Truy vấn dữ liệu từ SQL
    cur.execute(f"SELECT * FROM d1 WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 100", (ticker,))
    cur.execute(f"SELECT * FROM d1 WHERE ticker = %s", (ticker,))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df = pd.DataFrame.from_records(records, columns=columnName)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
    df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    # df = df.sort_values(by='time', ascending=True).reset_index(drop=True)
    # Tính trung bình trượt 20 ngày
    df['20_day_sma'] = df['close'].rolling(window=20).mean()

    # Tính độ lệch chuẩn 20 ngày
    df['20_day_std'] = df['close'].rolling(window=20).std()

    # Tính Bollinger Bands
    df['upper_band'] = df['20_day_sma'] + (df['20_day_std'] * 2)
    df['lower_band'] = df['20_day_sma'] - (df['20_day_std'] * 2)

    # Tạo biểu đồ Bollinger Bands sử dụng Plotly
    fig_bb = go.Figure()

    # Hiển thị dữ liệu Giá và Bollinger Bands
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=5)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma'], mode='lines', name='Trung bình 20 ngày',line=dict(color='#FBAC20',  dash='dot',  width=3)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['upper_band'], mode='lines', name='Dải trên Bollinger Bands', line=dict(color='#555555',  width=4)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['lower_band'],fill='tonexty', mode='lines', name='Dải dưới Bollinger Bands', line=dict(color='#555555',  width=3)))

    # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng và ẩn các đường kẻ dọc
    fig_bb.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),  # Ẩn đường kẻ dọc trên trục x
                    yaxis=dict(title='Giá'),  # Ẩn đường kẻ dọc trên trục y
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1)) # Màu của đường kẻ ngang
    # Chuyển biểu đồ Plotly thành HTML
    plot_bb = fig_bb.to_html(full_html=False)
     # Tính trung bình trượt 5 ngày và 20 ngày
    df['5_day_sma'] = df['close'].rolling(window=5).mean()
    df['20_day_sma_2'] = df['close'].rolling(window=20).mean()

    # Tạo biểu đồ tương tác
    fig_ma = go.Figure()

    # Hiển thị dữ liệu Giá cổ phiếu và MA(5) và MA(20)
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=5)))
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['5_day_sma'], mode='lines', name='MA(5)', line=dict(color='#FBAC20',  dash='dot',width=3)))
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma_2'], mode='lines', name='MA(20)', line=dict(color='#64BAFF',  dash='dot', width=3)))

    # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng
    fig_ma.update_layout(title='Biểu đồ Giá cổ phiếu và MA(5) và MA(20)',
                    xaxis=dict(title='Thời gian',  showgrid=False),
                    yaxis=dict(title='Giá'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang
    plot_ma = fig_ma.to_html(full_html=False)
    
        # Tính đường MACD (Moving Average Convergence Divergence)
    short_term = df['close'].ewm(span=12).mean()
    long_term = df['close'].ewm(span=26).mean()
    df['MACD'] = short_term - long_term

    # Tính đường Tín hiệu (Signal Line)
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # Tính MACD Histogram
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

    # Tạo biểu đồ MACD sử dụng Plotly
    fig_macd = go.Figure()

    # Hiển thị dữ liệu MACD và Signal Line
    fig_macd.add_trace(go.Scatter(x=df['time'], y=df['MACD'], mode='lines', name='MACD', line=dict(color='#FF3747', width=5)))
    fig_macd.add_trace(go.Scatter(x=df['time'], y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='#64BAFF', width=5)))

    # Tạo biểu đồ Histogram
    fig_macd.add_trace(go.Bar(x=df['time'], y=df['MACD_Histogram'], name='MACD Histogram', marker=dict(color='#64BAFF')))

    # Cài đặt thuộc tính cho biểu đồ
    fig_macd.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='Giá trị'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ

    plot_macd = fig_macd.to_html(full_html=False)
    
     # Tính %K và %D
    period = 14  # Kỳ giao dịch
    smooth = 3   # Độ trơn
    df['low_min'] = df['low'].rolling(window=period).min()
    df['high_max'] = df['high'].rolling(window=period).max()
    df['%K'] = 100 * (df['close'] - df['low_min']) / (df['high_max'] - df['low_min'])
    df['%D'] = df['%K'].rolling(window=smooth).mean()

    # Tạo biểu đồ Stochastic Oscillator sử dụng Plotly
    fig_stoch = go.Figure()

    # Hiển thị dữ liệu %K và %D
    fig_stoch.add_trace(go.Scatter(x=df['time'], y=df['%K'], mode='lines', name='%K (màu xanh)', line=dict(color='#64BAFF', width=5)))
    fig_stoch.add_trace(go.Scatter(x=df['time'], y=df['%D'], mode='lines', name='%D (màu đỏ)', line=dict(color='#FF3747', width=5)))

    # Vẽ đường giới hạn 20 và 80
    fig_stoch.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=20,
            y1=20,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    fig_stoch.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=80,
            y1=80,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    # Cài đặt thuộc tính cho biểu đồ
    fig_stoch.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='%'),
                    xaxis_rangeslider_visible=True,
                    yaxis_range=[0, 100],
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ
    plot_stoch = fig_stoch.to_html(full_html=False)
    
    # Tính chỉ số RSI(14)
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    print(rsi.head(20))

    # Tạo biểu đồ RSI(14) với đường giới hạn 30 và 70
    fig_rsi = go.Figure()

    # Hiển thị dữ liệu RSI(14)
    fig_rsi.add_trace(go.Scatter(x=df['time'], y=rsi, mode='lines', name='RSI(14)', line=dict(color='#FBAC20', width = 5)))

    # Thêm đường giới hạn 30 và 70
    fig_rsi.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=30,
            y1=30,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    fig_rsi.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=70,
            y1=70,
            line=dict(color="white", dash="dash", width = 2),
        )
    )

    # Đặt các thuộc tính cho biểu đồ
    fig_rsi.update_layout(title='RSI(14) với Đường Giới Hạn 30 và 70',
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='RSI'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ
    plot_rsi = fig_rsi.to_html(full_html=False)
    
    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/analyst/analyst.html", plot_bb=plot_bb, plot_ma = plot_ma, plot_macd = plot_macd, plot_stoch = plot_stoch, plot_rsi = plot_rsi, ticker=ticker, stock_codes=stock_codes)

#get 3 month record
@app.route("/analyst3M/d1/<ticker>", methods=['GET', 'POST'])
def analyst_3m(ticker = "TCH"):
    cur = mysql.connection.cursor()
    
    # Truy vấn dữ liệu từ SQL
    cur.execute(f"SELECT * FROM d1 WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 66", (ticker,))
    # cur.execute(f"SELECT * FROM d1 WHERE ticker = %s", (ticker,))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df = pd.DataFrame.from_records(records, columns=columnName)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
    df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    df = df.sort_values(by='time', ascending=True).reset_index(drop=True)
    # Tính trung bình trượt 20 ngày
    df['20_day_sma'] = df['close'].rolling(window=20).mean()

    # Tính độ lệch chuẩn 20 ngày
    df['20_day_std'] = df['close'].rolling(window=20).std()

    # Tính Bollinger Bands
    df['upper_band'] = df['20_day_sma'] + (df['20_day_std'] * 2)
    df['lower_band'] = df['20_day_sma'] - (df['20_day_std'] * 2)

    # Tạo biểu đồ Bollinger Bands sử dụng Plotly
    fig_bb = go.Figure()

    # Hiển thị dữ liệu Giá và Bollinger Bands
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=5)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma'], mode='lines', name='Trung bình 20 ngày',line=dict(color='#FBAC20',  dash='dot',  width=3)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['upper_band'], mode='lines', name='Dải trên Bollinger Bands', line=dict(color='#555555',  width=4)))
    fig_bb.add_trace(go.Scatter(x=df['time'], y=df['lower_band'],fill='tonexty', mode='lines', name='Dải dưới Bollinger Bands', line=dict(color='#555555',  width=3)))

    # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng và ẩn các đường kẻ dọc
    fig_bb.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),  # Ẩn đường kẻ dọc trên trục x
                    yaxis=dict(title='Giá'),  # Ẩn đường kẻ dọc trên trục y
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1)) # Màu của đường kẻ ngang
    # Chuyển biểu đồ Plotly thành HTML
    plot_bb = fig_bb.to_html(full_html=False)
     # Tính trung bình trượt 5 ngày và 20 ngày
    df['5_day_sma'] = df['close'].rolling(window=5).mean()
    df['20_day_sma_2'] = df['close'].rolling(window=20).mean()

    # Tạo biểu đồ tương tác
    fig_ma = go.Figure()

    # Hiển thị dữ liệu Giá cổ phiếu và MA(5) và MA(20)
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=5)))
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['5_day_sma'], mode='lines', name='MA(5)', line=dict(color='#FBAC20',  dash='dot',width=3)))
    fig_ma.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma_2'], mode='lines', name='MA(20)', line=dict(color='#64BAFF',  dash='dot', width=3)))

    # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng
    fig_ma.update_layout(title='Biểu đồ Giá cổ phiếu và MA(5) và MA(20)',
                    xaxis=dict(title='Thời gian',  showgrid=False),
                    yaxis=dict(title='Giá'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang
    plot_ma = fig_ma.to_html(full_html=False)
    
        # Tính đường MACD (Moving Average Convergence Divergence)
    short_term = df['close'].ewm(span=12).mean()
    long_term = df['close'].ewm(span=26).mean()
    df['MACD'] = short_term - long_term

    # Tính đường Tín hiệu (Signal Line)
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # Tính MACD Histogram
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

    # Tạo biểu đồ MACD sử dụng Plotly
    fig_macd = go.Figure()

    # Hiển thị dữ liệu MACD và Signal Line
    fig_macd.add_trace(go.Scatter(x=df['time'], y=df['MACD'], mode='lines', name='MACD', line=dict(color='#FF3747', width=5)))
    fig_macd.add_trace(go.Scatter(x=df['time'], y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='#64BAFF', width=5)))

    # Tạo biểu đồ Histogram
    fig_macd.add_trace(go.Bar(x=df['time'], y=df['MACD_Histogram'], name='MACD Histogram', marker=dict(color='#64BAFF')))

    # Cài đặt thuộc tính cho biểu đồ
    fig_macd.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='Giá trị'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ

    plot_macd = fig_macd.to_html(full_html=False)
    
     # Tính %K và %D
    period = 14  # Kỳ giao dịch
    smooth = 3   # Độ trơn
    df['low_min'] = df['low'].rolling(window=period).min()
    df['high_max'] = df['high'].rolling(window=period).max()
    df['%K'] = 100 * (df['close'] - df['low_min']) / (df['high_max'] - df['low_min'])
    df['%D'] = df['%K'].rolling(window=smooth).mean()

    # Tạo biểu đồ Stochastic Oscillator sử dụng Plotly
    fig_stoch = go.Figure()

    # Hiển thị dữ liệu %K và %D
    fig_stoch.add_trace(go.Scatter(x=df['time'], y=df['%K'], mode='lines', name='%K (màu xanh)', line=dict(color='#64BAFF', width=5)))
    fig_stoch.add_trace(go.Scatter(x=df['time'], y=df['%D'], mode='lines', name='%D (màu đỏ)', line=dict(color='#FF3747', width=5)))

    # Vẽ đường giới hạn 20 và 80
    fig_stoch.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=20,
            y1=20,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    fig_stoch.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=80,
            y1=80,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    # Cài đặt thuộc tính cho biểu đồ
    fig_stoch.update_layout(
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='%'),
                    xaxis_rangeslider_visible=True,
                    yaxis_range=[0, 100],
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ
    plot_stoch = fig_stoch.to_html(full_html=False)
    
    # Tính chỉ số RSI(14)
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    print(rsi.head(20))

    # Tạo biểu đồ RSI(14) với đường giới hạn 30 và 70
    fig_rsi = go.Figure()

    # Hiển thị dữ liệu RSI(14)
    fig_rsi.add_trace(go.Scatter(x=df['time'], y=rsi, mode='lines', name='RSI(14)', line=dict(color='#FBAC20', width = 5)))

    # Thêm đường giới hạn 30 và 70
    fig_rsi.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=30,
            y1=30,
            line=dict(color="white", dash="dash", width = 3),
        )
    )
    fig_rsi.add_shape(
        go.layout.Shape(
            type="line",
            x0=df['time'].min(),
            x1=df['time'].max(),
            y0=70,
            y1=70,
            line=dict(color="white", dash="dash", width = 2),
        )
    )

    # Đặt các thuộc tính cho biểu đồ
    fig_rsi.update_layout(title='RSI(14) với Đường Giới Hạn 30 và 70',
                    xaxis=dict(title='Thời gian', showgrid=False),
                    yaxis=dict(title='RSI'),
                    xaxis_rangeslider_visible=True,
                    plot_bgcolor='#363636',  # Màu nền của biểu đồ
                    paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
                    xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
                    yaxis_gridcolor='gray',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1))# Màu của đường kẻ ngang đồ
    plot_rsi = fig_rsi.to_html(full_html=False)
    
    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/analyst/analyst3M.html", plot_bb=plot_bb, plot_ma = plot_ma, plot_macd = plot_macd, plot_stoch = plot_stoch, plot_rsi = plot_rsi, ticker=ticker, stock_codes=stock_codes)
@app.route('/mcdx/<timeframe>/<ticker>', methods=['GET', 'POST'])
def create_mcdx_chart(timeframe="m15", ticker="TCH"):
    cur = mysql.connection.cursor()

    if timeframe == "m1":
        table_name = "m1_intraday_table"
    elif timeframe == "m15":
        table_name = "m15_intraday_table"
    elif timeframe == "h1":
        table_name = "h1_intraday_table"
    elif timeframe == "d1":
        table_name = "d1_intraday_table"
    else:
        return "Khung giờ không hợp lệ"


    cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s", (ticker,))
    records = cur.fetchall()

    columnName = ['ticker', 'time_stamp', 'percent_sheep_buy', 'percent_shark_sell', 'percent_shark_buy', 'percent_wolf_sell', 'percent_wolf_buy', 'percent_sheep_sell', "avg_price", "sum_vol", "order_count"]
    df = pd.DataFrame.from_records(records, columns=columnName)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
    df['time'] = df['time_stamp'].dt.tz_localize('UTC')

    df["Sharks"] = (df["percent_shark_sell"] + df["percent_shark_buy"]) 
    df["Wolfs"] = (df["percent_wolf_sell"] + df["percent_wolf_buy"]) 
    df["Sheeps"] = (df["percent_sheep_sell"] + df["percent_sheep_buy"]) 


    df['5_day_sma'] = df['Sharks'].rolling(window=5).mean()

    # Tạo biểu đồ cột thanh miền
    fig = px.bar(df, x='time', y=["Sharks", "Wolfs", "Sheeps"],
                labels={'variable': 'Class', 'value': 'Value'},
                title='Biểu đồ cột thanh miền',
                barmode='relative',
                color_discrete_sequence=['#ef5350','#fdff06', '#42ad39'])
    fig.add_trace(go.Scatter(x=df['time'], y=df['5_day_sma'], mode='lines', name='MA(5)', line=dict(color='#2196f3',  width = 3)))
    fig.update_xaxes(type='category',
                    showticklabels=False)

    plot_html = fig.to_html(full_html=False)

    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/analyst/mcdx.html", plot_mcdx=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe)

@app.route('/mcdx_new/<timeframe>/<ticker>', methods=['GET', 'POST'])
def create_mcdx_new_chart(timeframe="m15", ticker="TCH"):
    cur = mysql.connection.cursor()

    if timeframe == "m1":
        table_name = "m1_intraday_table"
    elif timeframe == "m15":
        table_name = "m15_intraday_table"
    elif timeframe == "h1":
        table_name = "h1_intraday_table"
    elif timeframe == "d1":
        table_name = "d1_intraday_table"
    else:
        return "Khung giờ không hợp lệ"


    cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s", (ticker,))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'percent_sheep_buy', 'percent_shark_sell', 'percent_shark_buy', 'percent_wolf_sell', 'percent_wolf_buy', 'percent_sheep_sell', "avg_price", "sum_vol", "order_count"]
    df_intraday = pd.DataFrame.from_records(records, columns=columnName)
    df_intraday['time_stamp'] = pd.to_datetime(df_intraday['time_stamp'], unit='s')
    df_intraday['time'] = df_intraday['time_stamp'].dt.tz_localize('UTC')
    df_intraday["Sharks"] = (df_intraday["percent_shark_sell"] + df_intraday["percent_shark_buy"]) 
    df_intraday["Wolfs"] = (df_intraday["percent_wolf_sell"] + df_intraday["percent_wolf_buy"]) 
    df_intraday["Sheeps"] = (df_intraday["percent_sheep_sell"] + df_intraday["percent_sheep_buy"]) 


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        name="Shark",
        x=df_intraday['time'], y=df_intraday['Sharks'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#990000'),
        stackgroup='one',
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
        
    ))

    fig.add_trace(go.Scatter(
        name="Wolf",
        x=df_intraday['time'], y=df_intraday['Wolfs'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#999900'),
        stackgroup='one'
    ))

    fig.add_trace(go.Scatter(
        name="Sleep",
        x=df_intraday['time'], y=df_intraday['Sheeps'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#66CC00'),
        stackgroup='one'
    ))

    fig.update_xaxes(type='category',
                        showticklabels=False)

    fig.update_layout(
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))

    plot_html = fig.to_html(full_html=False)
    
    fig_all = go.Figure()

    fig_all.add_trace(go.Scatter(
        name="Shark sell",

        x=df_intraday['time'], y=df_intraday['percent_shark_sell'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#990000'),
        stackgroup='one'
    ))

    fig_all.add_trace(go.Scatter(
        name="Shark buy",
        x=df_intraday['time'], y=df_intraday['percent_shark_buy'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#FF3333'),
        stackgroup='one'
    ))

    fig_all.add_trace(go.Scatter(
        name="Wolf sell",
        x=df_intraday['time'], y=df_intraday['percent_wolf_sell'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#999900'),
        stackgroup='one'
    ))

    fig_all.add_trace(go.Scatter(
        name="Wolf buy",
        x=df_intraday['time'], y=df_intraday['percent_wolf_buy'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#FFFF33'),
        stackgroup='one'
    ))

    fig_all.add_trace(go.Scatter(
        name="Sleep sell",
        x=df_intraday['time'], y=df_intraday['percent_sheep_sell'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#66CC00'),
        stackgroup='one'
    ))

    fig_all.add_trace(go.Scatter(
        name="Sleep buy",
        x=df_intraday['time'], y=df_intraday['percent_sheep_buy'],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5, color='#00CC66'),
        stackgroup='one', # define stack group
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
    ))

    fig_all.update_xaxes(type='category',
                        showticklabels=False)

    fig_all.update_layout(
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))
    
    plot_all = fig_all.to_html(full_html=False)
    
    labels = ['Sheeps','Wolf','Shark']
    values = [df_intraday['percent_sheep_buy'].values[0], df_intraday['percent_wolf_buy'].values[0], df_intraday['percent_shark_buy'].values[0]]
    fig_pie_buy = go.Figure(data=[go.Pie(labels=labels, values=values)])
    plot_pie_buy = fig_pie_buy.to_html(full_html=False)
    labels = ['Sheeps','Wolf','Shark']
    values = [df_intraday['percent_sheep_sell'].values[0], df_intraday['percent_wolf_sell'].values[0], df_intraday['percent_shark_sell'].values[0]]
    fig_pie_sell = go.Figure(data=[go.Pie(labels=labels, values=values)])
    plot_pie_sell = fig_pie_sell.to_html(full_html=False)

    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/analyst/mcdx_new.html", plot_mcdx=plot_html, plot_mcdx_all=plot_all,ticker=ticker, plot_pie_buy = plot_pie_buy,
                            plot_pie_sell = plot_pie_sell,stock_codes=stock_codes, selected_timeframe=timeframe)


@app.route('/treemap/<timeframe>', methods=['GET', 'POST'])
def create_treemap(timeframe="daylyArray"):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT DISTINCT d1.time_stamp FROM d1;
    """)
    records = cur.fetchall()
    columnName = ['timestamp']
    timestamp_table = pd.DataFrame.from_records(records, columns=columnName)['timestamp'].values
    timestamp_table = np.sort(timestamp_table)
    
    dict_industry_code = {
        "Bán lẻ": "5300",
        "Bất động sản": "8600",
        "Dầu khí": "0500",
        "Dịch vụ tài chính": "8700",
        "Điện, nước & xăng dầu khí đốt": "7500",
        "Ngân hàng": "8300",
        "Viễn thông": "6500",
        "Xây dựng và Vật liệu": "2300",
        "Y tế": "4500",
        "Bảo hiểm": "8500",
        "Công nghệ Thông tin": "9500",
        "Du lịch và Giải trí": "5700",
        "Hàng & Dịch vụ Công nghiệp": "2700",
        "Hàng cá nhân & Gia dụng": "3700",
        "Hóa chất": "1300",
        "Ô tô và phụ tùng": "3300",
        "Thực phẩm và đồ uống": "3500",
        "Tài nguyên Cơ bản": "1700",
        "Truyền thông": "5500"
    }
    selected_industries = list(dict_industry_code.keys())

    # #day
    # daylyArray = timestamp_table[-2:]
    # #week
    # weekArray = timestamp_table[-8:]
    # #month
    # monthArray = timestamp_table[-31:]

    if timeframe == "daylyArray":
        selected_timeframe = timestamp_table[-2:]
    elif timeframe == "weekArray":
        selected_timeframe = timestamp_table[-8:]
    elif timeframe == "monthArray":
        selected_timeframe = timestamp_table[-31:]
    else:
        return "Khung giờ không hợp lệ"
    
    if request.method == 'POST':
        selected_timeframe = request.form.get('timeframe')
        
        selected_industries = request.form.getlist('industry')
        print(selected_industries)
        if (len(selected_industries) == 0):
            selected_industries = list(dict_industry_code.keys())
        
        if selected_timeframe == "daylyArray": 
            selected_timeframe = timestamp_table[-2:]
        elif selected_timeframe == "weekArray":
            selected_timeframe = timestamp_table[-8:]
        elif selected_timeframe == "monthArray":
            selected_timeframe = timestamp_table[-31:]
        else:
            return "Khung giờ không hợp lệ"
        
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[0]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp_pr', 'open_pr', 'low_pr', 'high_pr', 'close_pr', 'volume_pr', 'sum_price_pr']
    df_price_previous = pd.DataFrame.from_records(records, columns=columnName)
    
    #target
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[-1]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df_price = pd.DataFrame.from_records(records, columns=columnName)
    df_price = df_price.set_index('ticker').join(df_price_previous.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price = df_price[['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'close_pr']]
    #append infomation
    cur.execute("""SELECT ct.ticker, ct.comGroupCode, ct.organName, ct.organShortName, it.industry_name 
    FROM company ct
    JOIN company_subgroup cs ON ct.ticker = cs.id_company
    JOIN group_subgroup gs ON gs.id_subgroup = cs.id_subgroup
    JOIN industry_group ig ON ig.id_group = gs.id_group
    JOIN industry it ON it.id_industry = ig.id_industry
    """)
    records = cur.fetchall()
    columnName = ['ticker', 'comGroupCode', 'organName', 'organShortName', 'industry_name']
    df = pd.DataFrame.from_records(records, columns=columnName)

    data_result = df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    data_result = data_result[(data_result['industry_name'].isin(selected_industries))]
    print(data_result['industry_name'].unique())
    data_result['percent'] = pd.to_numeric((data_result['close'] - data_result['close_pr'])/data_result['close_pr'])
    data_result = data_result.fillna(0)
    
    def checkTypeUpdown(x):
        if x == 0:
            return '0'
        if x < 0:
            if x <= -0.067 and timeframe == "daylyArray":
                return '-2'
            return '-1'
        if x >= 0.067 and timeframe == "daylyArray":
            return '2'
        return '1'
    
    data_result['type'] = data_result['percent'].apply(checkTypeUpdown)

    fig = px.treemap(data_result, 
                    path=['industry_name','ticker'],
                    values='volume',
                    labels='ticker',
                    color='type',
                    color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                    hover_data=['percent','organName'],
                    )

    fig.data[0].customdata[:,0] = np.where(fig.data[0].customdata[:,0] != '(?)', fig.data[0].customdata[:,0]*100, '(?)')
    fig.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"

    plot = fig.to_html(full_html=False)
    
    fig_vn30 = px.treemap(data_result, path=['comGroupCode','ticker'],
                 color='type',
                 color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                 hover_data=['percent','organName'],
                 values='volume',
                #  width=2000,
                #  height=1000
                 )
    fig_vn30.data[0].customdata[:,0] = np.where(fig_vn30.data[0].customdata[:,0] != '(?)', fig_vn30.data[0].customdata[:,0]*100, '(?)')
    fig_vn30.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"
    
    plot_vn30 = fig_vn30.to_html(full_html=False)
    return render_template("/chart/analyst/treemap.html", treemap=plot,
                           plot_vn30 = plot_vn30,
                           selected_timeframe=timeframe,
                           industry_codes = dict_industry_code,
                           selected_industries = selected_industries)
# @app.route("/")
@app.route('/view_indexMonthIndustry/<type_view>', methods=['GET', 'POST'])
def viewIndexMonthIndustry(type_view = "1M"):
    
    dict_industry_code = {
        "Bán lẻ": "5300",
        "Bất động sản": "8600",
        "Dầu khí": "0500",
        "Dịch vụ tài chính": "8700",
        "Điện, nước xăng dầu khí đốt": "7500",
        "Ngân hàng": "8300",
        "Viễn thông": "6500",
        "Xây dựng và vật liệu": "2300",
        "Y tế": "4500",
        "Bảo hiểm": "8500",
        "Công nghệ thông tin": "9500",
        "Du lịch và giải trí": "5700",
        "Hàng và dịch vụ Công nghiệp": "2700",
        "Hàng cá nhân và gia dụng": "3700",
        "Hóa chất": "1300",
        "Ô tô và phụ tùng": "3300",
        "Thực phẩm và đồ uống": "3500",
        "Tài nguyên cơ bản": "1700",
        "Truyền thông": "5500"
    }
    selected_industries = ["Bán lẻ", 
                           "Bất động sản", "Dầu khí",
                           "Dịch vụ tài chính", "Điện, nước xăng dầu khí đốt",
                           "Ngân hàng"]
    if request.method == 'POST':
        selected_industries = request.form.getlist('industry')
        if (len(selected_industries) == 0):
            selected_industries = ["Bán lẻ", "Bất động sản", "Dầu khí",
                           "Dịch vụ tài chính", "Điện, nước xăng dầu khí đốt", "Ngân hàng"]
        # return selected_industries;
    
    dat_json = []
    for name_industry in selected_industries:
        dat_tmp = []
        json_tmp = indexmonthindustry(industry_code = dict_industry_code[name_industry], type_mode = type_view.upper())
        dat_tmp.append([ str(datetime.strptime(str(elm['s']), "%d/%m/%y %H:%M")) if len(elm['s']) > 8 else
                        str(datetime.strptime(str(elm['s']), "%d/%m/%y")) for elm in json_tmp['body']['data']])
        dat_tmp.append([ elm['i'] for elm in json_tmp['body']['data']])
        dat_tmp.append([ elm['v'] for elm in json_tmp['body']['data']])
        dat_tmp.append(json_tmp['header']['i'])
        if (json_tmp['header']['pct'] == None):
            return redirect(url_for('viewIndexMonthIndustry', type_view = "1M"))
        dat_tmp.append(json_tmp['header']['pct'])
        dat_tmp.append(name_industry + f" ({json_tmp['header']['pct']}%) ")
        dat_tmp.append(dict_industry_code[name_industry])
        dat_tmp.append("rgba(255, 0, 0, 1)" if json_tmp['header']['pct'] < 0 else "rgba(0, 255, 0, 1)")
        
        dat_json.append(dat_tmp)
    
    return render_template("/chart/indexindustry/lineindexindustry.html",
                           json_data = dat_json,
                           industry_codes = dict_industry_code,
                           type_view = type_view,
                           selected_industries = selected_industries)   

def indexmonthindustry(industry_code = "5300", type_mode = "1M"):
    header = {
        "Accept": "application/json",
        "Accept-Language": "vi",
        "Content-Type": "application/json",
        "Referer": "https://tcinvest.tcbs.com.vn/",
        "Sec-Ch-Ua": '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76'
    }
    if (type_mode == "1M"):
        url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/flow-industry-index?exchange=ALL&industry={industry_code}&type={type_mode}"
        response = requests.request("GET", url, headers=header).json()
        return response
    
    url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/flow-industry-index?exchange=ALL&industry={industry_code}&type={type_mode.lower()}"
    response = requests.request("GET", url, headers=header).json()
    return response

@app.route("/")
@app.route('/overview/<ticker>', methods=['GET', 'POST'])
def overview(ticker = "TCH"):
    cur = mysql.connection.cursor()
        
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.ticker = %s;
    """, (ticker,))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df_price = pd.DataFrame.from_records(records, columns=columnName)
    df_price['time_stamp'] = pd.to_datetime(df_price['time_stamp'], unit='s')
    df_price['time'] = df_price['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    df_price['year'] = df_price['time'].dt.year
    df_price['month'] = df_price['time'].dt.month
    df_price['day'] = df_price['time'].dt.day
    df_price['quarter'] = df_price['time'].dt.quarter
    df_price.groupby('year').agg({
    'open':'mean',
    'close':'mean',
    'high':'mean',
    'low':'mean',
    })
    year_df = df_price.groupby('year').agg({
                'open':'mean',
                'close':'mean',
                'high':'mean',
                'low':'mean',
            }).reset_index()

    fig_line_year = go.Figure()
    fig_line_year.add_trace(go.Scatter(x=year_df['year'], y=year_df['high'], mode='lines+markers', name='High',line=dict(color='#FCB714')))
    fig_line_year.add_trace(go.Scatter(x=year_df['year'], y=year_df['low'], mode='lines+markers', name='Low', line=dict(color='#0EB194')))
    fig_line_year.add_trace(go.Scatter(x=year_df['year'], y=year_df['close'], mode='lines+markers', name='Close', line=dict(color='#2878BD')))
    fig_line_year.add_trace(go.Scatter(x=year_df['year'], y=year_df['open'], mode='lines+markers', name='Open', line=dict(color='#70B0E0')))
    fig_line_year.add_hline(y=year_df['close'].mean(), line_width=3, line_dash="dash", line_color="green")
    fig_line_year.update_traces(textposition="bottom right")
    plot_line_year = fig_line_year.to_html(full_html=False)
    
    #-------------------------------------------------------------------------------------------------------------------------
    day_df = df_price.groupby('day').agg({
                'open':'mean',
                'close':'mean',
                'high':'mean',
                'low':'mean',
            }).reset_index()

    fig_line_day = go.Figure()
    fig_line_day.add_trace(go.Scatter(x=day_df['day'], y=day_df['high'], mode='lines+markers', name='High',line=dict(color='#FCB714')))
    fig_line_day.add_trace(go.Scatter(x=day_df['day'], y=day_df['low'], mode='lines+markers', name='Low', line=dict(color='#0EB194')))
    fig_line_day.add_trace(go.Scatter(x=day_df['day'], y=day_df['close'], mode='lines+markers', name='Close', line=dict(color='#2878BD')))
    fig_line_day.add_trace(go.Scatter(x=day_df['day'], y=day_df['open'], mode='lines+markers', name='Open', line=dict(color='#70B0E0')))
    fig_line_day.add_hline(y=day_df['close'].mean(), line_width=3, line_dash="dash", line_color="green")
    fig_line_day.update_traces(textposition="bottom right")
    plot_line_day = fig_line_day.to_html(full_html=False)

    #---------------------------------------------------------------------------------------------------------------------------
    
    quarter_df = df_price.groupby('quarter').agg({
                'open':'mean',
                'close':'mean',
                'high':'mean',
                'low':'mean',
            }).reset_index()

    fig_line_quarter = go.Figure()
    fig_line_quarter.add_trace(go.Scatter(x=quarter_df['quarter'], y=quarter_df['high'], mode='lines+markers', name='High',line=dict(color='#FCB714')))
    fig_line_quarter.add_trace(go.Scatter(x=quarter_df['quarter'], y=quarter_df['low'], mode='lines+markers', name='Low', line=dict(color='#0EB194')))
    fig_line_quarter.add_trace(go.Scatter(x=quarter_df['quarter'], y=quarter_df['close'], mode='lines+markers', name='Close', line=dict(color='#2878BD')))
    fig_line_quarter.add_trace(go.Scatter(x=quarter_df['quarter'], y=quarter_df['open'], mode='lines+markers', name='Open', line=dict(color='#70B0E0')))
    fig_line_quarter.add_hline(y=day_df['close'].mean(), line_width=3, line_dash="dash", line_color="green")
    fig_line_quarter.update_traces(textposition="bottom right")
    
    plot_line_quarter = fig_line_quarter.to_html(full_html=False)
    
    #--------------------------------------------------------------------------------------------------------------------------------
    month_df = df_price.groupby('month').agg({
                'open':'mean',
                'close':'mean',
                'high':'mean',
                'low':'mean',
            }).reset_index()

    fig_line_month = go.Figure()
    fig_line_month.add_trace(go.Scatter(x=month_df['month'], y=month_df['high'], mode='lines+markers', name='High',line=dict(color='#FCB714')))
    fig_line_month.add_trace(go.Scatter(x=month_df['month'], y=month_df['low'], mode='lines+markers', name='Low', line=dict(color='#0EB194')))
    fig_line_month.add_trace(go.Scatter(x=month_df['month'], y=month_df['close'], mode='lines+markers', name='Close', line=dict(color='#2878BD')))
    fig_line_month.add_trace(go.Scatter(x=month_df['month'], y=month_df['open'], mode='lines+markers', name='Open', line=dict(color='#70B0E0')))
    fig_line_month.add_hline(y=month_df['close'].mean(), line_width=3, line_dash="dash", line_color="green")
    fig_line_month.update_traces(textposition="bottom right")
    plot_line_month = fig_line_month.to_html(full_html=False)
    
    #---------------------------------------------------------------------------------------------------------------------------------
    
    cur.execute("""
    SELECT DISTINCT d1.time_stamp FROM d1;
    """)
    records = cur.fetchall()
    columnName = ['timestamp']
    timestamp_table = pd.DataFrame.from_records(records, columns=columnName)['timestamp'].values
    timestamp_table = np.sort(timestamp_table)
    daylyArray = timestamp_table[-2:]
    
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(daylyArray[0]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp_pr', 'open_pr', 'low_pr', 'high_pr', 'close_pr', 'volume_pr', 'sum_price_pr']
    df_price_previous = pd.DataFrame.from_records(records, columns=columnName)
    
        # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(daylyArray[1]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df_price = pd.DataFrame.from_records(records, columns=columnName)
    df_price = df_price.set_index('ticker').join(df_price_previous.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price = df_price[['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'close_pr']]
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT ct.ticker, ct.comGroupCode, ct.organName, ct.organShortName, it.industry_name 
    FROM company ct
    JOIN company_subgroup cs ON ct.ticker = cs.id_company
    JOIN group_subgroup gs ON gs.id_subgroup = cs.id_subgroup
    JOIN industry_group ig ON ig.id_group = gs.id_group
    JOIN industry it ON it.id_industry = ig.id_industry
    """)
    records = cur.fetchall()
    columnName = ['ticker', 'comGroupCode', 'organName', 'organShortName', 'industry_name']
    df = pd.DataFrame.from_records(records, columns=columnName)
    df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index().head(2)
    data_day = df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    data_day['percent'] = pd.to_numeric((data_day['close'] - data_day['close_pr'])/data_day['close_pr']) * 100
    data_day['total_price'] = ((data_day['close_pr'] + data_day['close']) * data_day['volume']) / 2000000000  
    fig_trans_values = px.pie(data_day,
             values='total_price',
             names='industry_name',
             title='Giá trị giao dịch trong ngày',
             hover_data = ['percent'],
            #  hole = 0.2
             )

    fig_trans_values.update_traces(hoverinfo='label+percent+name')
    fig_trans_values.update_traces(textposition='inside')
    fig_trans_values.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    plot_trans_values = fig_trans_values.to_html(full_html=False)

    #----------------------------------------------------------------------------------------------------------------------------------
    fig_treemap = px.treemap(data_day.sort_values(by='volume', ascending=False).head(20), path=['ticker'],
                 color='ticker',
                 hover_data=['volume','percent','organName'],
                 values='volume',
                 )
    fig_treemap.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2d} bn"
    plot_treemap = fig_treemap.to_html(full_html=False)
    
    #-----------------------------------------------------------------------------------------------------------------------------
    fig_up = px.bar(data_day.sort_values(by='percent', ascending=False).head(10).sort_values(by='percent', ascending=True),
             x="percent",
             y="ticker",
             text='percent',
             orientation='h',
             title='Tăng nhiều nhất trong ngày',
             hover_data=['organName','close'])
    fig_up.update_layout(xaxis={'categoryorder':'total descending'})
    fig_up.update_traces(texttemplate='%{text:.2s}%', textposition='outside')
    fig_up.update_traces(marker_color='#34c6bb')
    plot_his_up = fig_up.to_html(full_html=False)
    
    #------------------------------------------------------------------------------------------------------------------------------
    fig_down = px.bar(data_day.sort_values(by='percent', ascending=True).head(10).sort_values(by='percent', ascending=False),
             x="percent",
             y="ticker",
             text='percent',
             orientation='h',
             title='Giảm nhiều nhất trong ngày',
             hover_data=['organName','close'])
    fig_down.update_layout(xaxis={'categoryorder':'total descending'})
    fig_down.update_traces(texttemplate='%{text:.2s}%', textposition='outside')
    fig_down.update_traces(marker_color='#fd817e')
    plot_his_down = fig_down.to_html(full_html=False)

    #--------------------------------------------------------------------------------------------------------------------------------
    data_day_indus = data_day.groupby('industry_name').agg({
    'volume':'sum',
    'percent':'mean'
    }).reset_index()
    data_day_indus['volume'] /= 1000000
    data_day_indus['type'] = data_day_indus['percent'] > 0
    fig_volume = px.bar(data_day_indus,
             x="volume",
             y="industry_name",
             text='volume',
             orientation='h',
             title='Khối lượng giao dịch trong ngày')
    fig_volume.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_volume.update_traces(texttemplate='%{text:.2f}tr', textposition='outside')
    fig_volume.update_traces(marker_color='#34c6bb')
    plot_his_volume = fig_volume.to_html(full_html=False)
    
    #--------------------------------------------------------------------------------------------------------------------------------
    fig_percent = px.bar(data_day_indus,
             x="percent",
             y="industry_name",
             text='percent',
             orientation='h',
             color='type',
             title='% Biến động giá trong ngày')
    fig_percent.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_percent.update_traces(texttemplate='%{text:.2f}%', textposition='outside') 
    plot_his_percent = fig_percent.to_html(full_html=False)
        
    #--------------------------------------------------------------------------------------------------------------------------------
    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]
    

    return render_template("/chart/overview/overview.html", plot_line_year=plot_line_year,plot_line_day=plot_line_day, 
                           plot_line_quarter=plot_line_quarter, plot_line_month=plot_line_month,plot_trans_values = plot_trans_values,
                           plot_treemap = plot_treemap,plot_his_up = plot_his_up,plot_his_down=plot_his_down,  plot_his_volume= plot_his_volume, plot_his_percent= plot_his_percent,
                           ticker=ticker, stock_codes=stock_codes)


@app.route('/treemap_cap/<timeframe>', methods=['GET', 'POST'])
def create_treemap_cap(timeframe="daylyArray"):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT DISTINCT d1.time_stamp FROM d1;
    """)
    records = cur.fetchall()
    columnName = ['timestamp']
    timestamp_table = pd.DataFrame.from_records(records, columns=columnName)['timestamp'].values
    timestamp_table = np.sort(timestamp_table)

    if timeframe == "daylyArray":
        selected_timeframe = timestamp_table[-2:]
    elif timeframe == "weekArray":
        selected_timeframe = timestamp_table[-8:]
    elif timeframe == "monthArray":
        selected_timeframe = timestamp_table[-31:]
    else:
        return "Khung giờ không hợp lệ"
    if request.method == 'POST':
        selected_timeframe = request.form.get('timeframe')
        if selected_timeframe == "daylyArray": 
            return redirect('/treemap_cap/daylyArray')
        elif selected_timeframe == "weekArray":
            return redirect('/treemap_cap/weekArray')
        elif selected_timeframe == "monthArray":
            return redirect('/treemap_cap/monthArray')
        else:
            return "Khung giờ không hợp lệ"
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[0]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp_pr', 'open_pr', 'low_pr', 'high_pr', 'close_pr', 'volume_pr', 'sum_price_pr']
    df_price_previous = pd.DataFrame.from_records(records, columns=columnName)
    
    #target
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[-1]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df_price = pd.DataFrame.from_records(records, columns=columnName)
    df_price = df_price.set_index('ticker').join(df_price_previous.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price = df_price[['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'close_pr']]
    #append infomation
    cur.execute("""SELECT ct.ticker, ct.comGroupCode, ct.organName, ct.organShortName, it.industry_name 
    FROM company ct
    JOIN company_subgroup cs ON ct.ticker = cs.id_company
    JOIN group_subgroup gs ON gs.id_subgroup = cs.id_subgroup
    JOIN industry_group ig ON ig.id_group = gs.id_group
    JOIN industry it ON it.id_industry = ig.id_industry
    """)
    records = cur.fetchall()
    columnName = ['ticker', 'comGroupCode', 'organName', 'organShortName', 'industry_name']
    df = pd.DataFrame.from_records(records, columns=columnName)
    
    # Truy vấn dữ liệu từ SQL
    cur.execute("""
    SELECT so.ticker, so.total_max_vol
    FROM stock_out so
    WHERE so.can_use = 1
    """)
    records = cur.fetchall()
    columnName = ['ticker', 'total_max_vol']
    df_stock_out = pd.DataFrame.from_records(records, columns=columnName)
    df = df.set_index('ticker').join(df_stock_out.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    data_result = df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    data_result['percent'] = pd.to_numeric((data_result['close'] - data_result['close_pr'])/data_result['close_pr'])
    def checkTypeUpdown(x):
        if x == 0:
            return '0'
        if x < 0:
            if x <= -0.065:
                return '-2'
            return '-1'
        if x >= 0.065:
            return '2'
        return '1'
    data_result['type'] = data_result['percent'].apply(checkTypeUpdown)
    data_result['TotalMoney'] = (data_result['total_max_vol'] * 1000000 * data_result['close']) / 1000000000
    

    fig = px.treemap(data_result, path=['industry_name','ticker'],
                 color='type',
                 color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                 hover_data=['percent','organName'],
                 values='TotalMoney',
                 )
    fig.data[0].customdata[:,0] = np.where(fig.data[0].customdata[:,0] != '(?)', fig.data[0].customdata[:,0]*100, '(?)')
    fig.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"

    plot = fig.to_html(full_html=False)
    
    fig_ex = px.treemap(data_result, path=['comGroupCode','ticker'],
                 color='type',
                 color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                 hover_data=['percent','organName'],
                 values='TotalMoney',
                #  width=2000,
                #  height=1000
                 )
    fig_ex.data[0].customdata[:,0] = np.where(fig_ex.data[0].customdata[:,0] != '(?)', fig_ex.data[0].customdata[:,0]*100, '(?)')
    fig_ex.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"
    
    plot_ex = fig_ex.to_html(full_html=False)
    return render_template("/chart/analyst/treemap_cap.html", treemap=plot, plot_ex = plot_ex,selected_timeframe=timeframe)



@app.route('/treemap_values/<timeframe>', methods=['GET', 'POST'])
def create_treemap_values(timeframe="daylyArray"):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT DISTINCT d1.time_stamp FROM d1;
    """)
    records = cur.fetchall()
    columnName = ['timestamp']
    timestamp_table = pd.DataFrame.from_records(records, columns=columnName)['timestamp'].values
    timestamp_table = np.sort(timestamp_table)

    if timeframe == "daylyArray":
        selected_timeframe = timestamp_table[-2:]
    elif timeframe == "weekArray":
        selected_timeframe = timestamp_table[-8:]
    elif timeframe == "monthArray":
        selected_timeframe = timestamp_table[-31:]
    else:
        return "Khung giờ không hợp lệ"
    if request.method == 'POST':
        selected_timeframe = request.form.get('timeframe')
        if selected_timeframe == "daylyArray": 
            return redirect('/treemap_values/daylyArray')
        elif selected_timeframe == "weekArray":
            return redirect('/treemap_values/weekArray')
        elif selected_timeframe == "monthArray":
            return redirect('/treemap_values/monthArray')
        else:
            return "Khung giờ không hợp lệ"
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[0]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp_pr', 'open_pr', 'low_pr', 'high_pr', 'close_pr', 'volume_pr', 'sum_price_pr']
    df_price_previous = pd.DataFrame.from_records(records, columns=columnName)
    
    #target
    # Truy vấn dữ liệu từ SQL
    cur.execute("""SELECT * 
    FROM d1
    WHERE d1.time_stamp = %s;
    """, (int(selected_timeframe[-1]),))
    records = cur.fetchall()
    columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
    df_price = pd.DataFrame.from_records(records, columns=columnName)
    df_price = df_price.set_index('ticker').join(df_price_previous.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price = df_price[['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'close_pr']]
    #append infomation
    cur.execute("""SELECT ct.ticker, ct.comGroupCode, ct.organName, ct.organShortName, it.industry_name 
    FROM company ct
    JOIN company_subgroup cs ON ct.ticker = cs.id_company
    JOIN group_subgroup gs ON gs.id_subgroup = cs.id_subgroup
    JOIN industry_group ig ON ig.id_group = gs.id_group
    JOIN industry it ON it.id_industry = ig.id_industry
    """)
    records = cur.fetchall()
    columnName = ['ticker', 'comGroupCode', 'organName', 'organShortName', 'industry_name']
    df = pd.DataFrame.from_records(records, columns=columnName)
    
    # Truy vấn dữ liệu từ SQL
    cur.execute("""
    SELECT d1.ticker, AVG(d1.close) * SUM(d1.volume)
    FROM d1
    WHERE d1.time_stamp >= %s AND d1.time_stamp <= %s
    GROUP BY d1.ticker;
    """, (int(selected_timeframe[0]), int(selected_timeframe[-1])))

    records = cur.fetchall()
    columnName = ['ticker', 'value_trans']
    df_vol_trans = pd.DataFrame.from_records(records, columns=columnName)
    df = df.set_index('ticker').join(df_vol_trans.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    
    data_result = df_price.set_index('ticker').join(df.set_index('ticker'), on='ticker', validate='1:1').reset_index()
    data_result['percent'] = pd.to_numeric((data_result['close'] - data_result['close_pr'])/data_result['close_pr'])
    def checkTypeUpdown(x):
        if x == 0:
            return '0'
        if x < 0:
            if x <= -0.065:
                return '-2'
            return '-1'
        if x >= 0.065:
            return '2'
        return '1'
    data_result['type'] = data_result['percent'].apply(checkTypeUpdown)
    data_result['TotalMoneyTrans'] = data_result['value_trans']  / 1000000000
    
    fig = px.treemap(data_result, path=['industry_name','ticker'],
                 color='type',
                 color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                 hover_data=['percent','organName', 'TotalMoneyTrans'],
                 values='TotalMoneyTrans',
                 )
    fig.data[0].customdata[:,0] = np.where(fig.data[0].customdata[:,0] != '(?)', fig.data[0].customdata[:,0]*100, '(?)')
    fig.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"
    plot = fig.to_html(full_html=False)
    
    fig_ex = px.treemap(data_result, path=['comGroupCode','ticker'],
                 color='type',
                 color_discrete_map={'0':'#cd8e1e', '1':'#04c584', '2':'#bc6dd0', '-1':'#d0303d', '-2':'#5499d0','(?)':'#333333'},
                 hover_data=['percent','organName', 'TotalMoneyTrans'],
                 values='TotalMoneyTrans',
                #  width=2000,
                #  height=1000
                 )
    fig_ex.data[0].customdata[:,0] = np.where(fig_ex.data[0].customdata[:,0] != '(?)', fig_ex.data[0].customdata[:,0]*100, '(?)')
    fig_ex.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2f}%"
    plot_ex = fig_ex.to_html(full_html=False)
    

    return render_template("/chart/analyst/treemap_values.html", treemap=plot, plot_ex = plot_ex,selected_timeframe=timeframe)
if __name__ == "__main__":
    app.run()
