import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

# Read data
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM height.xlsx"  # Please replace with your file path
data = pd.read_excel(file_path)

# Check if column names meet expectations
expected_columns = ['No', 'Sex', 'Age', 'Symptom status', 'cervical curvature type', 'C7 height', 'C7S', 'propensity_score_age', 'weight_age', 'propensity_score_c7', 'weight_c7']
if not all(col in data.columns for col in expected_columns):
    raise ValueError("Data column names do not match, please check the input file!")

# Convert the data type of the C7S column to float
data['C7S'] = data['C7S'].astype(float)

# Create a list to store matching results
matched_results = []

# Iterate over data of different symptom statuses
for disease_type in [1, 2]:  # 1 represents Cervical spondylosis group, 2 represents Healthy population group
    case_data = data[data['Symptom status'] == disease_type].copy()

    # First filter male and female samples based on propensity_score_c7 and C7 height error of ±0.1
    for idx_male, row_male in case_data[case_data['Sex'] == 0].iterrows():  # Iterate over male samples
        print(f"Processing male sample {row_male['No']} - propensity_score_c7: {row_male['propensity_score_c7']}, C7 height: {row_male['C7 height']}")  # Debug output
        # Filter eligible female samples based on propensity_score_c7 and C7 height error of ±0.1
        female_group_for_matching = case_data[(case_data['Sex'] == 1) & 
                                               (np.abs(case_data['propensity_score_c7'] - row_male['propensity_score_c7']) <= 0.1) & 
                                               (np.abs(case_data['C7 height'] - row_male['C7 height']) <= 0.1)]
        
        print(f"Number of filtered female samples: {len(female_group_for_matching)}")  # Debug output

        # If eligible female samples are found, perform one-to-one matching based on propensity_score_age
        for idx_female, row_female in female_group_for_matching.iterrows():
            # Calculate the propensity_score_age gap between the two
            age_distance = np.abs(row_male['propensity_score_age'] - row_female['propensity_score_age'])
            
            # Use nearest neighbor matching (based on propensity_score_age)
            if age_distance == np.min(age_distance):
                selected_match = row_female

                # Store the matching results
                matched_results.append({
                    'No_Male_c7': row_male['No'],  # Male sample (替换Sort为No)
                    'Sex_Male_c7': row_male['Sex'],
                    'Age_Male_c7': row_male['Age'],
                    'Symptom_status_Male_c7': row_male['Symptom status'],  # Add male symptom status
                    'Cervical_curvature_type_Male_c7': row_male['cervical curvature type'],
                    'C7_height_Male_c7': row_male['C7 height'],  # Changed to C7 height
                    'C7S_Male_c7': row_male['C7S'],  # Add C7S column
                    'Propensity_score_age_Male_c7': row_male['propensity_score_age'],
                    'Propensity_score_c7_Male': row_male['propensity_score_c7'],
                    'No_Female': selected_match['No'],  # Female sample (替换Sort为No)
                    'Sex_Female_c7': selected_match['Sex'],
                    'Age_Female_c7': selected_match['Age'],
                    'Symptom_status_Female_c7': selected_match['Symptom status'],                    
                    'Cervical_curvature_type_Female_c7': selected_match['cervical curvature type'],
                    'C7_height_Female_c7': selected_match['C7 height'],  # Changed to C7 height
                    'C7S_Female_c7': selected_match['C7S'],  # Add C7S column
                    'Propensity_score_age_Female_c7': selected_match['propensity_score_age'],
                    'Propensity_score_c7_Female': selected_match['propensity_score_c7']
                })

                # Remove matched samples from male and female groups to ensure each sample is matched only once
                case_data = case_data.drop(row_male.name)  # Remove the currently matched male sample
                case_data = case_data.drop(selected_match.name)  # Remove the currently matched female sample

                # End matching for the current male sample to ensure only one match
                break  # Exit the loop, only match once

# Convert matching results to DataFrame
matched_df = pd.DataFrame(matched_results)

# Save matching results
output_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM height filter.xlsx"  # Please replace with the path to save the file
matched_df.to_excel(output_path, index=False)

print(f"Matching results have been saved to {output_path}")