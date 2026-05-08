import pandas as pd
import scipy.stats as stats
import os

# ================= Configure Paths =================
# Please ensure the path here is the actual path on your computer
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\1万人的基线和数据.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\Table 1"

# Ensure the output directory exists; create it if it does not
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "10k-(sy+asy)-age(sex).xlsx")

# ================= Data Reading and Preprocessing =================
print("Reading data...")
# Read Excel data
data = pd.read_excel(input_file)
# Rename columns (ensure correspondence with original data)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# Define age groups (10-year intervals)
age_bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99]
age_labels = [
    "0-9 Y", "10-19 Y", "20-29 Y", "30-39 Y", "40-49 Y", 
    "50-59 Y", "60-69 Y", "70-79 Y", "80-89 Y", "90-99 Y"
]
# include_lowest=True ensures age 0 is included
data["Age group"] = pd.cut(data["Age"], bins=age_bins, labels=age_labels, right=True, include_lowest=True)

# New: Disease classification mapping dictionary (1=Symptomatic (cervical spondylosis group), 2=Asymptomatic (healthy group))
symptom_mapping = {1: "Symptomatic", 2: "Asymptomatic"}

# ================= General Statistical Analysis Function (used for other sections) =================
def perform_adaptive_analysis(groups, labels, subgroup_info):
    # 核心修改1：阈值从3改为10，样本量<10则不参与分析
    if any(len(group) < 10 for group in groups):
        return None

    # Check normality: Replace with D'Agostino-Pearson test (adapted for large samples, replacing the original Shapiro-Wilk test)
    try:
        # normaltest requires sample size ≥ 8; if insufficient, directly judge as non-normal
        normality = all(stats.normaltest(group).pvalue > 0.05 if len(group)>=8 else False for group in groups)
    except:
        normality = False

    descriptive_stats = [
        f"{label}: n={len(group)}, mean={group.mean():.2f}, sd={group.std():.2f}"
        for label, group in zip(labels, groups)
    ]

    if normality:
        stat, p_value = stats.f_oneway(*groups)
        test_method = "One-way ANOVA (ANOVA)"
    else:
        stat, p_value = stats.kruskal(*groups)
        test_method = "Kruskal-Wallis test"

    p_value_formatted = "P < 0.001" if p_value < 0.001 else f"P = {p_value:.3f}"

    return {
        "Subgroup premise": subgroup_info,
        "Comparison": " vs ".join(labels),
        "Test method": test_method,
        "P value": p_value_formatted,
        "Statistic": stat,
        "Group info": str(labels),
        "Descriptive statistics": "; ".join(descriptive_stats)
    }

# ================= Main Analysis Logic =================
results = []
print("Starting statistical analysis...")

# --- Section 1: Age analysis under disease classification ---
for disease_code in sorted(data["Symptom status"].unique()):
    # Replace disease code with English name
    disease_name = symptom_mapping.get(disease_code, f"Unknown({disease_code})")
    disease_data = data[data["Symptom status"] == disease_code]
    
    age_groups = []
    group_labels = []
    for age_group in age_labels:
        g_data = disease_data[disease_data["Age group"] == age_group]["C7S"]
        # 核心修改2：筛选条件从≥3改为≥10
        if len(g_data) >= 10:
            age_groups.append(g_data)
            group_labels.append(f"Age {age_group}")
            
    if len(age_groups) > 1:
        # Remove Symptom status prefix, retain only disease name
        res = perform_adaptive_analysis(age_groups, group_labels, f"{disease_name}")
        if res: results.append(res)

# --- Section 2: Curvature analysis under disease and age classification ---
for disease_code in sorted(data["Symptom status"].unique()):
    disease_name = symptom_mapping.get(disease_code, f"Unknown({disease_code})")
    disease_data = data[data["Symptom status"] == disease_code]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        
        curvature_groups = []
        group_labels = []
        for curvature in sorted(age_data["cervical curvature type"].unique()):
            c_data = age_data[age_data["cervical curvature type"] == curvature]["C7S"]
            # 核心修改3：筛选条件从≥3改为≥10
            if len(c_data) >= 10:
                curvature_groups.append(c_data)
                group_labels.append(f"Cervical curvature type {curvature}")
                
        if len(curvature_groups) > 1:
            # Remove Symptom status prefix, format: Disease name, Age: Age group
            res = perform_adaptive_analysis(curvature_groups, group_labels, f"{disease_name}, Age: {age_group}")
            if res: results.append(res)

# --- ★★★ Section 3 (Core modification): Disease + Age -> Gender comparison (Gender 0 vs Gender 1) ★★★ ---
print("Processing Section 3: Disease + Age -> Gender comparison (independent threshold judgment)...")
for disease_code in sorted(data["Symptom status"].unique()):
    disease_name = symptom_mapping.get(disease_code, f"Unknown({disease_code})")
    disease_data = data[data["Symptom status"] == disease_code]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        # Remove Symptom status prefix, format: Disease name, Age: Age group
        subgroup_info = f"{disease_name}, Age: {age_group}"
        
        # Extract data for two groups
        group0 = age_data[age_data["Sex"] == 0]["C7S"] # Gender 0
        group1 = age_data[age_data["Sex"] == 1]["C7S"] # Gender 1
        
        n0 = len(group0)
        n1 = len(group1)
        
        # 1. Construct descriptive statistics string (independent judgment!)
        desc_parts = []
        
        # ---- Judge Gender 0 ----
        if n0 >= 10:
            # Only when the number of cases >= 10, calculate and display mean and sd
            desc_parts.append(f"Sex 0: n={n0}, mean={group0.mean():.2f}, sd={group0.std():.2f}")
        else:
            # Otherwise, only display the number of cases and a prompt
            desc_parts.append(f"Sex 0: n={n0} (Less than 10 cases)")
            
        # ---- Judge Gender 1 ----
        if n1 >= 10:
            # Only when the number of cases >= 10, calculate and display mean and sd
            desc_parts.append(f"Sex 1: n={n1}, mean={group1.mean():.2f}, sd={group1.std():.2f}")
        else:
            # Otherwise, only display the number of cases and a prompt
            desc_parts.append(f"Sex 1: n={n1} (Less than 10 cases)")
            
        desc_str = "; ".join(desc_parts)
        
        # 2. Judge whether to perform statistical test (both sides must be >= 10)
        if n0 >= 10 and n1 >= 10:
            # Conditions met, perform test: Replace with D'Agostino-Pearson test (adapted for large samples)
            try:
                # Judge each group separately: perform normaltest only if sample size ≥ 8, otherwise judge as non-normal
                norm0 = stats.normaltest(group0).pvalue > 0.05 if len(group0)>=8 else False
                norm1 = stats.normaltest(group1).pvalue > 0.05 if len(group1)>=8 else False
                normality = norm0 and norm1
            except:
                normality = False
            
            if normality:
                stat_val, p_val = stats.f_oneway(group0, group1)
                method = "One-way ANOVA (ANOVA)"
            else:
                stat_val, p_val = stats.kruskal(group0, group1)
                method = "Kruskal-Wallis test"
            
            p_fmt = "P < 0.001" if p_val < 0.001 else f"P = {p_val:.3f}"
            stat_res = stat_val
        else:
            # Conditions not met, skip test
            method = "Skipped"
            p_fmt = "Insufficient sample size"
            stat_res = "N/A"
            
        # 3. Save results (save this row as long as at least one group has non-empty data)
        if n0 > 0 or n1 > 0:
            res = {
                "Subgroup premise": subgroup_info,
                "Comparison": "Sex 0 vs Sex 1",
                "Test method": method,
                "P value": p_fmt,
                "Statistic": stat_res,
                "Group info": "['Sex 0', 'Sex 1']",
                "Descriptive statistics": desc_str
            }
            results.append(res)

# --- Section 4: Curvature analysis under disease, age and gender classification ---
for disease_code in sorted(data["Symptom status"].unique()):
    disease_name = symptom_mapping.get(disease_code, f"Unknown({disease_code})")
    disease_data = data[data["Symptom status"] == disease_code]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        for gender in [0, 1]:
            gender_data = age_data[age_data["Sex"] == gender]
            
            curvature_groups = []
            group_labels = []
            for curvature in sorted(gender_data["cervical curvature type"].unique()):
                c_data = gender_data[gender_data["cervical curvature type"] == curvature]["C7S"]
                # 核心修改4：筛选条件从≥3改为≥10
                if len(c_data) >= 10:
                    curvature_groups.append(c_data)
                    group_labels.append(f"Cervical curvature type {curvature}")
            
            if len(curvature_groups) > 1:
                # Remove Symptom status prefix, format: Disease name, Age: Age group, Sex: Gender
                res = perform_adaptive_analysis(curvature_groups, group_labels, f"{disease_name}, Age: {age_group}, Sex: {gender}")
                if res: results.append(res)

# --- Section 5: Gender analysis under disease, age and curvature classification ---
for disease_code in sorted(data["Symptom status"].unique()):
    disease_name = symptom_mapping.get(disease_code, f"Unknown({disease_code})")
    disease_data = data[data["Symptom status"] == disease_code]
    for age_group in age_labels:
        age_data = disease_data[disease_data["Age group"] == age_group]
        for curvature in sorted(age_data["cervical curvature type"].unique()):
            curvature_data = age_data[age_data["cervical curvature type"] == curvature]
            
            gender_groups = []
            group_labels = []
            for gender in [0, 1]:
                g_data = curvature_data[curvature_data["Sex"] == gender]["C7S"]
                # 核心修改5：筛选条件从≥3改为≥10
                if len(g_data) >= 10:
                    gender_groups.append(g_data)
                    group_labels.append(f"Sex {gender}")
            
            if len(gender_groups) > 1:
                # Remove Symptom status prefix, format: Disease name, Age: Age group, Cervical curvature type: Curvature type
                res = perform_adaptive_analysis(gender_groups, group_labels, f"{disease_name}, Age: {age_group}, Cervical curvature type: {curvature}")
                if res: results.append(res)

# ================= Save Results =================
results_df = pd.DataFrame(results)

if not results_df.empty:
    try:
        results_df.to_excel(output_file, index=False)
        print(f"Statistics completed! Successfully generated {len(results_df)} comparison results.")
        print(f"Results saved to: {output_file}")
    except PermissionError:
        print(f"Error: Unable to write to file {output_file}. Please check if the file is open.")
else:
    print("No valid statistical results were generated.")