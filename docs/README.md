# Energy Consumption Analyzer

Advanced ML-powered energy consumption analysis system with anomaly detection and predictive insights.

## 🚀 Features

- **Real-time Energy Analysis**: Analyze energy consumption patterns across different room types
- **Advanced Anomaly Detection**: Multi-model ensemble approach for detecting unusual energy usage
- **Predictive Analytics**: Forecast future energy consumption with confidence intervals
- **Interactive Web Interface**: Modern, responsive frontend for data visualization
- **RESTful API**: Clean API endpoints for integration with other systems
- **Comprehensive Testing**: End-to-end validation and testing suite

## 📁 Project Structure

```
Energy Project/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── config.py                   # Centralized configuration
├── main.py                     # Main entry point
├── server.py                   # API server
├── data/                       # Energy consumption datasets
│   ├── January/
│   ├── February/
│   └── ... (all months)
├── backend/                    # ML engine and processing
│   ├── ml_engine.py           # Main ML engine
│   └── utils/                 # Utility functions
├── static/                     # Frontend files
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── tests/                      # Testing and validation
    └── validation.py
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Energy Project"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Run Full System (Recommended)
```bash
python main.py
```
Then select option 2 for API + Frontend.

### Option 2: Run ML Engine Only
```bash
python main.py
```
Then select option 1 for command-line ML engine.

### Option 3: Run API Server Directly
```bash
python server.py
```

## 📊 Usage

### Web Interface
1. Start the system using `python main.py`
2. Choose option 2 for full system
3. Open browser to `http://localhost:8000`
4. Select room type, month, and day
5. View analysis results and insights

### API Endpoints

#### Analyze Energy Data
```http
POST /api/analyze
Content-Type: application/json

{
  "bedType": "2",
  "month": "January", 
  "day": 1
}
```

#### Get Available Data
```http
GET /api/available-data
```

#### Health Check
```http
GET /api/health
```

## 🔧 Configuration

All configuration settings are centralized in `config.py`:

- **Data Directory**: `DATA_DIR` - Path to energy consumption datasets
- **API Settings**: `API_HOST`, `API_PORT` - Server configuration
- **ML Settings**: `ML_ENGINE_CONFIG` - Model parameters
- **Validation**: `VALID_BED_TYPES`, `VALID_MONTHS` - Input validation

## 🧪 Testing

Run the comprehensive validation suite:
```bash
python tests/validation.py
```

This will test:
- ML model accuracy
- Anomaly detection performance
- API functionality
- Data loading and processing
- System integration

## 📈 ML Engine Features

### Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection
- **Statistical Analysis**: Z-score and IQR-based detection
- **Ensemble Approach**: Multiple models for robust detection
- **Confidence Scoring**: Probability-based anomaly confidence

### Feature Engineering
- **Time-based Features**: Peak usage, variance, patterns
- **Statistical Features**: Mean, std, percentiles
- **Predictive Features**: Trend analysis, seasonality

### Predictive Analytics
- **Random Forest Regression**: Energy consumption prediction
- **Confidence Intervals**: Uncertainty quantification
- **Feature Importance**: Model interpretability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Run the validation tests
3. Review the configuration
4. Open an issue with detailed error information

## 🔄 Version History

- **v1.0.0**: Initial release with ML engine and web interface
- **v1.1.0**: Added comprehensive testing suite
- **v1.2.0**: Refactored architecture for better maintainability
