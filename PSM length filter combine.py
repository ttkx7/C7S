import pandas as pd

# Read data (read the file with actual column names)
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM length filter.xlsx"
data = pd.read_excel(file_path)

# Create a list to store matching results
flattened_data = []

# Iterate over each row of data and interleave male and female data
for idx, row in data.iterrows():
    # Add male data (use actual English column names)
    flattened_data.append([
        row['No_Male_c7'],          # Actual column name: No_Male_c7
        row['Sex_Male_c7'],         # Actual column name: Sex_Male_c7
        row['Age_Male_c7'],         # Actual column name: Age_Male_c7
        row['Symptom_status_Male_c7'], # Actual column name: Symptom_status_Male_c7
        row['Cervical_curvature_type_Male_c7'], # Actual column name: Cervical_curvature_type_Male_c7
        row['C7_length_Male_c7'],   # Actual column name: C7_length_Male_c7
        row['C7S_Male_c7'],         # Actual column name: C7S_Male_c7
        row['Propensity_score_age_Male_c7'], # Actual column name: Propensity_score_age_Male_c7
        row['Propensity_score_c7_Male']      # Actual column name: Propensity_score_c7_Male
    ])
    
    # Add female data (use actual English column names)
    flattened_data.append([
        row['No_Female'],           # Actual column name: No_Female
        row['Sex_Female_c7'],       # Actual column name: Sex_Female_c7
        row['Age_Female_c7'],       # Actual column name: Age_Female_c7
        row['Symptom_status_Female_c7'], # Actual column name: Symptom_status_Female_c7
        row['Cervical_curvature_type_Female_c7'], # Actual column name: Cervical_curvature_type_Female_c7
        row['C7_length_Female_c7'], # Actual column name: C7_length_Female_c7
        row['C7S_Female_c7'],       # Actual column name: C7S_Female_c7
        row['Propensity_score_age_Female_c7'], # Actual column name: Propensity_score_age_Female_c7
        row['Propensity_score_c7_Female']    # Actual column name: Propensity_score_c7_Female
    ])

# Create new DataFrame (output column names follow unified naming rules)
merged_data = pd.DataFrame(flattened_data, columns=[
    'No', 'Sex', 'Age', 'Symptom status', 'cervical curvature type', 'C7 length', 'C7S', 'propensity_score_age', 'propensity_score_c7'
])

# Save matching results
output_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM length filter combine.xlsx"
merged_data.to_excel(output_path, index=False)

print(f"Matching results have been saved to {output_path}")