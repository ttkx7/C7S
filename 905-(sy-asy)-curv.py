import pandas as pd
import scipy.stats as stats
import os
from itertools import combinations

# Read Excel file
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\加权匹配结果合并C7S（PSM-905人-表2采用的数据）.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905"  # Add root path for E drive (original code missed E:)
output_file = os.path.join(output_dir, "905-(sy-asy)-curv.xlsx")  # Modify file name

# Read Excel data and rename columns (replace with English)
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# Define mapping dictionary: number to English name
# Symptom status: 1 = Cervical Spondylosis Group (Symptomatic), 2 = Healthy Group (Asymptomatic)
symptom_mapping = {1: "Symptomatic", 2: "Asymptomatic"}
# Cervical curvature type: 1 = Lordotic, 2 = Straight, 3 = Sigmoid1, 4 = Sigmoid2, 5 = Kyphotic
curvature_mapping = {1: "Lordotic", 2: "Straight", 3: "Sigmoid1", 4: "Sigmoid2", 5: "Kyphotic"}

# Define a function for statistical analysis
def perform_test(group1, group1_name, group2, group2_name):
    # Calculate descriptive statistics (mean, standard deviation, sample size)
    group1_mean = group1.mean() if not group1.empty else "No data"
    group1_std = group1.std() if not group1.empty else "No data"
    group1_size = group1.count() if not group1.empty else "No data"
    group2_mean = group2.mean() if not group2.empty else "No data"
    group2_std = group2.std() if not group2.empty else "No data"
    group2_size = group2.count() if not group2.empty else "No data"

    # Normality test: Replace with D'Agostino-Pearson (DAP) method (requires sample size ≥8)
    # Handle situations with insufficient sample size to avoid errors
    if len(group1) >= 8:
        group1_normality_stat, group1_normality_p = stats.normaltest(group1)
    else:
        group1_normality_p = "No data"
        group1_normality_stat = "No data"
    
    if len(group2) >= 8:
        group2_normality_stat, group2_normality_p = stats.normaltest(group2)
    else:
        group2_normality_p = "No data"
        group2_normality_stat = "No data"

    # Determine normality (p-value > 0.05 indicates normal distribution; mark as "No data" if no data)
    if isinstance(group1_normality_p, (int, float)):
        group1_is_normal = "Yes" if group1_normality_p > 0.05 else "No"
    else:
        group1_is_normal = "No data"
    
    if isinstance(group2_normality_p, (int, float)):
        group2_is_normal = "Yes" if group2_normality_p > 0.05 else "No"
    else:
        group2_is_normal = "No data"

    # Choose the test method based on normality
    if group1_is_normal == "Yes" and group2_is_normal == "Yes":
        # Normal distribution: Independent Samples T-test
        test_stat, p_value = stats.ttest_ind(group1, group2) if not (group1.empty or group2.empty) else ("No data", "No data")
        test_method = "Independent Samples T-test"
    else:
        # Non-normal distribution: Mann-Whitney U test
        test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided') if not (group1.empty or group2.empty) else ("No data", "No data")
        test_method = "Mann-Whitney U test"

    # Format P-value
    if isinstance(p_value, (int, float)):
        if p_value < 0.001:
            p_value_formatted = "P < 0.001"
        else:
            p_value_formatted = f"P = {p_value:.3f}"
    else:
        p_value_formatted = "No data"

    return {
        "Comparison": f"{group1_name} vs {group2_name}",
        "Test Method": test_method,
        "P Value": p_value_formatted,
        "Test Statistic": test_stat,
        "Group 1 Name": group1_name,
        "Group 1 Mean (C7S)": group1_mean,
        "Group 1 Std (C7S)": group1_std,
        "Group 1 Sample Size": group1_size,
        "Group 1 Normality P Value (DAP)": group1_normality_p,
        "Group 1 Is Normal": group1_is_normal,
        "Group 2 Name": group2_name,
        "Group 2 Mean (C7S)": group2_mean,
        "Group 2 Std (C7S)": group2_std,
        "Group 2 Sample Size": group2_size,
        "Group 2 Normality P Value (DAP)": group2_normality_p,
        "Group 2 Is Normal": group2_is_normal,
    }

# Prepare comparison results list
results = []

# 1. Differences between different cervical curvature types in the Cervical Spondylosis Group (Symptomatic)
symptomatic_group = data[data["Symptom status"] == 1]
for comb in combinations(symptomatic_group["cervical curvature type"].unique(), 2):
    curv1 = curvature_mapping[comb[0]]
    curv2 = curvature_mapping[comb[1]]
    group1 = symptomatic_group[symptomatic_group["cervical curvature type"] == comb[0]]["C7S"]
    group2 = symptomatic_group[symptomatic_group["cervical curvature type"] == comb[1]]["C7S"]
    group1_name = f"Symptomatic {curv1}"  # No extra prefix
    group2_name = f"Symptomatic {curv2}"  # No extra prefix
    result = perform_test(group1, group1_name, group2, group2_name)
    results.append(result)

# 2. Differences between different cervical curvature types in the Healthy Group (Asymptomatic)
asymptomatic_group = data[data["Symptom status"] == 2]
for comb in combinations(asymptomatic_group["cervical curvature type"].unique(), 2):
    curv1 = curvature_mapping[comb[0]]
    curv2 = curvature_mapping[comb[1]]
    group1 = asymptomatic_group[asymptomatic_group["cervical curvature type"] == comb[0]]["C7S"]
    group2 = asymptomatic_group[asymptomatic_group["cervical curvature type"] == comb[1]]["C7S"]
    group1_name = f"Asymptomatic {curv1}"  # No extra prefix
    group2_name = f"Asymptomatic {curv2}"  # No extra prefix
    result = perform_test(group1, group1_name, group2, group2_name)
    results.append(result)

# 3. Differences between the Healthy Group and Cervical Spondylosis Group for the same cervical curvature types
for curve_num in data["cervical curvature type"].unique():
    curv_name = curvature_mapping[curve_num]
    group1 = asymptomatic_group[asymptomatic_group["cervical curvature type"] == curve_num]["C7S"]
    group2 = symptomatic_group[symptomatic_group["cervical curvature type"] == curve_num]["C7S"]
    if not group1.empty and not group2.empty:
        group1_name = f"Asymptomatic {curv_name}"  # No extra prefix
        group2_name = f"Symptomatic {curv_name}"   # No extra prefix
        result = perform_test(group1, group1_name, group2, group2_name)
        results.append(result)

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Process age units (replace "岁" with "Y", for example, 0-9岁 → 0-9 Y)
# Iterate through all columns and replace "岁" in the content (if there are age ranges in the data)
for col in results_df.columns:
    if results_df[col].dtype == "object":
        # Key modification: removed na=False parameter (older version of Pandas does not support this)
        results_df[col] = results_df[col].str.replace("岁", "Y")

# Output the Excel file
results_df.to_excel(output_file, index=False)

print(f"Statistical results saved to {output_file}")
