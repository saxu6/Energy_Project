import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#params
num_rooms = 15
num_students_per_room = 6
time_intervals = [(f"{i:02d}-{i + 2:02d}") for i in range(0, 24, 2)]
columns = ["Room No"] + time_intervals + ["Total Energy (kWh)"]
num_days = 30
month = "Jan"

# creating the dataset

# this function makes the data for each cell which holds the energy consumed per interval
def generate_energy_usage():
    usage = []
    for i in range(0, 24, 2):
        if 0 <= i < 8:
            usage.append(np.random.uniform(0.2, 0.6))
        elif 8 <= i < 12:
            usage.append(np.random.uniform(0.6, 1.5))
        elif 12 <= i < 18:
            usage.append(np.random.uniform(0.3, 1.2))
        elif 18 <= i < 24:
            usage.append(np.random.uniform(1.2, 3.0))
    return usage


# storing the data in a well-labelled csv
for day in range(1, num_days + 1):
    data = []
    for room_no in range(1, num_rooms + 1):
        energy_usage = generate_energy_usage()
        total_energy = sum(energy_usage)
        data.append([day, room_no] + energy_usage + [total_energy])

    columns = ["Day", "Room No"] + time_intervals + ["Total Energy (kWh)"]
    df = pd.DataFrame(data, columns=columns)

    daily_csv_filename = f"{month}_6bed_energy_consumption_day_{day}.csv"
    df.to_csv(daily_csv_filename, index=False)

# day avg
df_all = pd.concat([pd.read_csv(f"{month}_6bed_energy_consumption_day_{day}.csv") for day in range(1, num_days + 1)])
daily_avg_energy = df_all.groupby("Day")["Total Energy (kWh)"].mean()
print("Average daily energy consumption per day:")
print(daily_avg_energy)

# month avg
monthly_avg_energy = daily_avg_energy.mean()
print(f"Monthly average energy consumption: {monthly_avg_energy:.2f} kWh")

# graph
plt.figure(figsize=(10, 5))
plt.plot(daily_avg_energy.index, daily_avg_energy.values, marker='o', linestyle='-', label='Daily Avg Energy')
plt.axhline(y=monthly_avg_energy, color='r', linestyle='--', label=f'{month} Monthly Avg Energy')
plt.xlabel("Day")
plt.ylabel("Energy Consumption (kWh)")
plt.title(f"Daily Average Energy Consumption vs {month} Monthly Average for 6 bed")
plt.legend()
plt.grid()
plt.show()
