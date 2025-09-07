# Quick Start Guide - Enhanced Energy Consumption Analyzer

## 🚀 **Get Started in 10 Minutes**

This guide will help you set up and run the enhanced energy consumption analyzer with deep learning capabilities and modern UI.

## 📋 **Prerequisites**

- Python 3.12+
- Node.js 18+
- Docker (optional, for database)
- Git

## ⚡ **Quick Setup**

### **1. Install Dependencies**

```bash
# Install Python dependencies
pip install -r requirements.txt

# For GPU support (optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **2. Test the Enhanced ML Engine**

```bash
# Run the enhanced ML engine
python enhanced_ml_engine.py
```

**Expected Output:**
```
🚀 Enhanced ML Engine initialized on cpu
Enter bed type (2, 4, 6): 2
Enter month (e.g., January): April
Enter day: 1
📊 Loading data...
🔧 Engineering features...
🧠 Training Deep Learning Models...
📊 Training LSTM Anomaly Detector...
🔍 Training Autoencoder...
⚡ Training Transformer...
✅ Deep Learning Models Training Complete!
🚨 Detecting anomalies...
💡 Generating insights...
```

### **3. Test the Enhanced Frontend**

```bash
# Navigate to frontend directory
cd frontend

# Open the enhanced frontend
open enhanced_index.html
# OR serve with Python
python -m http.server 8000
# Then visit: http://localhost:8000/enhanced_index.html
```

## 🎯 **Key Features to Test**

### **Enhanced ML Engine**
- ✅ **Deep Learning Models**: LSTM, Transformer, Autoencoder
- ✅ **Ensemble Detection**: Traditional ML + Deep Learning
- ✅ **Advanced Features**: 30+ engineered features
- ✅ **Model Persistence**: Save/load trained models

### **Modern Frontend**
- ✅ **Dark Mode**: Toggle between light/dark themes
- ✅ **Responsive Design**: Works on mobile and desktop
- ✅ **Interactive Charts**: Plotly.js visualizations
- ✅ **Real-time Updates**: Dynamic data loading

## 🔧 **Configuration Options**

### **ML Engine Settings**

```python
# In enhanced_ml_engine.py
analyzer = EnhancedEnergyConsumptionAnalyzer(
    base_dir="/path/to/your/data",
    device='auto'  # 'cpu' or 'cuda' for GPU
)
```

### **Frontend Settings**

```javascript
// In enhanced_script.js
const config = {
    apiEndpoint: 'http://localhost:8000/api',
    theme: 'auto', // 'light', 'dark', or 'auto'
    chartTheme: 'plotly_white' // or 'plotly_dark'
};
```

## 📊 **Sample Data Structure**

Your data should be organized as follows:

```
Energy Project/
├── April/
│   ├── 2 Bedroom Data - Apr/
│   │   ├── Apr_2bed_energy_consumption_day_1.csv
│   │   ├── Apr_2bed_energy_consumption_day_2.csv
│   │   └── ...
│   ├── 4 Bedroom Data - Apr/
│   └── 6 Bedroom Data - Apr/
├── May/
└── ...
```

**CSV Format:**
```csv
Day,Room No,Total Energy (kWh),00-02,02-04,04-06,06-08,08-10,10-12,12-14,14-16,16-18,18-20,20-22,22-24
1,1,4.693,0.145,0.089,0.156,0.176,0.379,0.382,0.363,0.357,0.106,0.987,0.620,0.928
1,2,3.912,0.136,0.195,0.057,0.081,0.499,0.207,0.192,0.188,0.345,0.709,0.602,0.696
```

## 🧪 **Testing Different Scenarios**

### **1. Basic Analysis (Traditional ML)**
```python
# Use the original optimized_ml_engine.py
python optimized_ml_engine.py
```

### **2. Enhanced Analysis (Deep Learning)**
```python
# Use the new enhanced_ml_engine.py
python enhanced_ml_engine.py
```

### **3. Frontend Demo**
- Open `frontend/enhanced_index.html`
- Select different bed types, months, and days
- Toggle between basic and enhanced analysis modes
- Switch between light and dark themes

## 📈 **Performance Comparison**

| Feature | Original | Enhanced |
|---------|----------|----------|
| ML Models | 5 (Traditional) | 8 (Traditional + Deep Learning) |
| Features | 20+ | 30+ |
| UI Framework | Bootstrap | Tailwind CSS |
| Dark Mode | ❌ | ✅ |
| Real-time | ❌ | ✅ (WebSocket ready) |
| Model Confidence | Basic | Advanced scoring |

## 🔍 **Troubleshooting**

### **Common Issues**

**1. Import Errors**
```bash
# Install missing dependencies
pip install torch torchvision transformers
```

**2. CUDA/GPU Issues**
```python
# Force CPU usage
analyzer = EnhancedEnergyConsumptionAnalyzer(device='cpu')
```

**3. Data Not Found**
```python
# Check your data path
analyzer = EnhancedEnergyConsumptionAnalyzer(
    base_dir="/correct/path/to/your/data"
)
```

**4. Frontend Not Loading**
```bash
# Check if all files are in the correct location
ls frontend/
# Should show: enhanced_index.html, enhanced_script.js
```

### **Performance Tips**

**For Large Datasets:**
```python
# Reduce training epochs for faster testing
self._train_lstm_model(model, X_train, y_train, X_test, y_test, epochs=20)
self._train_autoencoder(autoencoder, scaled_features, epochs=20)
self._train_transformer(transformer, X_train, y_train, X_test, y_test, epochs=20)
```

**For GPU Acceleration:**
```python
# Install CUDA version of PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🎯 **Next Steps**

1. **Test the enhanced system** with your data
2. **Compare results** between basic and enhanced modes
3. **Customize the UI** theme and layout
4. **Integrate with your existing workflow**

## 📞 **Support**

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the error messages in the console
3. Verify your data format matches the expected structure
4. Ensure all dependencies are installed correctly

## 🚀 **Ready to Deploy?**

Once you've tested the enhanced system locally, check out the [ROADMAP.md](./ROADMAP.md) for production deployment steps including:

- FastAPI backend setup
- PostgreSQL database integration
- AWS deployment
- Real-time processing pipeline
- Advanced monitoring and alerting

---

**🎉 You're all set!** The enhanced energy consumption analyzer is now running with deep learning capabilities and a modern, responsive UI.
