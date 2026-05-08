import pandas as pd
import scipy.stats as stats
import os

# Read Excel file
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\加权匹配结果合并C7S（PSM-905人-表2采用的数据）.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905"
output_file = os.path.join(output_dir, "905-(sy-asy)-cate age.xlsx")  # Optimize file name with English

# Read Excel data and rename columns (replace with English column names to match your Excel header)
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]  

# Define two age grouping methods (Core: replace "岁" with Y; Age group 2 uses standard English without "age" prefix)
age_bins_1 = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99]
age_labels_1 = ["0-9 Y", "10-19 Y", "20-29 Y", "30-39 Y", "40-49 Y", "50-59 Y", "60-69 Y", "70-79 Y", "80-89 Y", "90-99 Y"]
data["Age group 1"] = pd.cut(data["Age"], bins=age_bins_1, labels=age_labels_1, right=True)

age_bins_2 = [0, 14, 24, 34, 59, float('inf')]
age_labels_2 = ["Children", "Adolescents", "Young adults", "Middle-aged adults", "Elderly"]  # Standard English without "age" prefix
data["Age group 2"] = pd.cut(data["Age"], bins=age_bins_2, labels=age_labels_2, right=True)

# Define a function for statistical analysis (Core modification: DAP normality test + English text replacement)
def perform_test(group1, group1_name, group2, group2_name):
    if len(group1) < 3 or len(group2) < 3:
        return {
            "Comparison": f"{group1_name} vs {group2_name}",
            "Test method": "Skipped",
            "P-value": "Insufficient sample size",
            "Test statistic": "No data",
            "Group 1 name": group1_name,
            "Group 1 sample size": len(group1),
            "Group 1 mean": "No data",
            "Group 1 standard deviation": "No data",
            "Group 1 normality P-value": "No data",
            "Group 1 is normal": "No data",
            "Group 2 name": group2_name,
            "Group 2 sample size": len(group2),
            "Group 2 mean": "No data",
            "Group 2 standard deviation": "No data",
            "Group 2 normality P-value": "No data",
            "Group 2 is normal": "No data",
        }

    # Calculate descriptive statistics (mean and standard deviation)
    group1_mean, group1_std = round(group1.mean(), 2), round(group1.std(), 2)
    group2_mean, group2_std = round(group2.mean(), 2), round(group2.std(), 2)

    # Replace normality test with DAP method (D'Agostino-Pearson), adapted for large samples; set to "No data" when sample size < 8
    # Normality test for Group 1
    if len(group1) >= 8:
        group1_normality_p = round(stats.normaltest(group1).pvalue, 3)  # DAP test
        group1_is_normal = "Yes" if group1_normality_p > 0.05 else "No"
    else:
        group1_normality_p = "No data"
        group1_is_normal = "No data"
    
    # Normality test for Group 2
    if len(group2) >= 8:
        group2_normality_p = round(stats.normaltest(group2).pvalue, 3)  # DAP test
        group2_is_normal = "Yes" if group2_normality_p > 0.05 else "No"
    else:
        group2_normality_p = "No data"
        group2_is_normal = "No data"

    # Select test method based on normality
    if group1_is_normal == "Yes" and group2_is_normal == "Yes":
        test_stat, p_value = stats.ttest_ind(group1, group2)
        test_method = "Independent samples t-test"
    else:
        test_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_method = "Mann-Whitney U test"

    # Format P-value
    p_value_formatted = "P < 0.001" if p_value < 0.001 else f"P = {round(p_value, 3)}"

    return {
        "Comparison": f"{group1_name} vs {group2_name}",
        "Test method": test_method,
        "P-value": p_value_formatted,
        "Test statistic": round(test_stat, 3),
        "Group 1 name": group1_name,
        "Group 1 sample size": len(group1),
        "Group 1 mean": group1_mean,
        "Group 1 standard deviation": group1_std,
        "Group 1 normality P-value": group1_normality_p,
        "Group 1 is normal": group1_is_normal,
        "Group 2 name": group2_name,
        "Group 2 sample size": len(group2),
        "Group 2 mean": group2_mean,
        "Group 2 standard deviation": group2_std,
        "Group 2 normality P-value": group2_normality_p,
        "Group 2 is normal": group2_is_normal,
    }

# Prepare list for comparison results
results = []

# Differences between different age groups in the symptomatic group (two age grouping methods, age labels without "age" prefix)
for age_group_col, age_labels in [("Age group 1", age_labels_1), ("Age group 2", age_labels_2)]:
    for disease_group in [1]:  # Symptomatic group (cervical spondylosis)
        disease_data = data[data["Symptom status"] == disease_group]
        for age1 in age_labels:
            for age2 in age_labels:
                if age1 >= age2:
                    continue
                group1 = disease_data[disease_data[age_group_col] == age1]["C7S"]
                group2 = disease_data[disease_data[age_group_col] == age2]["C7S"]
                # Core replacement: Cervical spondylosis group → Symptomatic
                result = perform_test(group1, f"Symptomatic_{age1}", group2, f"Symptomatic_{age2}")
                results.append(result)

# Differences between different age groups in the asymptomatic group (two age grouping methods, age labels without "age" prefix)
for age_group_col, age_labels in [("Age group 1", age_labels_1), ("Age group 2", age_labels_2)]:
    for disease_group in [2]:  # Asymptomatic group (healthy)
        disease_data = data[data["Symptom status"] == disease_group]
        for age1 in age_labels:
            for age2 in age_labels:
                if age1 >= age2:
                    continue
                group1 = disease_data[disease_data[age_group_col] == age1]["C7S"]
                group2 = disease_data[disease_data[age_group_col] == age2]["C7S"]
                # Core replacement: Healthy group → Asymptomatic
                result = perform_test(group1, f"Asymptomatic_{age1}", group2, f"Asymptomatic_{age2}")
                results.append(result)

# Differences between symptomatic and asymptomatic groups in the same age group (two age grouping methods, age labels without "age" prefix)
for age_group_col, age_labels in [("Age group 1", age_labels_1), ("Age group 2", age_labels_2)]:
    for age in age_labels:
        group_neck = data[(data["Symptom status"] == 1) & (data[age_group_col] == age)]["C7S"]
        group_healthy = data[(data["Symptom status"] == 2) & (data[age_group_col] == age)]["C7S"]
        # Core replacement: Cervical spondylosis group → Symptomatic; Healthy group → Asymptomatic
        result = perform_test(group1=group_neck, group1_name=f"Symptomatic_{age}", group2=group_healthy, group2_name=f"Asymptomatic_{age}")
        results.append(result)

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Export to Excel file
results_df.to_excel(output_file, index=False)
print(f"Statistical results have been saved to {output_file}")