import pandas as pd
import scipy.stats as stats
import os
from itertools import combinations

# Read Excel file
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\1万人的基线和数据.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\Table 1"
output_file = os.path.join(output_dir, "10k-(sy-asy)-age.xlsx")  # English output file name

# Automatically create output directory (to avoid errors if the directory does not exist)
try:
    os.makedirs(output_dir, exist_ok=True)
except PermissionError:
    print("Permission Error: Failed to create output directory, please check the folder read/write permissions!")
    exit(1)

# Read Excel data and rename columns (English translation strictly according to specified rules)
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom_status", "cervical_curvature_type", "C7S"]

# Define age grouping intervals
age_bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99]
age_labels = ["0-9 years", "10-19 years", "20-29 years", "30-39 years", "40-49 years", 
              "50-59 years", "60-69 years", "70-79 years", "80-89 years", "90-99 years"]

# Group by age
data["Age_Group"] = pd.cut(data["Age"], bins=age_bins, labels=age_labels, right=True)

# Define a function for statistical analysis
def perform_test(group1, group1_name, group2, group2_name):
    # Calculate descriptive statistics (mean, standard deviation, sample size) and format decimal places
    group1_mean = round(group1.mean(), 3) if not group1.empty else None
    group1_std = round(group1.std(), 3) if not group1.empty else None
    group1_size = group1.count()
    group2_mean = round(group2.mean(), 3) if not group2.empty else None
    group2_std = round(group2.std(), 3) if not group2.empty else None
    group2_size = group2.count()

    # Normality test: Replaced with D'Agostino-Pearson test (adapted for large samples, eliminating Shapiro-Wilk warnings)
    group1_normality_p = stats.normaltest(group1).pvalue if group1_size >= 8 else None  # normaltest requires n≥8
    group2_normality_p = stats.normaltest(group2).pvalue if group2_size >= 8 else None

    # Judge normality (p-value > 0.05 indicates normal distribution)
    group1_is_normal = "Yes" if (group1_normality_p is not None and group1_normality_p > 0.05) else "No"
    group2_is_normal = "Yes" if (group2_normality_p is not None and group2_normality_p > 0.05) else "No"

    # Select test method based on normality
    if group1_is_normal == "Yes" and group2_is_normal == "Yes":
        # Normal distribution: Independent Samples t-test
        test_stat, p_value = stats.ttest_ind(group1, group2) if not (group1.empty or group2.empty) else (None, None)
        test_method = "Independent Samples t-test"
    else:
        # Non-normal distribution: Mann-Whitney U test
        test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided') if not (group1.empty or group2.empty) else (None, None)
        test_method = "Mann-Whitney U test"

    # Format P-value (in line with the requirements of paper statistical reporting)
    if p_value is None:
        p_value_formatted = "N/A"
    elif p_value < 0.001:
        p_value_formatted = "P < 0.001"
    else:
        p_value_formatted = f"P = {round(p_value, 3)}"

    # Format test statistic
    test_stat_formatted = round(test_stat, 3) if test_stat is not None else "N/A"
    # Format normality P-value
    group1_normality_p_formatted = round(group1_normality_p, 3) if group1_normality_p is not None else "N/A"
    group2_normality_p_formatted = round(group2_normality_p, 3) if group2_normality_p is not None else "N/A"

    return {
        "Comparison": f"{group1_name} vs {group2_name}",
        "Test_Method": test_method,
        "P_Value": p_value_formatted,
        "Test_Statistic": test_stat_formatted,
        "Group1_Name": group1_name,
        "Group1_Mean": group1_mean,
        "Group1_Std": group1_std,
        "Group1_Sample_Size": group1_size,
        "Group1_Normality_P": group1_normality_p_formatted,
        "Group1_Is_Normal": group1_is_normal,
        "Group2_Name": group2_name,
        "Group2_Mean": group2_mean,
        "Group2_Std": group2_std,
        "Group2_Sample_Size": group2_size,
        "Group2_Normality_P": group2_normality_p_formatted,
        "Group2_Is_Normal": group2_is_normal,
    }

# Prepare list of comparison results
results = []

# 1. Differences between different age groups in the symptomatic group (original cervical spondylosis group)
symptomatic_group = data[data["Symptom_status"] == 1]  # Replace with specified group name
for comb in combinations(symptomatic_group["Age_Group"].dropna().unique(), 2):
    group1 = symptomatic_group[symptomatic_group["Age_Group"] == comb[0]]["C7S"]
    group2 = symptomatic_group[symptomatic_group["Age_Group"] == comb[1]]["C7S"]
    group1_name = f"Symptomatic group {comb[0]}"
    group2_name = f"Symptomatic group {comb[1]}"
    result = perform_test(group1, group1_name, group2, group2_name)
    results.append(result)

# 2. Differences between different age groups in the asymptomatic group (original healthy group)
asymptomatic_group = data[data["Symptom_status"] == 2]  # Replace with specified group name
for comb in combinations(asymptomatic_group["Age_Group"].dropna().unique(), 2):
    group1 = asymptomatic_group[asymptomatic_group["Age_Group"] == comb[0]]["C7S"]
    group2 = asymptomatic_group[asymptomatic_group["Age_Group"] == comb[1]]["C7S"]
    group1_name = f"Asymptomatic group {comb[0]}"
    group2_name = f"Asymptomatic group {comb[1]}"
    result = perform_test(group1, group1_name, group2, group2_name)
    results.append(result)

# 3. Differences between the symptomatic and asymptomatic groups in the same age group
for age_group in data["Age_Group"].dropna().unique():
    group1 = asymptomatic_group[asymptomatic_group["Age_Group"] == age_group]["C7S"]
    group2 = symptomatic_group[symptomatic_group["Age_Group"] == age_group]["C7S"]
    if not group1.empty and not group2.empty:
        group1_name = f"Asymptomatic group {age_group}"
        group2_name = f"Symptomatic group {age_group}"
        result = perform_test(group1, group1_name, group2, group2_name)
        results.append(result)

# Convert to DataFrame and export
try:
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_file, index=False)
    print(f"Statistical results have been saved to {output_file}")
except PermissionError:
    print("Permission Error: Failed to write to Excel file, please check if the file is occupied or the folder read/write permissions!")
except Exception as e:
    print(f"Failed to export file: {str(e)}")