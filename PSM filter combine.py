import pandas as pd

# Load data
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905\PSM filter.xlsx"  # Replace with your actual file path
data = pd.read_excel(file_path)

# Reformat the data by interleaving the information of disease 2 and disease 1
merged_data = pd.DataFrame()

# Interleave the data
flattened_data = []
for idx, row in data.iterrows():
    flattened_data.append([
        row['No_Asymptomatic'], row['Sex_Asymptomatic'], row['Age_Asymptomatic'], row['Symptom status_Asymptomatic'], row['Cervical curvature type_Asymptomatic'], row['C7S_Asymptomatic'], row['Propensity score_Asymptomatic']
    ])
    flattened_data.append([
        row['No_Symptomatic'], row['Sex_Symptomatic'], row['Age_Symptomatic'], row['Symptom status_Symptomatic'], row['Cervical curvature type_Symptomatic'], row['C7S_Symptomatic'], row['Propensity score_Symptomatic']
    ])

# Create the interleaved DataFrame
merged_data = pd.DataFrame(flattened_data, columns=['No', 'Sex', 'Age', 'Symptom status', 'Cervical curvature type', 'C7S', 'Propensity score'])

# Save the interleaved data
output_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905\PSM filter combine.xlsx"  # Replace with the actual save path
merged_data.to_excel(output_path, index=False)

print(f"Interleaved data has been saved to {output_path}")
