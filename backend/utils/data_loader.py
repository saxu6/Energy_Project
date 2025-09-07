import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from datetime import datetime

from config import DATA_DIR
base_dir = str(DATA_DIR)

def validate_month(month):
    month = month.title()
    valid_months = [datetime(2000, i, 1).strftime('%B') for i in range(1, 13)]
    if month not in valid_months:
        raise ValueError(f"Invalid month! Choose from: {valid_months}")
    return month

def validate_day(month, day):
    month_number = datetime.strptime(month, "%B").month
    year = datetime.now().year
    max_days = (datetime(year, month_number + 1, 1) - pd.Timedelta(days=1)).day if month_number < 12 else 31
    if not (1 <= day <= max_days):
        raise ValueError(f"Invalid day! Choose between 1 and {max_days}.")
    return day

def load_data(bed_type, month, day):
    month = validate_month(month)
    day = validate_day(month, day)
    month_abbr = month[:3]
    folder_name = f"{bed_type} Bedroom Data - {month_abbr}"
    filename = f"{month_abbr}_{bed_type}bed_energy_consumption_day_{day}.csv"
    file_path = os.path.join(base_dir, month, folder_name, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_csv(file_path)
    if 'Total Energy (kWh)' not in df.columns:
        raise ValueError("Missing 'Total Energy (kWh)' column in dataset.")
    return df

def detect_anomalies(df):
    avg_energy = df['Total Energy (kWh)'].mean()
    model = IsolationForest(contamination=0.1, random_state=42)
    df['Anomaly'] = model.fit_predict(df[['Total Energy (kWh)']])
    df['Anomaly'] = df['Anomaly'].map({1: "Normal", -1: "Anomaly"})
    df['Anomaly Reason'] = "Normal"
    df.loc[df['Total Energy (kWh)'] > (1.5 * avg_energy), 'Anomaly Reason'] = 'Unusual Spike'
    df.loc[df['Total Energy (kWh)'] > (2 * avg_energy), 'Anomaly Reason'] = 'Possible Overuse'
    df.loc[df['Total Energy (kWh)'] > (3 * avg_energy), 'Anomaly Reason'] = 'Faulty Equipment?'
    df.loc[df['Total Energy (kWh)'] < avg_energy, 'Anomaly'] = 'Normal'
    return df

def plot_energy_consumption(df, bed_type, month, day):
    plt.figure(figsize=(12, 6))
    anomaly_colors = df['Anomaly'].map({"Normal": "blue", "Anomaly": "red"})

    sns.scatterplot(x=df['Room No'], y=df['Total Energy (kWh)'], hue=df['Anomaly'],
                    palette={"Normal": 'blue', "Anomaly": 'red'}, s=100, edgecolor="black")
    avg_energy = df['Total Energy (kWh)'].mean()
    plt.axhline(avg_energy, color='green', linestyle='--', label="Day's Avg Energy")
    for i, row in df.iterrows():
        plt.text(row['Room No'], row['Total Energy (kWh)'], str(row['Room No']),
                 color=anomaly_colors[i], fontsize=10, ha='right', va='bottom', fontweight='bold')
    plt.xlabel("Room Number")
    plt.ylabel("Total Energy Consumption (kWh)")
    plt.title(f"Energy Consumption for {bed_type}-Bed on {month} {day}")
    plt.legend()
    plt.show()

def main():
    bed_type = input("Enter bed type (2, 4, 6): ").strip()
    month = input("Enter month (e.g., January): ").strip().title()
    day = input("Enter day: ").strip()
    if not bed_type.isdigit() or bed_type not in ["2", "4", "6"]:
        raise ValueError("Invalid bed type!")
    if not day.isdigit():
        raise ValueError("Invalid day!")
    day = int(day)
    df = load_data(bed_type, month, day)
    df = detect_anomalies(df)
    print("Anomaly detection is complete!")
    print("\n---- Anomalies and Causes ---")
    print(df[df['Anomaly'] == "Anomaly"][['Room No', 'Total Energy (kWh)', 'Anomaly Reason']])
    plot_energy_consumption(df, bed_type, month, day)

if __name__ == "__main__":
    main()
