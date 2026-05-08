import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

# Load data
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905\PSM.xlsx"  # Replace with your file path
data = pd.read_excel(file_path)

# Check if column names match the expected ones
expected_columns = ['No', 'Sex', 'Age', 'Symptom status', 'cervical curvature type', 'C7S', 'Propensity score', 'Weight']
if not all(col in data.columns for col in expected_columns):
    raise ValueError("Column names do not match, please check the input file!")

# Replace values in 'Symptom status' column: 1 -> Symptomatic, 2 -> Asymptomatic
data['Symptom status'] = data['Symptom status'].replace({1: 'Symptomatic', 2: 'Asymptomatic'})

# Separate the data based on Symptom status (Symptomatic and Asymptomatic)
case_1 = data[data['Symptom status'] == 'Symptomatic'].copy()  # Symptomatic group (Symptom status == 1)
case_2 = data[data['Symptom status'] == 'Asymptomatic'].copy()  # Asymptomatic group (Symptom status == 2)

# Create a list to store the matching results
matched_results = []

# Iterate through each sample in the Asymptomatic group (Symptom status 'Asymptomatic')
for idx_2, row_2 in case_2.iterrows():
    # Find all exact matches in the Symptomatic group (Symptom status 'Symptomatic')
    exact_matches = case_1[
        (case_1['Sex'] == row_2['Sex']) &
        (case_1['Age'] == row_2['Age']) &
        (case_1['Propensity score'] == row_2['Propensity score'])
    ]

    if not exact_matches.empty:
        # If multiple exact matches, randomly select one
        selected_match = exact_matches.sample(n=1)
    else:
        # If no exact match, use nearest neighbor matching
        case_1_scores = case_1[['Sex', 'Age', 'Propensity score']].values
        row_2_score = row_2[['Sex', 'Age', 'Propensity score']].values.reshape(1, -1)

        # Calculate Euclidean distance
        distances = cdist(case_1_scores, row_2_score, metric='euclidean')
        nearest_idx = np.argmin(distances)
        selected_match = case_1.iloc[[nearest_idx]]

    # Store the matching results, ensuring correct Symptom status label for both groups
    matched_results.append({
        'No_Asymptomatic': row_2['No'],  # Left part: Asymptomatic group
        'Sex_Asymptomatic': row_2['Sex'],
        'Age_Asymptomatic': row_2['Age'],
        'Cervical curvature type_Asymptomatic': row_2['cervical curvature type'],
        'C7S_Asymptomatic': row_2['C7S'],
        'Propensity score_Asymptomatic': row_2['Propensity score'],
        'No_Symptomatic': selected_match['No'].values[0],  # Right part: Symptomatic group
        'Sex_Symptomatic': selected_match['Sex'].values[0],
        'Age_Symptomatic': selected_match['Age'].values[0],
        'Cervical curvature type_Symptomatic': selected_match['cervical curvature type'].values[0],
        'C7S_Symptomatic': selected_match['C7S'].values[0],
        'Propensity score_Symptomatic': selected_match['Propensity score'].values[0]
    })

    # Remove the matched sample from case_1 to ensure each sample is matched only once
    case_1 = case_1.drop(selected_match.index)

# Convert the matched results into a DataFrame
matched_df = pd.DataFrame(matched_results)

# Save the matched results
output_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905\PSM filter.xlsx"  # Replace with the actual path
matched_df.to_excel(output_path, index=False)
print(f"Matching results have been saved to {output_path}")
