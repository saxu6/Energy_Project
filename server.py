#!/usr/bin/env python3
"""
API Bridge for Energy Consumption Analyzer
Connects the frontend with the ML backend for real-time analysis
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
from backend.ml_engine import EnergyConsumptionAnalyzer
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the ML analyzer
from config import DATA_DIR
analyzer = EnergyConsumptionAnalyzer(base_dir=str(DATA_DIR))

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """API endpoint for energy consumption analysis"""
    try:
        data = request.get_json()
        
        # Extract parameters
        bed_type = data.get('bedType')
        month = data.get('month')
        day = data.get('day')
        
        # Validate parameters
        if not all([bed_type, month, day]):
            return jsonify({
                'error': 'Missing required parameters: bedType, month, day'
            }), 400
        
        # Load and process data
        df = analyzer.load_data(bed_type, month, int(day))
        df = analyzer.engineer_features(df)
        df = analyzer.detect_anomalies_advanced(df)
        df = analyzer.predict_energy_consumption(df)
        insights = analyzer.generate_insights(df)
        
        # Convert DataFrame to JSON-serializable format
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        # Prepare response data
        df_dict = df.to_dict('records')
        df_dict = convert_numpy_types(df_dict)
        insights = convert_numpy_types(insights)
        
        response_data = {
            'success': True,
            'data': df_dict,
            'insights': insights,
            'summary': {
                'total_rooms': int(len(df)),
                'total_energy': float(df['Total Energy (kWh)'].sum()),
                'avg_energy': float(df['Total Energy (kWh)'].mean()),
                'anomaly_count': int(df['final_anomaly'].sum()),
                'anomaly_percentage': float((df['final_anomaly'].sum() / len(df)) * 100)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/available-data', methods=['GET'])
def get_available_data():
    """Get available data files"""
    try:
        base_dir = analyzer.base_dir
        available_data = {}
        
        # Scan for available data
        for month in os.listdir(base_dir):
            month_path = os.path.join(base_dir, month)
            if os.path.isdir(month_path) and month not in ['venv', '__pycache__', 'models']:
                available_data[month] = {}
                
                for bed_folder in os.listdir(month_path):
                    if 'Bedroom Data' in bed_folder:
                        bed_type = bed_folder.split()[0]  # Extract bed type
                        bed_path = os.path.join(month_path, bed_folder)
                        
                        if os.path.isdir(bed_path):
                            csv_files = [f for f in os.listdir(bed_path) if f.endswith('.csv')]
                            days = []
                            
                            for csv_file in csv_files:
                                # Extract day number from filename
                                if 'day_' in csv_file:
                                    day_str = csv_file.split('day_')[1].split('.')[0]
                                    try:
                                        days.append(int(day_str))
                                    except ValueError:
                                        continue
                            
                            if days:
                                available_data[month][bed_type] = sorted(days)
        
        return jsonify({
            'success': True,
            'available_data': available_data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Energy Consumption Analyzer API',
        'version': '1.0.0'
    })

@app.route('/api/models/save', methods=['POST'])
def save_models():
    """Save trained models"""
    try:
        data = request.get_json()
        filepath = data.get('filepath', 'models/')
        
        analyzer.save_models(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Models saved to {filepath}'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/models/load', methods=['POST'])
def load_models():
    """Load trained models"""
    try:
        data = request.get_json()
        filepath = data.get('filepath', 'models/')
        
        analyzer.load_models(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Models loaded from {filepath}'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_results(format):
    """Export analysis results"""
    try:
        data = request.get_json()
        analysis_data = data.get('data', [])
        
        if format == 'csv':
            df = pd.DataFrame(analysis_data)
            csv_content = df.to_csv(index=False)
            return jsonify({
                'success': True,
                'data': csv_content,
                'filename': 'energy_analysis_results.csv'
            })
        
        elif format == 'json':
            return jsonify({
                'success': True,
                'data': analysis_data,
                'filename': 'energy_analysis_results.json'
            })
        
        else:
            return jsonify({
                'error': f'Unsupported format: {format}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Energy Consumption Analyzer API...")
    print("📊 ML Engine initialized")
    print("🌐 Frontend available at: http://localhost:8000")
    print("🔌 API endpoints available at: http://localhost:8000/api")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )
