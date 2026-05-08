import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# 1. **Load data**
file_path = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\1万人的基线和数据.xlsx"  # Please replace with actual file path
data = pd.read_excel(file_path)

# 2. **Rename columns**
data.rename(columns={
    "性别,1女 0男": "Sex",
    "疾病分型：1、颈椎病；2、健康人群": "Symptom status",
    "颈椎曲度情况：1、正常；2、变直；3、上弓下直；4、下弓上直；5、曲度反弓（中间）": "Cervical curvature type"
}, inplace=True)

print("Modified column names:", data.columns.tolist())  # **Check column names**

# Ensure data column names match
expected_columns = ['No', 'Sex', 'Age', 'Symptom status', 'cervical curvature type', 'C7S']
if not all(col in data.columns for col in expected_columns):
    raise ValueError("Column names do not match, please check the column names!")

# 3. **Data preprocessing**
data.dropna(inplace=True)  # Remove missing values
data['Sex'] = data['Sex'].astype(int)
data['Age'] = data['Age'].astype(int)
data['Symptom status'] = data['Symptom status'].astype(int)

# 4. **Calculate propensity score (PS)**
# Baseline features
predictors = ['Sex', 'Age']
X = data[predictors]
y = data['Symptom status']

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Use Logistic Regression to calculate propensity scores
logit = LogisticRegression()
logit.fit(X_scaled, y)
data['Propensity score'] = logit.predict_proba(X_scaled)[:, 1]

# 5. **Weighted calculation**
# Group by Symptom status
case = data[data['Symptom status'] == 1].copy()  # Symptomatic group
control = data[data['Symptom status'] == 2].copy()  # Asymptomatic group

# Calculate matching weights
# Asymptomatic group weights
control['Weight'] = control['Propensity score'] / (1 - control['Propensity score'])
# Symptomatic group weights
case['Weight'] = (1 - case['Propensity score']) / case['Propensity score']

# Check weight distribution
print("Symptomatic group weight description:", case['Weight'].describe())
print("Asymptomatic group weight description:", control['Weight'].describe())

# 6. **Merge weighted data**
# Combine both groups back together
weighted_data = pd.concat([case, control], axis=0)

# 7. **Check weighted means and group differences**
# Calculate weighted means
weighted_case_mean = np.sum(case['C7S'] * case['Weight']) / np.sum(case['Weight'])
weighted_control_mean = np.sum(control['C7S'] * control['Weight']) / np.sum(control['Weight'])

print(f"Symptomatic group weighted mean: {weighted_case_mean}")
print(f"Asymptomatic group weighted mean: {weighted_control_mean}")

# 8. **Save weighted results**
output_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905\PSM.xlsx"  # Please replace with actual file path
weighted_data.to_excel(output_file, index=False)

print(f"✅ Weighted matching results have been saved to {output_file}")
