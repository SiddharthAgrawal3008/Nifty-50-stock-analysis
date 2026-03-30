# Nifty 50 Stock Analysis Dashboard

A comprehensive Streamlit-based dashboard for analyzing Nifty 50 stock performance with advanced visualization and rating system.

##  Features

- **Stock Performance Analysis**: Analyze historical stock data with interactive charts
- **Real-time Ratings**: Automatic stock rating based on cumulative returns and volatility
- **Interactive Visualizations**: Plotly-powered charts for better insights
- **Flexible Data Handling**: Smart column validation with multiple naming conventions support
- **Comprehensive Metrics**: Returns, volatility, risk assessment, and more

##  Stock Rating System

- 🟢 **Excellent**: Cumulative return > 15% and volatility < 25%
- 🔴 **Poor**: Cumulative return < -10% and volatility > 50%
- 🟡 **Neutral**: All other combinations

##  Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SiddharthAgrawal3008/Nifty-50-stock-analysis.git
   cd Nifty-50-stock-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

##  Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

##  Project Structure

```
Nifty-50-stock-analysis/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── NIFTY50_all.csv       # Historical stock data
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

##  Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualizations
- **scikit-learn**: Machine learning utilities
- **xgboost**: Gradient boosting framework

##  Data Format

The application expects CSV data with the following columns (case-insensitive):
- `Date` or `date`, `DATE`, `timestamp`
- `Symbol` or `symbol`, `SYMBOL`, `ticker`
- `Open` or `open`, `OPEN`, `open_price`
- `High` or `high`, `HIGH`, `high_price`
- `Low` or `low`, `LOW`, `low_price`
- `Last` or `close`, `CLOSE`, `price`, `LTP`

##  Usage

1. **Upload Data**: Use the file uploader to upload your stock data CSV
2. **Select Stocks**: Choose specific stocks or analyze all
3. **View Analysis**: Explore interactive charts and metrics
4. **Check Ratings**: Review automatic stock performance ratings

##  Customization

The application is designed to be flexible:
- Supports multiple column naming conventions
- Handles missing data gracefully
- Provides informative error messages
- Responsive design for various screen sizes

##  Technical Details

- **Framework**: Streamlit
- **Visualization**: Plotly Graph Objects & Express
- **Data Processing**: Pandas & NumPy
- **Rating Algorithm**: Custom risk-return assessment

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Author

**Siddharth Agrawal**
- GitHub: [@SiddharthAgrawal3008](https://github.com/SiddharthAgrawal3008)
- Email: siddharthagrawal804@gmail.com

##  Acknowledgments

- Nifty 50 data source and financial market insights
- Streamlit community for the amazing framework
- Plotly for interactive visualization capabilities

---

 If you find this project useful, please give it a star!
