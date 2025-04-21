import pandas as pd
import ast
import tkinter as tk
from tkinter import filedialog
import os

# GUI file selection
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select input CSV", filetypes=[("CSV files", "*.csv")])

if not file_path:
    print("No file selected.")
    exit()

# Read CSV
df = pd.read_csv(file_path)

# Process data
flattened_rows = []
for _, row in df.iterrows():
    player_name = row['player_name']
    rating = row['rating']
    try:
        compositions = ast.literal_eval(row['rating_composition'])
    except Exception as e:
        compositions = []
    
    entry = {'player_name': player_name, 'rating': rating}
    for i, comp in enumerate(compositions[:3], start=1):
        entry[f'key{i}'] = comp.get('KEY')
        entry[f'date{i}'] = comp.get('DATE')
        entry[f'pts{i}'] = comp.get('POINTS')
    
    flattened_rows.append(entry)

# Output cleaned DataFrame
cleaned_df = pd.DataFrame(flattened_rows)

# Save output
output_path = os.path.splitext(file_path)[0] + "_cleaned.csv"
cleaned_df.to_csv(output_path, index=False)

print(f"Cleaned file saved to:\n{output_path}")
