import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# 1. **Read data**
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\C7 length.xlsx"  # Please replace with the actual file path
data = pd.read_excel(file_path)

# 2. **Correct column names (unified standard names)**
data.rename(columns={
    "性别,1女 0男": "Sex",
    "疾病分型：1、颈椎病；2、健康人群": "Symptom status",
    "颈椎曲度情况：1、正常；2、变直；3、上弓下直；4、下弓上直；5、曲度反弓（中间）": "cervical curvature type",
    "c7长度": "C7 length",  # Unified column name correction to ensure correct data column
    "C7S": "C7S"  # Add C7S column name correction
}, inplace=True)

print("Corrected column names: ", data.columns.tolist())  # **Check column names**

# 3. **Data preprocessing**
data.dropna(inplace=True)  # Remove missing values
data['Sex'] = data['Sex'].astype(int)
data['Age'] = data['Age'].astype(int)
data['Symptom status'] = data['Symptom status'].astype(int)
data['C7 length'] = data['C7 length'].astype(float)  # Ensure C7 length is numeric type
data['C7S'] = data['C7S'].astype(float)  # Ensure C7S is numeric type

# **Check for missing values**
print(f"Presence of missing values:\n{data.isnull().sum()}")

# 4. **Calculate Propensity Score (PS) based on "Age"**
predictors_age = ['Age']
X_age = data[predictors_age]
y = data['Symptom status']

# Standardize features
scaler = StandardScaler()
X_age_scaled = scaler.fit_transform(X_age)

# Use Logistic Regression to calculate propensity score
logit_age = LogisticRegression(max_iter=1000)  # Increase maximum number of iterations
logit_age.fit(X_age_scaled, y)
data['propensity_score_age'] = logit_age.predict_proba(X_age_scaled)[:, 1]

# **Ensure the propensity_score_age column is generated successfully**
print("Corrected column names (check propensity_score_age): ", data.columns.tolist())  # Ensure propensity_score_age column exists

# 5. **Calculate weighted matching based on "Age"**
# Calculate age-weighted matching weights
data['weight_age'] = data['propensity_score_age'] / (1 - data['propensity_score_age'])

# 6. **Calculate Propensity Score (PS) based on "C7 length"**
predictors_c7 = ['C7 length']
X_c7 = data[predictors_c7]

# Standardize features
X_c7_scaled = scaler.fit_transform(X_c7)

# **Check if the C7 length column is valid**
print(f"Basic statistics of C7 length column:\n{data['C7 length'].describe()}")

# Use Logistic Regression to calculate propensity score
logit_c7 = LogisticRegression(max_iter=1000)  # Increase maximum number of iterations
logit_c7.fit(X_c7_scaled, y)

# **Ensure the propensity_score_c7 column is generated correctly**
data['propensity_score_c7'] = logit_c7.predict_proba(X_c7_scaled)[:, 1]

# Check if propensity_score_c7 is generated successfully
print("Corrected column names (check propensity_score_c7): ", data.columns.tolist())  # Ensure propensity_score_c7 column exists
print(data[['Age', 'C7 length', 'propensity_score_c7']].head())  # Check sample data to confirm propensity_score_c7 is generated correctly

# 7. **Calculate weighted matching based on "C7 length"**
# Calculate C7 length-weighted matching weights
data['weight_c7'] = data['propensity_score_c7'] / (1 - data['propensity_score_c7'])

# Check weight distribution
print("weight_c7 description: ", data['weight_c7'].describe())

# 8. **Calculate weighted mean**
weighted_case_mean_c7 = np.sum(data[data['Symptom status'] == 1]['C7 length'] * data[data['Symptom status'] == 1]['weight_c7']) / np.sum(data[data['Symptom status'] == 1]['weight_c7'])
weighted_control_mean_c7 = np.sum(data[data['Symptom status'] == 2]['C7 length'] * data[data['Symptom status'] == 2]['weight_c7']) / np.sum(data[data['Symptom status'] == 2]['weight_c7'])

print(f"Weighted mean of C7 length in cervical spondylosis group: {weighted_case_mean_c7}")
print(f"Weighted mean of C7 length in healthy population group: {weighted_control_mean_c7}")

# 9. **Save weighted results**
output_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM length.xlsx"  # Please replace with the actual file path
data.to_excel(output_file, index=False)

print(f"✅ Weighted matching results have been saved to {output_file}")