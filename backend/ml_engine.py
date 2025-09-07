import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.svm import OneClassSVM
import joblib

# Advanced ML
from scipy import stats
from scipy.signal import savgol_filter
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

# Visualization
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
# Only initialize notebook mode if in IPython environment
try:
    pyo.init_notebook_mode(connected=True)
except ImportError:
    pass  # Not in notebook environment

class EnergyConsumptionAnalyzer:
    """
    Advanced Energy Consumption Analysis with Multiple ML Models
    """
    
    def __init__(self, base_dir=None):
        from config import DATA_DIR
        self.base_dir = base_dir if base_dir else str(DATA_DIR)
        self.scaler = RobustScaler()
        self.models = {}
        self.feature_columns = []
        self.anomaly_thresholds = {}
        
    def load_data(self, bed_type, month, day):
        """Load and validate energy consumption data"""
        month = self._validate_month(month)
        day = self._validate_day(month, day)
        month_abbr = month[:3]
        folder_name = f"{bed_type} Bedroom Data - {month_abbr}"
        filename = f"{month_abbr}_{bed_type}bed_energy_consumption_day_{day}.csv"
        file_path = os.path.join(self.base_dir, month, folder_name, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        df = pd.read_csv(file_path)
        if 'Total Energy (kWh)' not in df.columns:
            raise ValueError("Missing 'Total Energy (kWh)' column in dataset.")
            
        return df
    
    def _validate_month(self, month):
        """Validate month input"""
        month = month.title()
        valid_months = [datetime(2000, i, 1).strftime('%B') for i in range(1, 13)]
        if month not in valid_months:
            raise ValueError(f"Invalid month! Choose from: {valid_months}")
        return month
    
    def _validate_day(self, month, day):
        """Validate day input"""
        month_number = datetime.strptime(month, "%B").month
        year = datetime.now().year
        max_days = (datetime(year, month_number + 1, 1) - pd.Timedelta(days=1)).day if month_number < 12 else 31
        if not (1 <= day <= max_days):
            raise ValueError(f"Invalid day! Choose between 1 and {max_days}.")
        return day
    
    def engineer_features(self, df):
        """Advanced feature engineering for energy consumption analysis"""
        df = df.copy()
        
        # Time-based features
        time_columns = [col for col in df.columns if '-' in col and col != 'Room No']
        
        # Peak usage features
        df['peak_usage'] = df[time_columns].max(axis=1)
        df['off_peak_usage'] = df[time_columns].min(axis=1)
        df['usage_variance'] = df[time_columns].var(axis=1)
        df['usage_std'] = df[time_columns].std(axis=1)
        df['usage_range'] = df[time_columns].max(axis=1) - df[time_columns].min(axis=1)
        
        # Statistical features
        df['usage_skewness'] = df[time_columns].skew(axis=1)
        df['usage_kurtosis'] = df[time_columns].kurtosis(axis=1)
        df['usage_median'] = df[time_columns].median(axis=1)
        df['usage_q75'] = df[time_columns].quantile(0.75, axis=1)
        df['usage_q25'] = df[time_columns].quantile(0.25, axis=1)
        df['usage_iqr'] = df['usage_q75'] - df['usage_q25']
        
        # Peak hours analysis (18-22 typically highest usage)
        peak_hours = ['18-20', '20-22']
        df['peak_hours_usage'] = df[peak_hours].sum(axis=1)
        df['peak_hours_ratio'] = df['peak_hours_usage'] / df['Total Energy (kWh)']
        
        # Morning usage (06-10)
        morning_hours = ['06-08', '08-10']
        df['morning_usage'] = df[morning_hours].sum(axis=1)
        df['morning_ratio'] = df['morning_usage'] / df['Total Energy (kWh)']
        
        # Night usage (22-06)
        night_hours = ['22-24', '00-02', '02-04', '04-06']
        df['night_usage'] = df[night_hours].sum(axis=1)
        df['night_ratio'] = df['night_usage'] / df['Total Energy (kWh)']
        
        # Anomaly indicators
        df['z_score'] = np.abs(stats.zscore(df['Total Energy (kWh)']))
        df['iqr_score'] = np.abs((df['Total Energy (kWh)'] - df['Total Energy (kWh)'].median()) / df['Total Energy (kWh)'].std())
        
        # Smoothing features
        df['smoothed_usage'] = savgol_filter(df['Total Energy (kWh)'], window_length=5, polyorder=2)
        df['usage_trend'] = df['Total Energy (kWh)'] - df['smoothed_usage']
        
        # Store feature columns for later use
        self.feature_columns = [col for col in df.columns if col not in ['Day', 'Room No', 'Total Energy (kWh)']]
        
        return df
    
    def detect_anomalies_advanced(self, df):
        """Multi-model anomaly detection system"""
        df = df.copy()
        
        # Prepare features for anomaly detection
        feature_data = df[self.feature_columns].fillna(0)
        scaled_features = self.scaler.fit_transform(feature_data)
        
        # 1. Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42, n_estimators=200)
        df['iso_forest_anomaly'] = iso_forest.fit_predict(scaled_features)
        
        # 2. One-Class SVM
        svm = OneClassSVM(kernel='rbf', nu=0.1, gamma='scale')
        df['svm_anomaly'] = svm.fit_predict(scaled_features)
        
        # 3. DBSCAN Clustering
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        df['dbscan_cluster'] = dbscan.fit_predict(scaled_features)
        df['dbscan_anomaly'] = (df['dbscan_cluster'] == -1).astype(int)
        
        # 4. Statistical Methods
        # Z-score based
        z_threshold = 2.5
        df['z_score_anomaly'] = (df['z_score'] > z_threshold).astype(int)
        
        # IQR based
        q1 = df['Total Energy (kWh)'].quantile(0.25)
        q3 = df['Total Energy (kWh)'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df['iqr_anomaly'] = ((df['Total Energy (kWh)'] < lower_bound) | 
                            (df['Total Energy (kWh)'] > upper_bound)).astype(int)
        
        # 5. Ensemble Decision
        anomaly_scores = (df['iso_forest_anomaly'] == -1).astype(int) + \
                        (df['svm_anomaly'] == -1).astype(int) + \
                        df['dbscan_anomaly'] + \
                        df['z_score_anomaly'] + \
                        df['iqr_anomaly']
        
        # Consensus threshold (at least 2 models agree)
        df['final_anomaly'] = (anomaly_scores >= 2).astype(int)
        df['anomaly_confidence'] = anomaly_scores / 5.0
        
        # 6. Anomaly Classification
        df['anomaly_type'] = 'Normal'
        
        # High consumption anomalies
        high_consumption = df['Total Energy (kWh)'] > df['Total Energy (kWh)'].quantile(0.9)
        df.loc[high_consumption & (df['final_anomaly'] == 1), 'anomaly_type'] = 'High Consumption'
        
        # Low consumption anomalies
        low_consumption = df['Total Energy (kWh)'] < df['Total Energy (kWh)'].quantile(0.1)
        df.loc[low_consumption & (df['final_anomaly'] == 1), 'anomaly_type'] = 'Low Consumption'
        
        # Unusual patterns
        unusual_pattern = (df['usage_variance'] > df['usage_variance'].quantile(0.9)) & (df['final_anomaly'] == 1)
        df.loc[unusual_pattern, 'anomaly_type'] = 'Unusual Pattern'
        
        # Store models for later use
        self.models['iso_forest'] = iso_forest
        self.models['svm'] = svm
        self.models['dbscan'] = dbscan
        self.anomaly_thresholds = {
            'z_threshold': z_threshold,
            'iqr_bounds': (lower_bound, upper_bound)
        }
        
        return df
    
    def predict_energy_consumption(self, df):
        """Predict energy consumption using multiple models"""
        df = df.copy()
        
        # Prepare features
        feature_data = df[self.feature_columns].fillna(0)
        X = feature_data.drop(['iso_forest_anomaly', 'svm_anomaly', 'dbscan_cluster', 
                              'dbscan_anomaly', 'z_score_anomaly', 'iqr_anomaly', 
                              'final_anomaly', 'anomaly_confidence', 'anomaly_type'], axis=1, errors='ignore')
        
        y = df['Total Energy (kWh)']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 1. Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        df['rf_prediction'] = rf_model.predict(X)
        
        # 2. Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        df['lr_prediction'] = lr_model.predict(X)
        
        # 3. Ensemble prediction
        df['ensemble_prediction'] = (df['rf_prediction'] + df['lr_prediction']) / 2
        
        # Calculate prediction errors
        df['prediction_error'] = abs(df['Total Energy (kWh)'] - df['ensemble_prediction'])
        df['prediction_error_ratio'] = df['prediction_error'] / df['Total Energy (kWh)']
        
        # Store models
        self.models['random_forest'] = rf_model
        self.models['linear_regression'] = lr_model
        
        return df
    
    def generate_insights(self, df):
        """Generate comprehensive insights and recommendations"""
        insights = {
            'summary': {},
            'anomalies': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Summary statistics
        insights['summary'] = {
            'total_rooms': len(df),
            'total_energy': df['Total Energy (kWh)'].sum(),
            'avg_energy': df['Total Energy (kWh)'].mean(),
            'std_energy': df['Total Energy (kWh)'].std(),
            'min_energy': df['Total Energy (kWh)'].min(),
            'max_energy': df['Total Energy (kWh)'].max(),
            'anomaly_count': df['final_anomaly'].sum(),
            'anomaly_percentage': (df['final_anomaly'].sum() / len(df)) * 100
        }
        
        # Anomaly analysis
        anomalies = df[df['final_anomaly'] == 1]
        if len(anomalies) > 0:
            insights['anomalies'] = {
                'high_consumption': len(anomalies[anomalies['anomaly_type'] == 'High Consumption']),
                'low_consumption': len(anomalies[anomalies['anomaly_type'] == 'Low Consumption']),
                'unusual_pattern': len(anomalies[anomalies['anomaly_type'] == 'Unusual Pattern']),
                'avg_confidence': anomalies['anomaly_confidence'].mean(),
                'top_anomalous_rooms': anomalies.nlargest(3, 'anomaly_confidence')[['Room No', 'Total Energy (kWh)', 'anomaly_type', 'anomaly_confidence']].to_dict('records')
            }
        
        # Pattern analysis
        insights['patterns'] = {
            'peak_hours_avg': df['peak_hours_usage'].mean(),
            'morning_usage_avg': df['morning_usage'].mean(),
            'night_usage_avg': df['night_usage'].mean(),
            'usage_variance_avg': df['usage_variance'].mean(),
            'most_efficient_room': df.loc[df['Total Energy (kWh)'].idxmin(), 'Room No'],
            'least_efficient_room': df.loc[df['Total Energy (kWh)'].idxmax(), 'Room No']
        }
        
        # Recommendations
        recommendations = []
        
        if insights['summary']['anomaly_percentage'] > 15:
            recommendations.append("High anomaly rate detected. Consider investigating equipment or occupancy patterns.")
        
        if df['peak_hours_ratio'].mean() > 0.4:
            recommendations.append("Peak hours usage is high. Consider load balancing strategies.")
        
        if df['night_usage'].mean() > df['night_usage'].quantile(0.8):
            recommendations.append("Unusually high night usage detected. Check for equipment left on.")
        
        if df['usage_variance'].mean() > df['usage_variance'].quantile(0.8):
            recommendations.append("High usage variance suggests inconsistent patterns. Consider occupancy monitoring.")
        
        insights['recommendations'] = recommendations
        
        return insights
    
    def create_interactive_visualizations(self, df, bed_type, month, day):
        """Create comprehensive interactive visualizations"""
        
        # 1. Main Energy Consumption Plot
        fig1 = go.Figure()
        
        # Normal points
        normal_df = df[df['final_anomaly'] == 0]
        fig1.add_trace(go.Scatter(
            x=normal_df['Room No'],
            y=normal_df['Total Energy (kWh)'],
            mode='markers',
            name='Normal',
            marker=dict(color='blue', size=10),
            hovertemplate='Room %{x}<br>Energy: %{y:.2f} kWh<extra></extra>'
        ))
        
        # Anomaly points
        anomaly_df = df[df['final_anomaly'] == 1]
        if len(anomaly_df) > 0:
            fig1.add_trace(go.Scatter(
                x=anomaly_df['Room No'],
                y=anomaly_df['Total Energy (kWh)'],
                mode='markers',
                name='Anomaly',
                marker=dict(color='red', size=15, symbol='diamond'),
                hovertemplate='Room %{x}<br>Energy: %{y:.2f} kWh<br>Type: %{text}<extra></extra>',
                text=anomaly_df['anomaly_type']
            ))
        
        # Average line
        avg_energy = df['Total Energy (kWh)'].mean()
        fig1.add_hline(y=avg_energy, line_dash="dash", line_color="green", 
                      annotation_text=f"Average: {avg_energy:.2f} kWh")
        
        fig1.update_layout(
            title=f"Energy Consumption Analysis - {bed_type}-Bed ({month} {day})",
            xaxis_title="Room Number",
            yaxis_title="Total Energy Consumption (kWh)",
            hovermode='closest'
        )
        
        # 2. Feature Analysis
        fig2 = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Peak Hours Usage', 'Usage Variance', 'Z-Score Distribution', 'Usage Patterns'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Peak hours usage
        fig2.add_trace(go.Bar(x=df['Room No'], y=df['peak_hours_usage'], name='Peak Hours'),
                      row=1, col=1)
        
        # Usage variance
        fig2.add_trace(go.Bar(x=df['Room No'], y=df['usage_variance'], name='Variance'),
                      row=1, col=2)
        
        # Z-score distribution
        fig2.add_trace(go.Histogram(x=df['z_score'], name='Z-Score', nbinsx=20),
                      row=2, col=1)
        
        # Usage patterns (morning vs night)
        fig2.add_trace(go.Bar(x=df['Room No'], y=df['morning_usage'], name='Morning'),
                      row=2, col=2)
        fig2.add_trace(go.Bar(x=df['Room No'], y=df['night_usage'], name='Night'),
                      row=2, col=2)
        
        fig2.update_layout(title_text="Feature Analysis", showlegend=True)
        
        # 3. Time Series Analysis
        time_columns = [col for col in df.columns if '-' in col and col != 'Room No']
        time_data = df[time_columns].mean()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=list(time_data.index),
            y=time_data.values,
            mode='lines+markers',
            name='Average Usage by Time',
            line=dict(color='purple', width=3)
        ))
        
        fig3.update_layout(
            title="Average Energy Usage by Time Interval",
            xaxis_title="Time Interval",
            yaxis_title="Average Energy (kWh)",
            xaxis_tickangle=-45
        )
        
        return fig1, fig2, fig3
    
    def save_models(self, filepath='models/'):
        """Save trained models for later use"""
        os.makedirs(filepath, exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, f"{filepath}/{name}_model.pkl")
        
        # Save scaler and thresholds
        joblib.dump(self.scaler, f"{filepath}/scaler.pkl")
        joblib.dump(self.anomaly_thresholds, f"{filepath}/thresholds.pkl")
        joblib.dump(self.feature_columns, f"{filepath}/feature_columns.pkl")
    
    def load_models(self, filepath='models/'):
        """Load previously trained models"""
        for name in ['iso_forest', 'svm', 'dbscan', 'random_forest', 'linear_regression']:
            try:
                self.models[name] = joblib.load(f"{filepath}/{name}_model.pkl")
            except FileNotFoundError:
                pass
        
        try:
            self.scaler = joblib.load(f"{filepath}/scaler.pkl")
            self.anomaly_thresholds = joblib.load(f"{filepath}/thresholds.pkl")
            self.feature_columns = joblib.load(f"{filepath}/feature_columns.pkl")
        except FileNotFoundError:
            pass

def main():
    """Main execution function"""
    analyzer = EnergyConsumptionAnalyzer()
    
    # Get user input
    bed_type = input("Enter bed type (2, 4, 6): ").strip()
    month = input("Enter month (e.g., January): ").strip().title()
    day = input("Enter day: ").strip()
    
    # Validate inputs
    if not bed_type.isdigit() or bed_type not in ["2", "4", "6"]:
        raise ValueError("Invalid bed type!")
    if not day.isdigit():
        raise ValueError("Invalid day!")
    day = int(day)
    
    # Load and process data
    print("Loading data...")
    df = analyzer.load_data(bed_type, month, day)
    
    print("Engineering features...")
    df = analyzer.engineer_features(df)
    
    print("Detecting anomalies...")
    df = analyzer.detect_anomalies_advanced(df)
    
    print("Predicting energy consumption...")
    df = analyzer.predict_energy_consumption(df)
    
    print("Generating insights...")
    insights = analyzer.generate_insights(df)
    
    # Display results
    print("\n" + "="*50)
    print("ENERGY CONSUMPTION ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Rooms: {insights['summary']['total_rooms']}")
    print(f"   Total Energy: {insights['summary']['total_energy']:.2f} kWh")
    print(f"   Average Energy: {insights['summary']['avg_energy']:.2f} kWh")
    print(f"   Anomalies Detected: {insights['summary']['anomaly_count']} ({insights['summary']['anomaly_percentage']:.1f}%)")
    
    if insights['anomalies']:
        print(f"\n🚨 ANOMALIES:")
        print(f"   High Consumption: {insights['anomalies']['high_consumption']}")
        print(f"   Low Consumption: {insights['anomalies']['low_consumption']}")
        print(f"   Unusual Patterns: {insights['anomalies']['unusual_pattern']}")
        print(f"   Average Confidence: {insights['anomalies']['avg_confidence']:.2f}")
        
        print(f"\n   Top Anomalous Rooms:")
        for room in insights['anomalies']['top_anomalous_rooms']:
            print(f"     Room {room['Room No']}: {room['Total Energy (kWh)']:.2f} kWh ({room['anomaly_type']})")
    
    print(f"\n📈 PATTERNS:")
    print(f"   Peak Hours Usage: {insights['patterns']['peak_hours_avg']:.2f} kWh")
    print(f"   Morning Usage: {insights['patterns']['morning_usage_avg']:.2f} kWh")
    print(f"   Night Usage: {insights['patterns']['night_usage_avg']:.2f} kWh")
    print(f"   Most Efficient: Room {insights['patterns']['most_efficient_room']}")
    print(f"   Least Efficient: Room {insights['patterns']['least_efficient_room']}")
    
    if insights['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Create visualizations
    print("\nCreating visualizations...")
    fig1, fig2, fig3 = analyzer.create_interactive_visualizations(df, bed_type, month, day)
    
    # Save plots
    fig1.write_html(f"energy_consumption_{bed_type}bed_{month}_{day}.html")
    fig2.write_html(f"feature_analysis_{bed_type}bed_{month}_{day}.html")
    fig3.write_html(f"time_series_{bed_type}bed_{month}_{day}.html")
    
    print(f"\n✅ Analysis complete! Interactive plots saved as HTML files.")
    
    # Save models
    analyzer.save_models()
    print("Models saved for future use.")

if __name__ == "__main__":
    main()
