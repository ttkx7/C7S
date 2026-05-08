import pandas as pd

# Read data (read the file with actual column names)
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM height filter.xlsx"
data = pd.read_excel(file_path)

# Create a list to store matching results
flattened_data = []

# Iterate over each row of data and interleave male and female data
for idx, row in data.iterrows():
    # Add male data (exact match with actual column names)
    flattened_data.append([
        row['No_Male_c7'],          # Actual column name
        row['Sex_Male_c7'],         # Actual column name
        row['Age_Male_c7'],         # Actual column name
        row['Symptom_status_Male_c7'],  # Actual column name (replace space with underscore)
        row['Cervical_curvature_type_Male_c7'],  # Actual column name (uppercase C + underscore)
        row['C7_height_Male_c7'],   # Actual column name (replace space with underscore)
        row['C7S_Male_c7'],         # Actual column name
        row['Propensity_score_age_Male_c7'],  # Actual column name (uppercase P)
        row['Propensity_score_c7_Male']       # Actual column name (uppercase P)
    ])
    
    # Add female data (exact match with actual column names)
    flattened_data.append([
        row['No_Female'],           # Actual column name (no _c7 suffix)
        row['Sex_Female_c7'],       # Actual column name
        row['Age_Female_c7'],       # Actual column name
        row['Symptom_status_Female_c7'],  # Actual column name (replace space with underscore)
        row['Cervical_curvature_type_Female_c7'],  # Actual column name (uppercase C + underscore)
        row['C7_height_Female_c7'], # Actual column name (replace space with underscore)
        row['C7S_Female_c7'],       # Actual column name
        row['Propensity_score_age_Female_c7'],  # Actual column name (uppercase P)
        row['Propensity_score_c7_Female']       # Actual column name (uppercase P)
    ])

# Create new DataFrame (output column names follow your standard naming rules)
merged_data = pd.DataFrame(flattened_data, columns=[
    'No', 'Sex', 'Age', 'Symptom status', 'cervical curvature type', 'C7 height', 'C7S', 'propensity_score_age', 'propensity_score_c7'
])

# Save matching results
output_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM height filter combine.xlsx"
merged_data.to_excel(output_path, index=False)

print(f"Matching results have been saved to {output_path}")