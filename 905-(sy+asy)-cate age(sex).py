import pandas as pd
import scipy.stats as stats
import os

# Read Excel file
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\加权匹配结果合并C7S（PSM-905人-表2采用的数据）.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905"
output_file = os.path.join(output_dir, "905-(sy+asy)-cate age(sex).xlsx")  # Modify file name

# Read Excel data and rename columns (replace with English column names)
data = pd.read_excel(input_file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# Define mapping from numeric symptom status to English labels (1=Symptomatic, 2=Asymptomatic)
symptom_mapping = {
    1: "Symptomatic",  # Symptomatic
    2: "Asymptomatic"  # Asymptomatic
}

# Define new age groups (standard English labels, no numeric intervals)
age_bins = [0, 14, 24, 34, 59, float('inf')]
age_labels = ["Children", "Adolescents", "Young adults", "Middle-aged adults", "Elderly"]
data["Age group"] = pd.cut(data["Age"], bins=age_bins, labels=age_labels, right=True)

# Define a statistical analysis function that selects ANOVA or Kruskal-Wallis test based on normality
# Replace normality test with D'Agostino-Pearson (DAP) method
def perform_adaptive_analysis(groups, labels, subgroup_info):
    if any(len(group) < 3 for group in groups):
        skip_info = {label: len(group) for label, group in zip(labels, groups) if len(group) < 3}
        return {
            "Subgroup condition": subgroup_info,
            "Comparison": " vs ".join(labels),
            "Test method": "Skipped",
            "P-value": "Insufficient sample size",
            "Test statistic": "N/A",
            "Group information": f"{', '.join([f'{label} (n={len(group)})' for label, group in zip(labels, groups)])}",
            "Descriptive statistics": f"Insufficient sample size: {skip_info}"
        }

    # Check normality of each group (replaced with DAP method, which requires sample size ≥ 8)
    normality = []
    for group in groups:
        if len(group) < 8:  # D'Agostino-Pearson test requires at least 8 samples; insufficient sample size is considered non-normal
            normality.append(False)
        else:
            _, dap_p = stats.normaltest(group)  # D'Agostino-Pearson normality test
            normality.append(dap_p > 0.05)

    # Levene's test for homogeneity of variance
    levene_stat, levene_p = stats.levene(*groups)

    # Calculate descriptive statistics
    descriptive_stats = [
        f"{label}: n={len(group)}, mean={group.mean():.2f}, sd={group.std():.2f}"
        for label, group in zip(labels, groups)
    ]

    if all(normality) and levene_p > 0.05:
        # Use one-way ANOVA
        stat, p_value = stats.f_oneway(*groups)
        test_method = "One-way ANOVA"
        test_stat = stat
    else:
        # Use Kruskal-Wallis test
        stat, p_value = stats.kruskal(*groups)
        test_method = "Kruskal-Wallis test"
        test_stat = stat

    # Format P-value
    p_value_formatted = "P < 0.001" if p_value < 0.001 else f"P = {p_value:.3f}"

    return {
        "Subgroup condition": subgroup_info,
        "Comparison": " vs ".join(labels),
        "Test method": test_method,
        "P-value": p_value_formatted,
        "Test statistic": test_stat,
        "F-value" if test_method == "One-way ANOVA" else "U-value": test_stat,
        "Levene's test for homogeneity of variance P-value": f"P = {levene_p:.3f}",
        "Group information": f"{', '.join([f'{label} (n={len(group)})' for label, group in zip(labels, groups)])}",
        "Descriptive statistics": "; ".join(descriptive_stats)
    }

# Prepare result list
results = []

# Part 1: Age analysis under symptom status classification
for disease in data["Symptom status"].unique():
    disease_data = data[data["Symptom status"] == disease]
    # Core modification: Remove the prefix "Symptom status: ", only retain symptom labels
    subgroup_info = f"{symptom_mapping.get(disease, disease)}"
    age_groups = [
        disease_data[disease_data["Age group"] == age_group]["C7S"]
        for age_group in age_labels
        if not disease_data[disease_data["Age group"] == age_group].empty
    ]
    # Age labels without "Age" prefix
    group_labels = [f"{age_group}" for age_group in age_labels if not disease_data[disease_data["Age group"] == age_group].empty]
    if len(age_groups) > 1:
        result = perform_adaptive_analysis(age_groups, group_labels, subgroup_info)
        results.append(result)

# Part 2: Curvature analysis under symptom status and age group classification
for disease in data["Symptom status"].unique():
    disease_data = data[data["Symptom status"] == disease]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        # Core modification: Remove the prefix "Symptom status: "
        subgroup_info = f"{symptom_mapping.get(disease, disease)}, {age_group}"
        curvature_groups = [
            age_data[age_data["cervical curvature type"] == curvature]["C7S"]
            for curvature in age_data["cervical curvature type"].unique()
        ]
        group_labels = [f"Curvature {curvature}" for curvature in age_data["cervical curvature type"].unique()]
        if len(curvature_groups) > 1:
            result = perform_adaptive_analysis(curvature_groups, group_labels, subgroup_info)
            results.append(result)

# Part 3: Gender analysis under symptom status and age group classification
for disease in data["Symptom status"].unique():
    disease_data = data[data["Symptom status"] == disease]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        # Core modification: Remove the prefix "Symptom status: "
        subgroup_info = f"{symptom_mapping.get(disease, disease)}, {age_group}"
        gender_groups = [
            age_data[age_data["Sex"] == gender]["C7S"]
            for gender in [0, 1]
        ]
        group_labels = [f"Sex {gender}" for gender in [0, 1]]
        if len(gender_groups) > 1:
            result = perform_adaptive_analysis(gender_groups, group_labels, subgroup_info)
            results.append(result)

# Part 4: Curvature analysis under symptom status, age group, and gender classification
for disease in data["Symptom status"].unique():
    disease_data = data[data["Symptom status"] == disease]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        for gender in [0, 1]:
            gender_data = age_data[age_data["Sex"] == gender]
            # Core modification: Remove the prefix "Symptom status: "
            subgroup_info = f"{symptom_mapping.get(disease, disease)}, {age_group}, Sex: {gender}"
            curvature_groups = [
                gender_data[gender_data["cervical curvature type"] == curvature]["C7S"]
                for curvature in gender_data["cervical curvature type"].unique()
            ]
            group_labels = [f"Curvature {curvature}" for curvature in gender_data["cervical curvature type"].unique()]
            if len(curvature_groups) > 1:
                result = perform_adaptive_analysis(curvature_groups, group_labels, subgroup_info)
                results.append(result)

# Part 5: Gender analysis under symptom status, age group, and curvature type classification
for disease in data["Symptom status"].unique():
    disease_data = data[data["Symptom status"] == disease]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        for curvature in age_data["cervical curvature type"].unique():
            curvature_data = age_data[age_data["cervical curvature type"] == curvature]
            # Core modification: Remove the prefix "Symptom status: "
            subgroup_info = f"{symptom_mapping.get(disease, disease)}, {age_group}, Curvature: {curvature}"
            gender_groups = [
                curvature_data[curvature_data["Sex"] == gender]["C7S"]
                for gender in [0, 1]
            ]
            group_labels = [f"Sex {gender}" for gender in [0, 1]]
            if len(gender_groups) > 1:
                result = perform_adaptive_analysis(gender_groups, group_labels, subgroup_info)
                results.append(result)

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Export to Excel file
results_df.to_excel(output_file, index=False)
print(f"Statistical results have been saved to {output_file}")