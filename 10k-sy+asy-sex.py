import pandas as pd
import scipy.stats as stats
import os

# ========== Option 1: File path/filename modification ==========
# Input file path (keep the original path, only ensure path format compatibility)
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\1万人的基线和数据.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\Table 1"
# Option 1: Output filename optimization (reflecting statistical logic)
output_file = os.path.join(output_dir, "10k-sy+asy-sex.xlsx")

# Automatically create output directory (to avoid errors when the directory does not exist)
os.makedirs(output_dir, exist_ok=True)

# Read Excel data and rename columns to the specified English format
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# Define statistical analysis function (keep the comments in Chinese, core variables in English)
def perform_test(group1, group1_name, group2, group2_name):
    # Calculate descriptive statistics (mean, standard deviation, sample size)
    group1_mean, group1_std, group1_size = group1.mean(), group1.std(), group1.count()
    group2_mean, group2_std, group2_size = group2.mean(), group2.std(), group2.count()

    # Normality test: replace with normaltest (suitable for large samples, replacing Shapiro-Wilk)
    # normaltest is based on skewness and kurtosis, suitable for N>5000 scenarios, no accuracy warnings
    group1_norm_stat, group1_normality_p = stats.normaltest(group1)
    group2_norm_stat, group2_normality_p = stats.normaltest(group2)

    # Check normality (p-value > 0.05 indicates normal distribution)
    group1_is_normal = group1_normality_p > 0.05
    group2_is_normal = group2_normality_p > 0.05

    # Choose test method based on normality
    if group1_is_normal and group2_is_normal:
        # Normal distribution: Independent samples t-test
        test_stat, p_value = stats.ttest_ind(group1, group2)
        test_method = "Independent Samples t-test"
    else:
        # Non-normal distribution: Mann-Whitney U test
        test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_method = "Mann-Whitney U test"

    # Format p-value
    if p_value < 0.001:
        p_value_formatted = "P < 0.001"
    else:
        p_value_formatted = f"P = {p_value:.3f}"

    # Return results (fields in English)
    return {
        "Comparison": f"{group1_name} vs {group2_name}",
        "Test_Method": test_method,
        "P_Value": p_value_formatted,
        "Test_Statistic": round(test_stat, 4),
        "Group1_Name": group1_name,
        "Group1_Mean": round(group1_mean, 2),
        "Group1_Std": round(group1_std, 2),
        "Group1_Sample_Size": group1_size,
        "Group1_Normality_P": round(group1_normality_p, 4),
        "Group1_Is_Normal": "Yes" if group1_is_normal else "No",
        "Group2_Name": group2_name,
        "Group2_Mean": round(group2_mean, 2),
        "Group2_Std": round(group2_std, 2),
        "Group2_Sample_Size": group2_size,
        "Group2_Normality_P": round(group2_normality_p, 4),
        "Group2_Is_Normal": "Yes" if group2_is_normal else "No",
    }

# Prepare a list to store the results
results = []

# 1. Male vs Female in the symptomatic group (group names in English as per your requirement)
male_cervical = data[(data["Symptom status"] == 1) & (data["Sex"] == 0)]["C7S"]
female_cervical = data[(data["Symptom status"] == 1) & (data["Sex"] == 1)]["C7S"]
results.append(perform_test(male_cervical, "Male - Symptomatic group", female_cervical, "Female - Symptomatic group"))

# 2. Male vs Female in the asymptomatic group
male_healthy = data[(data["Symptom status"] == 2) & (data["Sex"] == 0)]["C7S"]
female_healthy = data[(data["Symptom status"] == 2) & (data["Sex"] == 1)]["C7S"]
results.append(perform_test(male_healthy, "Male - Asymptomatic group", female_healthy, "Female - Asymptomatic group"))

# 3. Healthy male vs symptomatic male
results.append(perform_test(male_healthy, "Male - Asymptomatic group", male_cervical, "Male - Symptomatic group"))

# 4. Healthy female vs symptomatic female
results.append(perform_test(female_healthy, "Female - Asymptomatic group", female_cervical, "Female - Symptomatic group"))

# Convert to DataFrame and output
results_df = pd.DataFrame(results)

# Catch permission error and provide Chinese message
try:
    results_df.to_excel(output_file, index=False)
    print(f"✅ Statistical results have been saved to: {output_file}")
except PermissionError:
    print(f"❌ Permission error! Please close the file: {output_file} and rerun the code")
except Exception as e:
    print(f"❌ Error writing file: {str(e)}")
