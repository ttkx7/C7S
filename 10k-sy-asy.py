import pandas as pd
import scipy.stats as stats
import os

# ========== Option 1: File path/filename modification ==========
# Input file path (keep the original path, only ensure path format compatibility)
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\1万人的基线和数据.xlsx"
# Output directory (keep the original directory)
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\Table 1"
# Option 1: Output filename optimization (reflecting group naming)
output_file = os.path.join(output_dir, "10k-sy-asy.xlsx")

# Read Excel data and rename columns
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# ========== Group Name Replacement (Core Requirement) ==========
# Symptomatic group: Symptomatic group (Symptom status=1)
group1 = data[data["Symptom status"] == 1]["C7S"]  
# Asymptomatic group: Asymptomatic group (Symptom status=2)
group2 = data[data["Symptom status"] == 2]["C7S"]  

# Calculate descriptive statistics (mean, standard deviation, sample size)
group1_mean, group1_std, group1_size = group1.mean(), group1.std(), group1.count()
group2_mean, group2_std, group2_size = group2.mean(), group2.std(), group2.count()

# ========== Key Modification: Replace with normaltest (for large sample, eliminate Shapiro-Wilk warning) ==========
# normaltest returns: test statistic, p-value (p > 0.05 indicates normal distribution)
# Replace the original stats.shapiro() to adapt to large sample scenario N > 5000
group1_norm_stat, group1_normality_p = stats.normaltest(group1)
group2_norm_stat, group2_normality_p = stats.normaltest(group2)

# Check normality (p-value > 0.05 indicates normal distribution) — logic unchanged
group1_is_normal = group1_normality_p > 0.05
group2_is_normal = group2_normality_p > 0.05

# Choose test method based on normality — logic unchanged
if group1_is_normal and group2_is_normal:
    # Normal distribution: Independent T-test
    test_stat, p_value = stats.ttest_ind(group1, group2)
    test_method = "Independent T-test"
else:
    # Non-normal distribution: Mann-Whitney U test
    test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    test_method = "Mann-Whitney U Test"

# Format p-value — logic unchanged
if p_value < 0.001:
    p_value_formatted = "P < 0.001"
else:
    p_value_formatted = f"P = {p_value:.3f}"

# ========== Update Group Names in Result Table ==========
results = {
    "Group": ["Symptomatic group", "Asymptomatic group"],  # Core replacement
    "Mean": [group1_mean, group2_mean],
    "Standard Deviation": [group1_std, group2_std],
    "Sample Size": [group1_size, group2_size],
    "Normality P-value": [group1_normality_p, group2_normality_p],
    "Is Normal Distribution": [group1_is_normal, group2_is_normal],
}

summary_df = pd.DataFrame(results)

# Add statistical test results — logic unchanged
summary_df.loc[len(summary_df)] = ["", "", "", "", "", ""]
summary_df.loc[len(summary_df)] = ["Test Method", test_method, "", "", "", ""]
summary_df.loc[len(summary_df)] = ["P-value", p_value_formatted, "", "", "", ""]

# Output Excel file
summary_df.to_excel(output_file, index=False)

print(f"Statistical results have been saved to {output_file}")
