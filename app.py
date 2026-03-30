import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- Stock Rating Function ---
def get_stock_rating(cum_return: float, volatility: float) -> str:
    if cum_return > 0.15 and volatility < 0.25:
        return "🟢 Excellent"
    elif cum_return < -0.10 and volatility > 0.5:
        return "🔴 Poor"
    else:
        return "🟡 Neutral"

st.set_page_config(page_title="Nifty 50 Stock Analysis ", layout="wide")

def validate_columns(df):
    """Validate and rename columns, making all columns optional with graceful fallbacks"""
    # Column mapping with alternatives
    column_mapping = {
        'Date': ['date', 'DATE', 'DATE_TIME', 'date_time', 'timestamp', 'TIMESTAMP', 'time', 'TIME'],
        'Symbol': ['symbol', 'SYMBOL', 'stock', 'STOCK', 'code', 'CODE', 'ticker', 'TICKER'],
        'Open': ['open', 'OPEN', 'open_price', 'OPEN_PRICE', 'opening_price', 'OPENING_PRICE'],
        'High': ['high', 'HIGH', 'high_price', 'HIGH_PRICE', 'highest_price', 'HIGHEST_PRICE'],
        'Low': ['low', 'LOW', 'low_price', 'LOW_PRICE', 'lowest_price', 'LOWEST_PRICE'],
        'Last': ['close', 'CLOSE', 'last_traded_price', 'LAST_TRADED_PRICE', 'closing_price', 'CLOSING_PRICE', 
                'last_price', 'LAST_PRICE', 'price', 'PRICE', 'LTP']
    }

    # Try to find alternative column names and rename them
    column_replacements = {}
    found_columns = []
    for col, alternatives in column_mapping.items():
        if col in df.columns:
            found_columns.append(col)
            continue
            
        for alt in alternatives:
            if alt in df.columns:
                column_replacements[col] = alt
                found_columns.append(col)
                break

    # Rename columns if we found alternatives
    if column_replacements:
        df = df.rename(columns=column_replacements)
        st.info(f"Found alternative column names: {', '.join([f'{old} -> {new}' for old, new in column_replacements.items()])}")

    # Check which columns we found
    missing_columns = [col for col in column_mapping.keys() if col not in found_columns]
    
    if missing_columns:
        st.info(f"Note: The following columns are missing but the app will still work: {', '.join(missing_columns)}")
        st.info("The app will adapt to show only available data.")
        
        # For each missing column, suggest alternatives
        for col in missing_columns:
            st.info(f"If you have a column for {col}, try renaming it to one of these: {', '.join(column_mapping[col])}")
    
    # Add default values for missing columns
    for col in missing_columns:
        if col == 'Date':
            df[col] = pd.to_datetime(df.index if df.index.name else range(len(df)))
        elif col == 'Symbol':
            df[col] = 'Unknown'
        elif col in ['Open', 'High', 'Low', 'LTP']:
            df[col] = np.nan

    return df  # Return the modified dataframe with renamed columns and defaults for missing columns

def create_scatter_plot(df, x_col, y_col, title, yaxis_title, color='blue', height=400):
    """Create a scatter plot with Plotly"""
    fig = go.Figure(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            line=dict(color=color)
        )
    )
    fig.update_layout(
        title=title,
        yaxis_title=yaxis_title,
        xaxis_title='Date',
        height=height
    )
    st.plotly_chart(fig, use_container_width=True)

def create_bar_chart(df, x_col, y_col, title, yaxis_title, color='green', height=400):
    """Create a bar chart with Plotly"""
    fig = go.Figure(
        go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color=color
        )
    )
    fig.update_layout(
        title=title,
        yaxis_title=yaxis_title,
        xaxis_title='Date',
        height=height
    )
    st.plotly_chart(fig, use_container_width=True)

def create_histogram(df, x_col, title, nbins=50, color='orange', height=400):
    """Create a histogram with Plotly Express"""
    fig = px.histogram(
        df,
        x=x_col,
        nbins=nbins,
        color_discrete_sequence=[color]
    )
    fig.update_layout(
        title=title,
        height=height
    )
    st.plotly_chart(fig, use_container_width=True)

def create_heatmap(corr_df, title, height=600, width=800):
    """Create a heatmap for correlation matrix"""
    fig = go.Figure(
        go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale='coolwarm',
            zmin=-1,
            zmax=1,
            text=corr_df.values,
            hovertemplate='Symbol 1: %{y}<br>Symbol 2: %{x}<br>Correlation: %{text:.2f}'
        )
    )
    fig.update_layout(
        title=title,
        height=height,
        width=width
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("Nifty 50 Stock Analysis")
    st.markdown("""
    This Web-App provides comprehensive analysis of NIFTY 50 stocks, 
    including Price analysis, OHLC Candlestick Chart, and Performance metrics.
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Upload NIFTY 50 CSV File", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = validate_columns(df)
            
            # Add a symbol selector
            symbols = ['All'] + sorted(df['Symbol'].unique())
            symbol = st.sidebar.selectbox("Select Symbol", symbols)
            
            # Filter by symbol
            if symbol == 'All':
                filtered_df = df
            else:
                filtered_df = df[df['Symbol'] == symbol]

            # Detect price column first
            price_columns = ['Last', 'LTP']
            price_col = None
            for col in price_columns:
                if col in filtered_df.columns:
                    price_col = col
                    break
            
            if price_col is None:
                st.error("No price column (Last or LTP) found in the data. Please make sure your CSV file has a price column.")
                return

            # Add date range selector
            if 'Date' in filtered_df.columns:
                # Convert Date column to datetime if it's not already
                filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
                
                date_range = st.sidebar.date_input(
                    "Select Date Range",
                    value=(filtered_df['Date'].min().date(), filtered_df['Date'].max().date()),
                    min_value=filtered_df['Date'].min().date(),
                    max_value=filtered_df['Date'].max().date()
                )
                
                # Convert date inputs to datetime
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                
                # Filter once at the beginning and use this filtered_df throughout
                filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & 
                                       (filtered_df['Date'] <= end_date)]
                
                # Sort by date
                filtered_df = filtered_df.sort_values('Date')

                # Display date range info
                if not filtered_df.empty:
                    st.info(f"Date range in data: {filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}")

                # Create a copy of the filtered dataframe for analysis
                analysis_df = filtered_df.copy()

                # Drop rows with missing price data
                analysis_df = analysis_df.dropna(subset=[price_col, 'Open', 'High', 'Low'])

                # Calculate metrics only on filtered data
                analysis_df['Daily Return'] = analysis_df[price_col].pct_change()
                analysis_df['Cumulative Return'] = (1 + analysis_df['Daily Return']).cumprod() - 1
                analysis_df['Volatility 14D'] = analysis_df['Daily Return'].rolling(window=14).std() * np.sqrt(252)
            
            if 'Daily Return' in filtered_df.columns:
                filtered_df['Volatility 14D'] = filtered_df['Daily Return'].rolling(window=14).std() * np.sqrt(252)

            # Display date range info
            if not filtered_df.empty:
                st.info(f"Date range in data: {filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}")

            # --- Data Preview ---
            st.subheader("Data Preview")
            st.dataframe(filtered_df.head(50))

            # --- Export Options ---
            st.subheader("Export Options")
            st.download_button("Download Filtered CSV", filtered_df.to_csv(index=False), "filtered_data.csv")


            # Add missing columns
            price_columns = ['Last', 'LTP']
            price_col = None
            for col in price_columns:
                if col in filtered_df.columns:
                    price_col = col
                    break
            
            if price_col is None:
                st.error("No price column (Last or LTP) found in the data. Please make sure your CSV file has a price column.")
                return

            # Convert numeric columns to appropriate types
            numeric_cols = ['Open', 'High', 'Low', price_col, 'Chng', '% Chng', 'Volume (lacs)', 'Turnover (crs.)']
            for col in numeric_cols:
                if col in filtered_df.columns:
                    try:
                        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
                    except Exception as e:
                        st.warning(f"Warning: Could not convert column {col} to numeric: {str(e)}")

            # Add missing columns
            if 'Chng' not in filtered_df.columns:
                filtered_df['Chng'] = filtered_df[price_col].diff()
            if '% Chng' not in filtered_df.columns:
                filtered_df['% Chng'] = filtered_df['Chng'] / filtered_df[price_col].shift(1) * 100

            # Add Daily Return for price analysis
            filtered_df['Daily Return'] = filtered_df[price_col].pct_change()
            # Ensure Volatility 14D is present for later use
            if 'Daily Return' in filtered_df.columns:
                filtered_df['Volatility 14D'] = filtered_df['Daily Return'].rolling(window=14).std() * np.sqrt(252)

            # Handle NaN values
            filtered_df = filtered_df.dropna(subset=[price_col, 'Open', 'High', 'Low'])

            # --- OHLC Candlestick Chart ---
            if symbol != 'All':
                st.subheader("OHLC Candlestick Chart")
                if not analysis_df.empty:
                    fig = go.Figure(data=[
                        go.Candlestick(
                            x=analysis_df['Date'],
                            open=analysis_df['Open'],
                            high=analysis_df['High'],
                            low=analysis_df['Low'],
                            close=analysis_df[price_col],
                            name=symbol
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"OHLC Chart for {symbol}",
                        yaxis_title='Price',
                        xaxis_title='Date',
                        height=600
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No OHLC data available for the selected symbol.")
            else:
                st.info("Select a single symbol to view the OHLC candlestick chart.")

            # --- Price Analysis ---
            if not analysis_df.empty:
                st.subheader("Price Analysis")

                # --- Stock Rating ---
                # Get the latest cumulative return and volatility
                final_cum_return = analysis_df['Cumulative Return'].iloc[-1] if not analysis_df['Cumulative Return'].isnull().all() else None
                final_volatility = analysis_df['Volatility 14D'].iloc[-1] if not analysis_df['Volatility 14D'].isnull().all() else None
                if final_cum_return is not None and final_volatility is not None:
                    rating = get_stock_rating(final_cum_return, final_volatility)
                    if "Excellent" in rating:
                        st.success(f"⭐ Performance Rating: {rating}")
                    elif "Neutral" in rating:
                        st.warning(f"⚠️ Performance Rating: {rating}")
                    elif "Poor" in rating:
                        st.error(f"🚨 Performance Rating: {rating}")
                    st.markdown("ℹ️ **Rating Logic:** Excellent = return > 15% & volatility < 0.25, Poor = return < -10% & volatility > 0.5, else Neutral.")
                else:
                    st.info("Not enough data to compute stock rating.")

                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    if not analysis_df['Cumulative Return'].isnull().all():
                        # Create and display chart
                        fig_cum = go.Figure(
                            go.Scatter(
                                x=analysis_df['Date'],
                                y=analysis_df['Cumulative Return'],
                                line=dict(color='blue')
                            )
                        )
                        fig_cum.update_layout(
                            title="Cumulative Return",
                            yaxis_title="Cumulative Return",
                            xaxis_title='Date',
                            height=300
                        )
                        st.plotly_chart(fig_cum, use_container_width=True)
                        # Chart Export Buttons
                        png_bytes = fig_cum.to_image(format="png")
                        svg_bytes = fig_cum.to_image(format="svg")
                        st.download_button("Download Cumulative Return (PNG)", png_bytes, file_name="cumulative_return.png")
                        st.download_button("Download Cumulative Return (SVG)", svg_bytes, file_name="cumulative_return.svg")
                    else:
                        st.info("Not enough data for cumulative return chart.")
                
                with col2:
                    if not analysis_df['Volatility 14D'].isnull().all():
                        # Create and display chart
                        fig_vol = go.Figure(
                            go.Scatter(
                                x=analysis_df['Date'],
                                y=analysis_df['Volatility 14D'],
                                line=dict(color='red')
                            )
                        )
                        fig_vol.update_layout(
                            title="Volatility (14D)",
                            yaxis_title="Volatility (14D)",
                            xaxis_title='Date',
                            height=300
                        )
                        st.plotly_chart(fig_vol, use_container_width=True)
                        # Chart Export Buttons
                        png_bytes = fig_vol.to_image(format="png")
                        svg_bytes = fig_vol.to_image(format="svg")
                        st.download_button("Download Volatility 14D (PNG)", png_bytes, file_name="volatility_14d.png")
                        st.download_button("Download Volatility 14D (SVG)", svg_bytes, file_name="volatility_14d.svg")
                    else:
                        st.info("Not enough data for volatility chart.")

            # --- Daily % Change Bar Chart ---
            st.subheader("Daily % Change Bar Chart")
            if not analysis_df['Daily Return'].isnull().all():
                fig_bar = go.Figure(
                    go.Bar(
                        x=analysis_df['Date'],
                        y=analysis_df['Daily Return'],
                        marker_color=np.where(analysis_df['Daily Return']>0, 'green', 'red')
                    )
                )
                fig_bar.update_layout(
                    title="Daily % Change",
                    yaxis_title="% Change",
                    xaxis_title='Date',
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                # Chart Export Buttons
                png_bytes = fig_bar.to_image(format="png")
                svg_bytes = fig_bar.to_image(format="svg")
                st.download_button("Download Daily % Change (PNG)", png_bytes, file_name="daily_change.png")
                st.download_button("Download Daily % Change (SVG)", svg_bytes, file_name="daily_change.svg")
            else:
                st.info("No daily return data available for this selection.")

            # --- Volume Analysis ---
            if 'Volume (lacs)' in filtered_df.columns:
                # Convert volume to numeric
                filtered_df['Volume (lacs)'] = pd.to_numeric(filtered_df['Volume (lacs)'], errors='coerce')
                st.subheader("Volume Analysis")
                create_scatter_plot(
                    filtered_df, 'Date', 'Volume (lacs)',
                    "Volume Analysis", "Volume (lacs)",
                    color='blue', height=400
                )
            else:
                st.info("No volume data available.")

            # --- Turnover Analysis ---
            if 'Turnover (crs.)' in filtered_df.columns:
                # Convert turnover to numeric
                filtered_df['Turnover (crs.)'] = pd.to_numeric(filtered_df['Turnover (crs.)'], errors='coerce')
                st.subheader("Turnover Analysis")
                create_scatter_plot(
                    filtered_df, 'Date', 'Turnover (crs.)',
                    "Turnover Analysis", "Turnover (crs.)",
                    color='purple', height=400
                )
            else:
                st.info("No turnover data available.")

            # --- Price Distribution ---
            st.subheader("Price Distribution")
            if not filtered_df['Last'].isnull().all():
                create_histogram(
                    filtered_df, 'Last',
                    "Price Distribution", nbins=50,
                    color='orange', height=400
                )
            else:
                st.info("No price data available for distribution.")

            # --- Performance Metrics ---
            st.subheader("Performance Metrics")
            if '365 d % chng' in filtered_df.columns and '30 d % chng' in filtered_df.columns:
                st.write("**365 Day % Change:**", filtered_df['365 d % chng'].iloc[-1])
                st.write("**30 Day % Change:**", filtered_df['30 d % chng'].iloc[-1])

            # --- Top Gainers/Losers Table ---
            if 'Chng' in filtered_df.columns:
                st.subheader("Top Gainers & Losers")
                day_changes = filtered_df[['Date', 'Symbol', 'Chng']].dropna()
                if not day_changes.empty:
                    top_gains = day_changes.sort_values('Chng', ascending=False).head(5)
                    top_losses = day_changes.sort_values('Chng').head(5)
                    st.write("**Top 5 Gainers:**")
                    st.dataframe(top_gains)
                    st.write("**Top 5 Losers:**")
                    st.dataframe(top_losses)
                else:
                    st.info("No change data available for gainers/losers table.")

            # --- 52 Week High/Low ---
            if '52w H' in filtered_df.columns and '52w L' in filtered_df.columns:
                st.subheader("52 Week High/Low")
                if not filtered_df['Cumulative Return'].isnull().all():
                    fig = go.Figure(
                        go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Cumulative Return'],
                            line=dict(color='blue')
                        )
                    )
                    fig.update_layout(
                        yaxis_title='Cumulative Return',
                        xaxis_title='Date',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for cumulative return chart.")
            
            # Volatility Chart
            with col2:
                if not filtered_df['Volatility 14D'].isnull().all():
                    fig = go.Figure(
                        go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Volatility 14D'],
                            line=dict(color='red')
                        )
                    )
                    fig.update_layout(
                        yaxis_title='Volatility (14D)',
                        xaxis_title='Date',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for volatility chart.")

            # --- Correlation Matrix ---
            if symbol == 'All' and 'Symbol' in df.columns and 'Last' in df.columns and not df.empty:
                st.subheader("Correlation Matrix (Last)")
                pivot = df.pivot_table(index='Date', columns='Symbol', values='Last')
                corr = pivot.corr()
                
                if not corr.empty:
                    create_heatmap(corr, "Correlation Matrix")
                else:
                    st.info("Not enough data for correlation matrix.")

            # --- XGBoost Forecast Section ---
            with st.expander("XGBoost Price Forecast "):
                st.markdown("""
                This section uses XGBoost to forecast the next N days of prices for the selected symbol, based on historical data and engineered features. Use for educational purposes only.
                """)
                # Always show the expander, but check requirements and show warnings if not met
                requirements_met = True
                feat_df = None
                if symbol == 'All':
                    st.warning("Please select a single symbol (not 'All') to use XGBoost forecasting.")
                    requirements_met = False
                elif analysis_df.empty:
                    st.warning("No data available for the selected symbol.")
                    requirements_met = False
                else:
                    # Prepare features and check length
                    try:
                        def prepare_features(df, price_col='Last', lags=7):
                            df = df[['Date', price_col]].copy()
                            df = df.dropna()
                            df['Date'] = pd.to_datetime(df['Date'])
                            df = df.set_index('Date')
                            for i in range(1, lags + 1):
                                df[f'lag_{i}'] = df[price_col].shift(i)
                            df['rolling_mean'] = df[price_col].rolling(window=5).mean()
                            df['rolling_std'] = df[price_col].rolling(window=5).std()
                            df = df.dropna()
                            return df
                        lags = 7
                        feat_df = prepare_features(analysis_df, price_col=price_col, lags=lags)

                        if len(feat_df) < 30:
                            st.warning("Not enough data for XGBoost training. Need at least 30 rows after feature engineering.")
                            requirements_met = False
                    except Exception as ex:
                        st.warning(f"Feature engineering error: {ex}")
                        requirements_met = False
                if requirements_met:
                    from sklearn.model_selection import train_test_split
                    def split_data(df, target_col='Last'):
                        X = df.drop(columns=[target_col])
                        y = df[target_col]
                        return train_test_split(X, y, test_size=0.2, shuffle=False)
                    from xgboost import XGBRegressor
                    def train_model(X_train, y_train):
                        model = XGBRegressor(n_estimators=100, learning_rate=0.1)
                        model.fit(X_train, y_train)
                        return model
                    def predict_next_days(df, model, days=5, lags=7):
                        predictions = []
                        last_row = df.iloc[-1:].copy()
                        for _ in range(days):
                            input_features = last_row.drop(columns=['Last'])
                            next_price = model.predict(input_features)[0]
                            predictions.append(next_price)
                            # Shift lags for next prediction (avoid lag_0)
                            for i in range(lags, 1, -1):
                                last_row[f'lag_{i}'] = last_row[f'lag_{i-1}']
                            last_row['lag_1'] = next_price
                            last_row['rolling_mean'] = np.mean([last_row[f'lag_{i}'].values[0] for i in range(1, 6)])
                            last_row['rolling_std'] = np.std([last_row[f'lag_{i}'].values[0] for i in range(1, 6)])
                        return predictions
                    def show_xgboost_forecast(df, predictions, symbol='Stock'):
                        future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=len(predictions), freq='D')
                        forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted Price': predictions})
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index, y=df['Last'], name='Historical', line=dict(color='blue')))
                        fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Predicted Price'], name='Forecast', line=dict(color='red')))
                        fig.update_layout(title=f"XGBoost Forecast for {symbol}", xaxis_title="Date", yaxis_title="Price")
                        st.plotly_chart(fig, use_container_width=True)
                    try:
                        X_train, X_test, y_train, y_test = split_data(feat_df, target_col=price_col)
                        model = train_model(X_train, y_train)
                        preds = model.predict(X_test)
                        test_score = np.sqrt(np.mean((preds - y_test) ** 2))
                        st.info(f"Test RMSE: {test_score:.3f}")
                        days_to_predict = st.slider("Forecast Horizon (days)", min_value=1, max_value=15, value=5)
                        future_preds = predict_next_days(feat_df, model, days=days_to_predict, lags=lags)
                        show_xgboost_forecast(feat_df, future_preds, symbol=symbol)
                    except Exception as ex:
                        st.warning(f"XGBoost forecast error: {ex}")



        except Exception as e:
            st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
