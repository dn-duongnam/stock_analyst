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
@app.route('/cand/<timeframe>/<ticker>', methods=['GET', 'POST'])
def create_cand_chart(timeframe="d1", ticker="TCH"):
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

    cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 100", (ticker,))
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

    return render_template("/chart/cand/cand.html", plot_cand=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe, open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price, volume=volume)
@app.route("/")
@app.route("/analyst/d1/<ticker>", methods=['GET', 'POST'])
def analyst(ticker = "TCH"):
    cur = mysql.connection.cursor()
    
    # Truy vấn dữ liệu từ SQL
    cur.execute(f"SELECT * FROM d1 WHERE ticker = %s ORDER BY time_stamp DESC LIMIT 100", (ticker,))
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
                    yaxis_gridcolor='gray')  # Màu của đường kẻ ngang
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
                    yaxis_gridcolor='gray')  # Màu của đường kẻ ngang
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
                    yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ

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
                    yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ
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
                    yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ
    plot_rsi = fig_rsi.to_html(full_html=False)
    
    cur.execute("SELECT DISTINCT ticker FROM d1")
    stock_codes = [code[0] for code in cur.fetchall()]

    return render_template("/chart/analyst/analyst.html", plot_bb=plot_bb, plot_ma = plot_ma, plot_macd = plot_macd, plot_stoch = plot_stoch, plot_rsi = plot_rsi, ticker=ticker, stock_codes=stock_codes)
    

# @app.route('/cand/<timeframe>/<ticker>', methods=['GET', 'POST'])
# def create_cand_chart(timeframe="d1", ticker="TCH"):
#     cur = mysql.connection.cursor()

#     # Xác định bảng cơ sở dữ liệu dựa trên khung giờ được chọn
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

#     # Truy vấn dữ liệu từ SQL
#     cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()

#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     data = pd.DataFrame.from_records(records, columns=columnName)
#     data['time_stamp'] = pd.to_datetime(data['time_stamp'], unit='s')
#     data['time'] = data['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')

#     # Tạo danh sách các biểu đồ nến
#     fig = go.Figure(data=[go.Candlestick(x=data['time'],
#                                          open=data['open'],
#                                          high=data['high'],
#                                          low=data['low'],
#                                          close=data['close'])])

#     # Tùy chỉnh biểu đồ nếu cần
#     fig.update_layout(
#         xaxis_title='Thời gian',
#         yaxis_title='Giá',
#         plot_bgcolor='#363636',  # Màu nền của biểu đồ
#         xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#         yaxis_gridcolor='gray',  # Màu của đường kẻ ngang đồ
#         xaxis_rangeslider_visible=True
#     )

#     # Chuyển biểu đồ Plotly thành HTML
#     plot_html = fig.to_html(full_html=False)

#     # Truy vấn danh sách mã cổ phiếu
#     cur.execute("SELECT DISTINCT ticker FROM d1")
#     stock_codes = [code[0] for code in cur.fetchall()]

#     return render_template("/chart/cand/line.html", plot_cand=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe)

#-------------------------------------------------------------------------------------------------------------------------------------------
# #Line
# @app.route('/line/<timeframe>/<ticker>', methods=['GET', 'POST'])
# def create_line_chart(timeframe="d1", ticker="TCH"):
#     cur = mysql.connection.cursor()

#     # Xác định bảng cơ sở dữ liệu dựa trên khung giờ được chọn
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

#     # Truy vấn dữ liệu từ SQL
#     cur.execute(f"SELECT * FROM {table_name} WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()

#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     data = pd.DataFrame.from_records(records, columns=columnName)
#     data['time_stamp'] = pd.to_datetime(data['time_stamp'], unit='s')
#     data['time'] = data['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     fig = px.line(data, x='time', y='open', labels={'open': 'Giá Mở Cửa'})
#     fig.update_layout(title='Biểu đồ nến và Khối lượng giao dịch',
#                   plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                   xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                   yaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                   xaxis_rangeslider_visible=True)
#      # Chuyển biểu đồ Plotly thành HTML
#     plot_html = fig.to_html(full_html=False)

#     # Truy vấn danh sách mã cổ phiếu
#     cur.execute("SELECT DISTINCT ticker FROM d1")
#     stock_codes = [code[0] for code in cur.fetchall()]

#     return render_template("/chart/cand/line.html", plot_line_open=plot_html, ticker=ticker, stock_codes=stock_codes, selected_timeframe=timeframe)

#-----------------------------------------------------------------------------------------------------------------------------------

# Bollinger Bands

# @app.route('/bb/d1/<ticker>',  methods=['GET','POST'])
# def create_bb_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tính trung bình trượt 20 ngày
#     df['20_day_sma'] = df['close'].rolling(window=20).mean()

#     # Tính độ lệch chuẩn 20 ngày
#     df['20_day_std'] = df['close'].rolling(window=20).std()

#     # Tính Bollinger Bands
#     df['upper_band'] = df['20_day_sma'] + (df['20_day_std'] * 2)
#     df['lower_band'] = df['20_day_sma'] - (df['20_day_std'] * 2)

#     # Tạo biểu đồ Bollinger Bands sử dụng Plotly
#     fig = go.Figure()

#     # Hiển thị dữ liệu Giá và Bollinger Bands
#     fig.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=3)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma'], mode='lines', name='Trung bình 20 ngày',line=dict(color='#FBAC20',  dash='dot',  width=1)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['upper_band'], mode='lines', name='Dải trên Bollinger Bands', line=dict(color='#555555',  width=2)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['lower_band'],fill='tonexty', mode='lines', name='Dải dưới Bollinger Bands', line=dict(color='#555555',  width=2)))

#     # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng và ẩn các đường kẻ dọc
#     fig.update_layout(title='Bollinger Bands trên toàn bộ dữ liệu',
#                     xaxis=dict(title='Thời gian', showgrid=False),  # Ẩn đường kẻ dọc trên trục x
#                     yaxis=dict(title='Giá'),  # Ẩn đường kẻ dọc trên trục y
#                     xaxis_rangeslider_visible=True,
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray')  # Màu của đường kẻ ngang
#     # Chuyển biểu đồ Plotly thành HTML
#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/bb.html", plot=plot_html)

# #---------------------------------------------------------------------------------------------------------------------------------------

# #MA
# @app.route('/ma/d1/<ticker>',  methods=['GET','POST'])
# def create_ma_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tính trung bình trượt 5 ngày và 20 ngày
#     df['5_day_sma'] = df['close'].rolling(window=5).mean()
#     df['20_day_sma'] = df['close'].rolling(window=20).mean()

#     # Tạo biểu đồ tương tác
#     fig = go.Figure()

#     # Hiển thị dữ liệu Giá cổ phiếu và MA(5) và MA(20)
#     fig.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name='Giá đóng cửa', line=dict(color='#00F4B0', width=3)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['5_day_sma'], mode='lines', name='MA(5)', line=dict(color='#FBAC20',  dash='dot',width=2)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma'], mode='lines', name='MA(20)', line=dict(color='#64BAFF',  dash='dot', width=2)))

#     # Cài đặt thuộc tính cho biểu đồ, đặt màu nền trắng
#     fig.update_layout(title='Biểu đồ Giá cổ phiếu và MA(5) và MA(20)',
#                     xaxis=dict(title='Thời gian',  showgrid=False),
#                     yaxis=dict(title='Giá'),
#                     xaxis_rangeslider_visible=True,
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray')  # Màu của đường kẻ ngang
#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/ma5ma20.html", plot=plot_html)
# #----------------------------------------------------------------------------------------------------------------------------------

#MACD
# @app.route('/macd/d1/<ticker>',  methods=['GET','POST'])
# def create_macd_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tính đường MACD (Moving Average Convergence Divergence)
#     short_term = df['close'].ewm(span=12).mean()
#     long_term = df['close'].ewm(span=26).mean()
#     df['MACD'] = short_term - long_term

#     # Tính đường Tín hiệu (Signal Line)
#     df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

#     # Tính MACD Histogram
#     df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

#     # Tạo biểu đồ MACD sử dụng Plotly
#     fig = go.Figure()

#     # Hiển thị dữ liệu MACD và Signal Line
#     fig.add_trace(go.Scatter(x=df['time'], y=df['MACD'], mode='lines', name='MACD', line=dict(color='#FF3747', width=3)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='#64BAFF', width=3)))

#     # Tạo biểu đồ Histogram
#     fig.add_trace(go.Bar(x=df['time'], y=df['MACD_Histogram'], name='MACD Histogram', marker=dict(color='#64BAFF')))

#     # Cài đặt thuộc tính cho biểu đồ
#     fig.update_layout(title='Biểu đồ MACD',
#                     xaxis=dict(title='Thời gian', showgrid=False),
#                     yaxis=dict(title='Giá trị'),
#                     xaxis_rangeslider_visible=True,
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ

#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/macd.html", plot=plot_html)

# #-------------------------------------------------------------------------------------------------------------------------------
# STOCH(14,3)
# @app.route('/stoch/d1/<ticker>',  methods=['GET','POST'])
# def create_stoch_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tính %K và %D
#     period = 14  # Kỳ giao dịch
#     smooth = 3   # Độ trơn
#     df['low_min'] = df['low'].rolling(window=period).min()
#     df['high_max'] = df['high'].rolling(window=period).max()
#     df['%K'] = 100 * (df['close'] - df['low_min']) / (df['high_max'] - df['low_min'])
#     df['%D'] = df['%K'].rolling(window=smooth).mean()

#     # Tạo biểu đồ Stochastic Oscillator sử dụng Plotly
#     fig = go.Figure()

#     # Hiển thị dữ liệu %K và %D
#     fig.add_trace(go.Scatter(x=df['time'], y=df['%K'], mode='lines', name='%K (màu xanh)', line=dict(color='#64BAFF', width=3)))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['%D'], mode='lines', name='%D (màu đỏ)', line=dict(color='#FF3747', width=3)))

#     # Vẽ đường giới hạn 20 và 80
#     fig.add_shape(
#         go.layout.Shape(
#             type="line",
#             x0=df['time'].min(),
#             x1=df['time'].max(),
#             y0=20,
#             y1=20,
#             line=dict(color="white", dash="dash", width = 2),
#         )
#     )
#     fig.add_shape(
#         go.layout.Shape(
#             type="line",
#             x0=df['time'].min(),
#             x1=df['time'].max(),
#             y0=80,
#             y1=80,
#             line=dict(color="white", dash="dash", width = 3),
#         )
#     )
#     # Cài đặt thuộc tính cho biểu đồ
#     fig.update_layout(title='Stochastic Oscillator trên toàn bộ dữ liệu',
#                     xaxis=dict(title='Thời gian', showgrid=False),
#                     yaxis=dict(title='%'),
#                     xaxis_rangeslider_visible=True,
#                     yaxis_range=[0, 100],
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ
#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/stoch.html", plot=plot_html)

# #----------------------------------------------------------------------------------------------------------------------------------
#RSI(14)
# @app.route('/rsi/d1/<ticker>',  methods=['GET','POST'])
# def create_rsi_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tính chỉ số RSI(14)
#     delta = df['close'].diff(1)
#     gain = delta.where(delta > 0, 0)
#     loss = -delta.where(delta < 0, 0)

#     avg_gain = gain.rolling(window=14).mean()
#     avg_loss = loss.rolling(window=14).mean()

#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#     print(rsi.head(20))

#     # Tạo biểu đồ RSI(14) với đường giới hạn 30 và 70
#     fig = go.Figure()

#     # Hiển thị dữ liệu RSI(14)
#     fig.add_trace(go.Scatter(x=df['time'], y=rsi, mode='lines', name='RSI(14)', line=dict(color='#FBAC20', width = 3)))

#     # Thêm đường giới hạn 30 và 70
#     fig.add_shape(
#         go.layout.Shape(
#             type="line",
#             x0=df['time'].min(),
#             x1=df['time'].max(),
#             y0=30,
#             y1=30,
#             line=dict(color="white", dash="dash", width = 2),
#         )
#     )
#     fig.add_shape(
#         go.layout.Shape(
#             type="line",
#             x0=df['time'].min(),
#             x1=df['time'].max(),
#             y0=70,
#             y1=70,
#             line=dict(color="white", dash="dash", width = 2),
#         )
#     )

#     # Đặt các thuộc tính cho biểu đồ
#     fig.update_layout(title='RSI(14) với Đường Giới Hạn 30 và 70',
#                     xaxis=dict(title='Thời gian', showgrid=False),
#                     yaxis=dict(title='RSI'),
#                     xaxis_rangeslider_visible=True,
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     paper_bgcolor='white',  # Màu nền của toàn bộ khung biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray')  # Màu của đường kẻ ngang đồ
#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/rsi14.html", plot=plot_html)
# #-----------------------------------------------------------------------------------------------------------------------------------
# #Nến + KLGD
# @app.route('/cand_volume/d1/<ticker>',  methods=['GET','POST'])
# def create_cand_volume_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
    
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
#     # Tạo subplot cho biểu đồ nến và histogram
#     fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

#     # Tạo danh sách màu cho biểu đồ histogram
#     colors = ['green' if close > open else 'red' for open, close in zip(df['open'], df['close'])]

#     # Biểu đồ nến
#     candlestick = go.Candlestick(x=df['time'],
#                     open=df['open'],
#                     high=df['high'],
#                     low=df['low'],
#                     close=df['close'])
#     fig.add_trace(candlestick, row=1, col=1)

#     # Biểu đồ histogram khối lượng giao dịch với màu tùy theo giá đóng cửa
#     bar = go.Bar(x=df['time'], y=df['volume'], marker_color=colors)
#     fig.add_trace(bar, row=2, col=1)

#     # Tùy chỉnh biểu đồ nến
#     fig.update_xaxes(title_text="Thời gian", row=2, col=1)
#     fig.update_yaxes(title_text="Giá", row=1, col=1)

#     # Tùy chỉnh trục y cho biểu đồ histogram
#     fig.update_xaxes(title_text="Thời gian", row=1, col=1)
#     fig.update_yaxes(title_text="Khối lượng giao dịch", secondary_y=True, row=2, col=1)

#     # Hiển thị biểu đồ
#     fig.update_layout(title='Biểu đồ nến và Khối lượng giao dịch',
#                     plot_bgcolor='#363636',  # Màu nền của biểu đồ
#                     xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     yaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#                     xaxis_rangeslider_visible=True)
#     # Chuyển biểu đồ Plotly thành HTML
#     plot_html = fig.to_html(full_html=False)

#     return render_template("/chart/d1/cand_volume.html", plot=plot_html)

# #-----------------------------------------------------------------------------------------------------------------------------------
# # Nến + BB
# @app.route('/cand_bb/d1/<ticker>',  methods=['GET','POST'])
# def create_cand_bb_d1(ticker = "TCB"):
#     cur = mysql.connection.cursor()
    
#     # Truy vấn dữ liệu từ SQL
#     cur.execute("SELECT * FROM d1 WHERE ticker = %s", (ticker,))
#     records = cur.fetchall()
    
#     columnName = ['ticker', 'time_stamp', 'open', 'low', 'high', 'close', 'volume', 'sum_price']
#     df = pd.DataFrame.from_records(records, columns=columnName)
#     df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')
#     df['time'] = df['time_stamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    
#     # Tạo biểu đồ nến sử dụng Plotly
#     fig = go.Figure(data=[go.Candlestick(x=df['time'],
#                     open=df['open'],
#                     high=df['high'],
#                     low=df['low'],
#                     close=df['close'])])

#     # Tính dải Bollinger Bands
#     df['20_day_sma'] = df['close'].rolling(window=20).mean()
#     df['20_day_std'] = df['close'].rolling(window=20).std()
#     df['upper_band'] = df['20_day_sma'] + (df['20_day_std'] * 2)
#     df['lower_band'] = df['20_day_sma'] - (df['20_day_std'] * 2)

#     # Tạo biểu đồ dải Bollinger Bands
#     fig.add_trace(go.Scatter(x=df['time'], y=df['20_day_sma'], mode='lines', name='Trung bình 20 ngày', line=dict(color='#FF3747')))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['upper_band'], mode='lines', name='Dải trên Bollinger Bands', line=dict(color='#64BAFF')))
#     fig.add_trace(go.Scatter(x=df['time'], y=df['lower_band'], fill='tonexty', name='Dải dưới Bollinger Bands', line=dict(color='#64BAFF'), fillcolor='rgba(40, 60, 52, 0.4)'))


#     # Tùy chỉnh biểu đồ nến
#     fig.update_layout(
#         title='Biểu đồ nến và Bollinger Bands',
#         xaxis_title='Thời gian',
#         yaxis_title='Giá',
#         plot_bgcolor='#363636',  # Màu nền của biểu đồ
#         xaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#         yaxis_gridcolor='gray',  # Màu của đường kẻ ngang
#         xaxis_rangeslider_visible=True
#     )
#     plot_html = fig.to_html(full_html=False)

    return render_template("/chart/d1/cand_bb.html", plot=plot_html)
if __name__ == "__main__":
    app.run()
