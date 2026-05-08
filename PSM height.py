import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# 1. **Read data**
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\C7 height.xlsx"  # Please replace with the actual file path
data = pd.read_excel(file_path)

# 2. **Correct column names (unified standard names)**
data.rename(columns={
    "Gender, 1 for female 0 for male": "Sex",
    "Disease classification: 1. Cervical spondylosis; 2. Healthy population": "Symptom status",
    "Cervical curvature status: 1. Normal; 2. Straightened; 3. Upper arch lower straight; 4. Lower arch upper straight; 5. Curvature reversal (middle)": "cervical curvature type",
    "C7 length": "C7 height",
    "C7S": "C7S"
}, inplace=True)

print("Corrected column names: ", data.columns.tolist())  # **Check column names**

# 3. **Data preprocessing**
data.dropna(inplace=True)  # Remove missing values
data['Sex'] = data['Sex'].astype(int)  # 统一为Sex列
data['Age'] = data['Age'].astype(int)
data['Symptom status'] = data['Symptom status'].astype(int)  # 统一为Symptom status列
data['C7 height'] = data['C7 height'].astype(float)  # 统一为C7 height列
data['C7S'] = data['C7S'].astype(float)

# **Check for missing values**
print(f"Presence of missing values:\n{data.isnull().sum()}")

# 4. **Calculate Propensity Score (PS) based on "Age"**
predictors_age = ['Age']
X_age = data[predictors_age]
y = data['Symptom status']  # 替换为统一的Symptom status列

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

# 6. **Calculate Propensity Score (PS) based on "C7 height"**
predictors_c7 = ['C7 height']  # 统一为C7 height列
X_c7 = data[predictors_c7]

# Standardize features
X_c7_scaled = scaler.fit_transform(X_c7)

# **Check if the C7 height column is valid**
print(f"Basic statistics of C7 height column:\n{data['C7 height'].describe()}")

# Use Logistic Regression to calculate propensity score
logit_c7 = LogisticRegression(max_iter=1000)  # Increase maximum number of iterations
logit_c7.fit(X_c7_scaled, y)

# **Ensure the propensity_score_c7 column is generated correctly**
data['propensity_score_c7'] = logit_c7.predict_proba(X_c7_scaled)[:, 1]

# Check if propensity_score_c7 is generated successfully
print("Corrected column names (check propensity_score_c7): ", data.columns.tolist())  # Ensure propensity_score_c7 column exists
print(data[['Age', 'C7 height', 'propensity_score_c7']].head())  # 列名统一为C7 height

# 7. **Calculate weighted matching based on "C7 height"**
# Calculate C7 height-weighted matching weights
data['weight_c7'] = data['propensity_score_c7'] / (1 - data['propensity_score_c7'])

# Check weight distribution
print("weight_c7 description: ", data['weight_c7'].describe())

# 8. **Calculate weighted mean**
# 统一使用Symptom status和C7 height列名
weighted_case_mean_c7 = np.sum(data[data['Symptom status'] == 1]['C7 height'] * data[data['Symptom status'] == 1]['weight_c7']) / np.sum(data[data['Symptom status'] == 1]['weight_c7'])
weighted_control_mean_c7 = np.sum(data[data['Symptom status'] == 2]['C7 height'] * data[data['Symptom status'] == 2]['weight_c7']) / np.sum(data[data['Symptom status'] == 2]['weight_c7'])

print(f"Weighted mean of C7 height in cervical spondylosis group: {weighted_case_mean_c7}")
print(f"Weighted mean of C7 height in healthy population group: {weighted_control_mean_c7}")

# 9. **Save weighted results**
output_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM height.xlsx"  # Please replace with the actual file path
data.to_excel(output_file, index=False)

print(f"✅ Weighted matching results have been saved to {output_file}")