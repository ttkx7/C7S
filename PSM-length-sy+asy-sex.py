import pandas as pd
import numpy as np
import scipy.stats as stats
import os

# ========== File path configuration (consistent with 905 code) ==========
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height\PSM length filter combine - 6 columns.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM length&height"
output_file = os.path.join(output_dir, "PSM-length-sy+asy-sex.xlsx")

# Automatically create output directory (same as 905 code)
os.makedirs(output_dir, exist_ok=True)

# Read Excel data and rename columns (consistent with 905 code style)
data = pd.read_excel(input_file)
data.columns = ["Sex", "Age", "Disease_Type", "Cervical_Curvature_Type", "C7_Length", "C7S"]

# Define statistical analysis function (100% align with 905 code, use DAP test)
def perform_test(group1, group1_name, group2, group2_name):
    # Calculate sample size (same as 905 code)
    group1_size, group2_size = len(group1), len(group2)

    # Calculate descriptive statistics (mean, standard deviation)
    group1_mean, group1_std = group1.mean(), group1.std()
    group2_mean, group2_std = group2.mean(), group2.std()

    # ========== Core modification: DAP test (normaltest) same as 905 code ==========
    # Normality test: D'Agostino-Pearson test (suitable for large samples, same as 905)
    group1_norm_stat, group1_normality_p = stats.normaltest(group1)
    group2_norm_stat, group2_normality_p = stats.normaltest(group2)

    # Check normality (p-value > 0.05 = normal distribution, same logic as 905)
    group1_is_normal = group1_normality_p > 0.05
    group2_is_normal = group2_normality_p > 0.05

    # Choose test method (same as 905 code)
    if group1_is_normal and group2_is_normal:
        test_stat, p_value = stats.ttest_ind(group1, group2)
        test_method = "Independent Samples t-test"
    else:
        test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_method = "Mann-Whitney U test"

    # Format p-value (same as 905 code)
    if p_value < 0.001:
        p_value_formatted = "P < 0.001"
    else:
        p_value_formatted = f"P = {p_value:.3f}"

    # Return results (all fields same as 905 code)
    return {
        "Comparison": f"{group1_name} vs {group2_name}",
        "Test_Method": test_method,
        "P_Value": p_value_formatted,
        "Test_Statistic": round(test_stat, 4),
        "Group1_Name": group1_name,
        "Group1_Sample_Size": group1_size,
        "Group1_Mean": round(group1_mean, 2),
        "Group1_Std": round(group1_std, 2),
        "Group1_Normality_P": round(group1_normality_p, 4),
        "Group1_Is_Normal": "Yes" if group1_is_normal else "No",
        "Group2_Name": group2_name,
        "Group2_Sample_Size": group2_size,
        "Group2_Mean": round(group2_mean, 2),
        "Group2_Std": round(group2_std, 2),
        "Group2_Normality_P": round(group2_normality_p, 4),
        "Group2_Is_Normal": "Yes" if group2_is_normal else "No",
    }

# Prepare results list (same as 905 code structure)
results = []

# 1. Male vs Female in Symptomatic group (Disease_Type=1)
male_symptomatic = data[(data["Disease_Type"] == 1) & (data["Sex"] == 0)]["C7S"]
female_symptomatic = data[(data["Disease_Type"] == 1) & (data["Sex"] == 1)]["C7S"]
results.append(perform_test(male_symptomatic, "Male - Symptomatic group", female_symptomatic, "Female - Symptomatic group"))

# 2. Male vs Female in Asymptomatic group (Disease_Type=2)
male_asymptomatic = data[(data["Disease_Type"] == 2) & (data["Sex"] == 0)]["C7S"]
female_asymptomatic = data[(data["Disease_Type"] == 2) & (data["Sex"] == 1)]["C7S"]
results.append(perform_test(male_asymptomatic, "Male - Asymptomatic group", female_asymptomatic, "Female - Asymptomatic group"))

# 3. Asymptomatic Male vs Symptomatic Male
results.append(perform_test(male_asymptomatic, "Male - Asymptomatic group", male_symptomatic, "Male - Symptomatic group"))

# 4. Asymptomatic Female vs Symptomatic Female
results.append(perform_test(female_asymptomatic, "Female - Asymptomatic group", female_symptomatic, "Female - Symptomatic group"))

# Convert to DataFrame and output (same as 905 code)
results_df = pd.DataFrame(results)

# Error handling (same as 905 code, English prompt)
try:
    results_df.to_excel(output_file, index=False)
    print(f"✅ Statistical results have been saved to: {output_file}")
except PermissionError:
    print(f"❌ Permission error! Please close the file: {output_file} and rerun the code")
except Exception as e:
    print(f"❌ Error writing file: {str(e)}")