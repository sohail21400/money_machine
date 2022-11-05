import streamlit as st
import pandas as pd
import datetime as dt
import yfinance as yf
import mplfinance as mpf

@st.experimental_memo(persist='disk')
def download_data(interval, symbol, start_date, end_date):
    with st.spinner('Donloading data...'):
        # downloading date from yfinance
        if interval == 'Intraday':
            data = yf.download(tickers=symbol, start=start_date, end=end_date, interval="5m")
        elif interval == 'Daily':
            data = yf.download(tickers=symbol, start=start_date, end=end_date)

        print(f"Date downloaded from yfinance")
        data = data.rename(columns = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj close', 'Volume': 'volume'})
        st.write(data)
        for i in data.columns:
            data[i] = data[i].astype(float)
            data.index = pd.to_datetime(data.index)
        st.write(f"Number of candles downloaded: {data.size}")
        st.balloons()
        return data

@st.experimental_memo()
def get_data(interval, symbol, start_date, end_date):
    data = download_data(interval, symbol, start_date, end_date)
    return data


st.title("Historical Data Downloader")
st.write("This app downloads historical data from Yahoo Finance")

# Select the stock symbol
symbol = st.text_input('Symbol:', 'RELIANCE.NS').upper()
st.write(f'Selected Stock: **{symbol}**')

# Select the interval type, daily or intraday
interval_values = ['Intraday', 'Daily']
interval = st.selectbox(label="Interval", 
            index=interval_values.index('Intraday'),
            options=interval_values,
            label_visibility='visible')




default_end_date = dt.date.today()
default_start_date = dt.date.today() - dt.timedelta(days=59)


if interval == 'Daily':
    # we can get the past 20 years of daily data
    # setting default start date to 1 year ago
    default_start_date = dt.date.today() - dt.timedelta(days=364)
    
elif interval == 'Intraday':
    # we can only get a maximum of past 60 days of intraday data
    # setting default start date to 60 days ago
    default_start_date = dt.date.today() - dt.timedelta(days=59)

# Select the start date and end date
col1, col2 = st.columns(2)

start_date = col1.date_input('Start Date', default_start_date)
end_date = col2.date_input('End Date', default_end_date)

if interval == 'Intraday':
    # if the start date is more than 60 days ago, set it to 60 days ago
    if start_date < dt.datetime.today().date() - dt.timedelta(59):
        st.error('Only maximum of past 60 days data can be downloaded', icon="🚨")
        start_date = dt.datetime.today() - dt.timedelta(59)
        temp = start_date.strftime('%Y/%m/%d')
        st.info(f'Setting the start date as: {temp}', icon="ℹ️")

# download button
download_button_clicked = st.button(label='Download', key="download")

if download_button_clicked:
    data = get_data(interval=interval, symbol=symbol, start_date=start_date, end_date=end_date)

    # NOTE: I tried to download the dataframe as a csv file. But it's not working
    # I think it is an issue with the state management. The page is getting refreshed. And I guess the data is lost before saving
    # if st.button(label="Download as CSV", key="download_csv"):
    #     data = download_and_cache_df(interval=interval, symbol=symbol, start=start_date, end=end_date)
    #     data.to_csv(f"{symbol}-{start_date.date()}-to-{end_date.date()}.csv")
    #     # st.info(f"Downloaded {symbol}-{start_date.date()}-to-{end_date.date()}.csv", icon="ℹ️")
    #     st.info(f"Downloaded.csv", icon="ℹ️")


    # PLOTING THE DATA
    st.title('mplfinance demo')

    # with st.sidebar.form('settings_form'):
    with st.form('settings_from'):
        show_nontrading_days = st.checkbox('Show non-trading days', True)
        # https://github.com/matplotlib/mplfinance/blob/master/examples/styles.ipynb
        chart_styles = [
            'default', 'binance', 'blueskies', 'brasil', 
            'charles', 'checkers', 'classic', 'yahoo',
            'mike', 'nightclouds', 'sas', 'starsandstripes'
        ]
        chart_style = st.selectbox('Chart style', options=chart_styles, index=chart_styles.index('starsandstripes'))
        chart_types = [
            'candle', 'ohlc', 'line', 'renko', 'pnf'
        ]
        chart_type = st.selectbox('Chart type', options=chart_types, index=chart_types.index('candle'))

        mav1 = st.number_input('Mav 1', min_value=3, max_value=30, value=3, step=1)
        mav2 = st.number_input('Mav 2', min_value=3, max_value=30, value=6, step=1)
        mav3 = st.number_input('Mav 3', min_value=3, max_value=30, value=9, step=1)

        st.form_submit_button('Apply')

    

    fig, ax = mpf.plot(
        data,
        title=f'{symbol}, {start_date}',
        type=chart_type,
        show_nontrading=show_nontrading_days,
        mav=(int(mav1),int(mav2),int(mav3)),
        volume=True,

        style=chart_style,
        figsize=(15,10),
        
        # Need this setting for Streamlit, see source code (line 778) here:
        # https://github.com/matplotlib/mplfinance/blob/master/src/mplfinance/plotting.py
        returnfig=True
    )

    st.pyplot(fig)







print("--------------------RESTARTED---------------------\n")


