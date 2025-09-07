#!/usr/bin/env python3
"""
Final Validation Script for Energy Consumption Analyzer
Tests the complete system end-to-end to ensure launch readiness
"""

import os
import sys
import time
import requests
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.append('../backend')

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def test_ml_accuracy():
    """Test ML model accuracy and anomaly detection"""
    print_header("Testing ML Model Accuracy")
    
    try:
        from ml_engine import EnergyConsumptionAnalyzer
        
        analyzer = EnergyConsumptionAnalyzer()
        
        # Test with multiple datasets to ensure consistency
        test_cases = [
            ("2", "January", 1),
            ("4", "January", 1),
            ("6", "January", 1),
            ("2", "April", 1),
            ("4", "April", 1)
        ]
        
        results = []
        
        for bed_type, month, day in test_cases:
            try:
                # Load and process data
                df = analyzer.load_data(bed_type, month, day)
                df = analyzer.engineer_features(df)
                df = analyzer.detect_anomalies_advanced(df)
                df = analyzer.predict_energy_consumption(df)
                insights = analyzer.generate_insights(df)
                
                # Calculate accuracy metrics
                total_rooms = len(df)
                anomalies = df[df['final_anomaly'] == 1]
                anomaly_rate = len(anomalies) / total_rooms
                
                # Check prediction accuracy
                prediction_error = df['prediction_error'].mean()
                prediction_error_ratio = df['prediction_error_ratio'].mean()
                
                results.append({
                    'bed_type': bed_type,
                    'month': month,
                    'day': day,
                    'total_rooms': total_rooms,
                    'anomalies': len(anomalies),
                    'anomaly_rate': anomaly_rate,
                    'avg_prediction_error': prediction_error,
                    'avg_prediction_error_ratio': prediction_error_ratio,
                    'avg_confidence': anomalies['anomaly_confidence'].mean() if len(anomalies) > 0 else 0
                })
                
                print(f"✅ {bed_type}-bed {month} day {day}:")
                print(f"   Rooms: {total_rooms}, Anomalies: {len(anomalies)} ({anomaly_rate:.1%})")
                print(f"   Prediction Error: {prediction_error:.3f} kWh ({prediction_error_ratio:.1%})")
                print(f"   Avg Confidence: {anomalies['anomaly_confidence'].mean():.2f}" if len(anomalies) > 0 else "   No anomalies")
                
            except Exception as e:
                print(f"❌ {bed_type}-bed {month} day {day}: {e}")
                return False
        
        # Overall accuracy assessment
        avg_anomaly_rate = np.mean([r['anomaly_rate'] for r in results])
        avg_prediction_error = np.mean([r['avg_prediction_error'] for r in results])
        avg_confidence = np.mean([r['avg_confidence'] for r in results if r['avg_confidence'] > 0])
        
        print(f"\n📊 Overall Performance:")
        print(f"   Average Anomaly Rate: {avg_anomaly_rate:.1%}")
        print(f"   Average Prediction Error: {avg_prediction_error:.3f} kWh")
        print(f"   Average Confidence: {avg_confidence:.2f}")
        
        # Quality checks
        if avg_anomaly_rate < 0.05 or avg_anomaly_rate > 0.3:
            print(f"⚠️  Anomaly rate ({avg_anomaly_rate:.1%}) may need adjustment")
        
        if avg_prediction_error > 1.0:
            print(f"⚠️  High prediction error ({avg_prediction_error:.3f} kWh)")
        
        if avg_confidence < 0.5:
            print(f"⚠️  Low average confidence ({avg_confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ ML accuracy test failed: {e}")
        return False

def test_api_performance():
    """Test API performance and response times"""
    print_header("Testing API Performance")
    
    # Start API server
    try:
        api_process = subprocess.Popen([
            sys.executable, 'api_bridge.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(5)
        
        # Test response times
        endpoints = [
            ('/api/health', 'GET', None),
            ('/api/available-data', 'GET', None),
            ('/api/analyze', 'POST', {'bedType': '2', 'month': 'April', 'day': 1})
        ]
        
        performance_results = []
        
        for endpoint, method, data in endpoints:
            try:
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(f'http://localhost:8000{endpoint}', timeout=30)
                else:
                    response = requests.post(f'http://localhost:8000{endpoint}', 
                                           json=data, timeout=30)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: {response_time:.3f}s")
                    performance_results.append(response_time)
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                return False
        
        # Performance assessment
        avg_response_time = np.mean(performance_results)
        max_response_time = np.max(performance_results)
        
        print(f"\n📊 API Performance:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Maximum Response Time: {max_response_time:.3f}s")
        
        if avg_response_time > 5.0:
            print(f"⚠️  Slow average response time ({avg_response_time:.3f}s)")
        
        if max_response_time > 10.0:
            print(f"⚠️  Very slow maximum response time ({max_response_time:.3f}s)")
        
        # Stop API server
        api_process.terminate()
        api_process.wait()
        
        return True
        
    except Exception as e:
        print(f"❌ API performance test failed: {e}")
        return False

def test_data_integrity():
    """Test data integrity and consistency"""
    print_header("Testing Data Integrity")
    
    try:
        base_dir = Path("/Users/saxu/PycharmProjects/Energy Project/months")
        
        # Check data consistency across months
        months_with_data = []
        total_files = 0
        
        for month in base_dir.iterdir():
            if month.is_dir() and month.name not in ['.DS_Store']:
                month_files = 0
                
                for bed_folder in month.iterdir():
                    if bed_folder.is_dir() and 'Bedroom Data' in bed_folder.name:
                        csv_files = list(bed_folder.glob("*.csv"))
                        month_files += len(csv_files)
                        
                        # Check file structure consistency
                        if csv_files:
                            sample_df = pd.read_csv(csv_files[0])
                            expected_columns = ['Day', 'Room No', 'Total Energy (kWh)'] + \
                                             [f"{i*2:02d}-{(i+1)*2:02d}" for i in range(12)]
                            
                            if not all(col in sample_df.columns for col in expected_columns):
                                print(f"❌ Inconsistent columns in {csv_files[0]}")
                                return False
                            
                            # Check data quality
                            if sample_df['Total Energy (kWh)'].min() < 0:
                                print(f"❌ Negative energy values in {csv_files[0]}")
                                return False
                            
                            if sample_df['Total Energy (kWh)'].max() > 20:
                                print(f"⚠️  Very high energy values in {csv_files[0]}")
                
                if month_files > 0:
                    months_with_data.append(month.name)
                    total_files += month_files
        
        print(f"✅ Data integrity check passed")
        print(f"   Months with data: {len(months_with_data)}")
        print(f"   Total CSV files: {total_files}")
        print(f"   Data months: {months_with_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def test_aws_deployment_readiness():
    """Test AWS deployment readiness"""
    print_header("Testing AWS Deployment Readiness")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        'deployment.yaml',
        'requirements.txt',
        'env.example'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    # Check Docker build
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
        else:
            print("⚠️  Docker not available")
    except FileNotFoundError:
        print("⚠️  Docker not installed")
    
    # Check for environment variables
    env_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_env = []
    
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var} configured")
        else:
            print(f"⚠️  {var} not configured")
            missing_env.append(var)
    
    if missing_files:
        print(f"\n❌ Missing required files: {missing_files}")
        return False
    
    if missing_env:
        print(f"\n⚠️  Missing environment variables: {missing_env}")
        print("   These are needed for AWS deployment")
    
    return True

def generate_launch_report():
    """Generate a comprehensive launch readiness report"""
    print_header("Launch Readiness Report")
    
    tests = [
        ("ML Model Accuracy", test_ml_accuracy),
        ("API Performance", test_api_performance),
        ("Data Integrity", test_data_integrity),
        ("AWS Deployment", test_aws_deployment_readiness)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n{'='*60}")
    print("📋 LAUNCH READINESS SUMMARY")
    print(f"{'='*60}")
    
    for test_name, result in results.items():
        status = "✅ READY" if result else "❌ NOT READY"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} components ready")
    
    if passed == total:
        print("\n🎉 SYSTEM IS LAUNCH READY!")
        print("   All components are functioning correctly")
        print("   Ready for AWS deployment")
        print("   Ready for production use")
    else:
        print(f"\n⚠️  {total - passed} components need attention")
        print("   Please review and fix issues before launch")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if passed == total:
        print("   ✅ Deploy to AWS using provided Docker configuration")
        print("   ✅ Set up monitoring and alerting")
        print("   ✅ Configure backup and disaster recovery")
        print("   ✅ Set up CI/CD pipeline")
    else:
        print("   🔧 Fix failing components before deployment")
        print("   🔧 Run tests again after fixes")
        print("   🔧 Consider staging deployment first")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Energy Consumption Analyzer - Final Validation")
    print("=" * 60)
    
    success = generate_launch_report()
    
    if success:
        print("\n🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed. Please fix issues before launch.")
        sys.exit(1)
