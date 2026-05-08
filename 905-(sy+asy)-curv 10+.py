import pandas as pd
import scipy.stats as stats
import os

# ================= Configuration of paths =================
# Please ensure the paths here are the actual paths on your computer
input_file = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\加权匹配结果合并C7S（PSM-905人-表2采用的数据）.xlsx"
output_dir = r"E:\PG After24-9\论文\冉宇-C7倾斜角\数据处理\spine公开代码及数据备用\PSM 905"

# Ensure the output directory exists; create it if it does not
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "905-(sy+asy)-curv 10+.xlsx")

# ================= Data reading and preprocessing =================
print("Reading data...")
# Read Excel data
data = pd.read_excel(input_file)
# Rename columns (replace with English column names, corresponding to the modified Excel file)
data.columns = ["No", "Sex", "Age", "Symptom status", "cervical curvature type", "C7S"]

# Define mapping relationships
symptom_status_mapping = {1: "Symptomatic", 2: "Asymptomatic"}  # Symptom status mapping
curvature_type_mapping = {1: "Lordotic", 2: "Straight", 3: "Sigmoid1", 4: "Sigmoid2", 5: "Kyphotic"}  # Cervical curvature type mapping
sex_mapping = {0: "Male", 1: "Female"}  # Added: Sex mapping

# Define age groups (10-year intervals, replace "岁" with Y)
age_bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99]
age_labels = [
    "0-9 Y", "10-19 Y", "20-29 Y", "30-39 Y", "40-49 Y", 
    "50-59 Y", "60-69 Y", "70-79 Y", "80-89 Y", "90-99 Y"
]

# Perform binning
# include_lowest=True ensures that age 0 is included in the 0-9 Y interval
data["Age group"] = pd.cut(data["Age"], bins=age_bins, labels=age_labels, right=True, include_lowest=True)

# ================= Statistical analysis functions =================
def perform_adaptive_analysis(groups, labels, subgroup_info):
    """
    Perform adaptive statistical analysis:
    1. Check normality (D'Agostino-Pearson method)
    2. Select ANOVA or Kruskal-Wallis
    3. Return statistical results
    """
    # Recheck sample size (double insurance here, although filtered externally)
    if any(len(group) < 3 for group in groups):
        return None 

    # Check normality of each group (D'Agostino-Pearson test, replacing the original Shapiro-Wilk)
    # DAP test requires each group to have a sample size ≥ 8; otherwise, skip the test for that group and determine it as non-normal
    normality = True
    try:
        for group in groups:
            if len(group) < 8:
                normality = False
                break
            # D'Agostino-Pearson normality test (p>0.05 indicates compliance with normal distribution)
            dap_stat, dap_p = stats.normaltest(group)
            if dap_p <= 0.05:
                normality = False
                break
    except Exception:
        normality = False # If the test fails, default to non-normal

    # Calculate descriptive statistics (mean ± standard deviation)
    descriptive_stats = []
    for label, group in zip(labels, groups):
        if len(group) == 0:
            desc = f"{label}: n=0, mean=No data, sd=No data"
        else:
            desc = f"{label}: n={len(group)}, mean={group.mean():.2f}, sd={group.std():.2f}"
        descriptive_stats.append(desc)

    if normality:
        # Normal distribution -> One-way ANOVA
        stat, p_value = stats.f_oneway(*groups)
        test_method = "One-way ANOVA"
    else:
        # Non-normal -> Kruskal-Wallis test
        stat, p_value = stats.kruskal(*groups)
        test_method = "Kruskal-Wallis test"

    # Format P value
    p_value_formatted = "P < 0.001" if p_value < 0.001 else f"P = {p_value:.3f}"

    return {
        "Subgroup": subgroup_info,  # Original "分型前提", changed to English key name
        "Comparison": " vs ".join(labels),  # Original "比较", changed to English key name
        "Test method": test_method,  # Original "检验方法", changed to English key name
        "P value": p_value_formatted,  # Original "P值", changed to English key name
        "Test statistic": stat,  # Original "统计量", changed to English key name
        "Group info": str(labels),  # Original "组信息", changed to English key name
        "Descriptive statistics": "; ".join(descriptive_stats)  # Original "描述性统计", changed to English key name
    }

# ================= Core filtering logic (modified version) =================
def filter_groups(data_subset, group_col, label_list, label_prefix="", min_samples=3):
    """
    Filter out groups with sample size >= min_samples.
    """
    valid_groups = []
    valid_labels = []
    
    # If label_list is specified (e.g., age group list), traverse in order
    unique_vals = label_list if label_list is not None else sorted(data_subset[group_col].dropna().unique())

    for val in unique_vals:
        # Extract data for the current group
        group_data = data_subset[data_subset[group_col] == val]["C7S"]
        
        # Core logic: only groups with sample size >= min_samples are included in the comparison
        if len(group_data) >= min_samples:
            valid_groups.append(group_data)
            # Format label name
            if label_prefix:
                valid_label = str(val) if label_prefix not in ["Symptom status", "cervical curvature type", "Sex"] else val
            else:
                valid_label = str(val)
            
            # Map numbers to English (symptom status/cervical curvature type/sex)
            if group_col == "Symptom status" and val in symptom_status_mapping:
                valid_label = symptom_status_mapping[val]
            elif group_col == "cervical curvature type" and val in curvature_type_mapping:
                valid_label = curvature_type_mapping[val]
            elif group_col == "Sex" and val in sex_mapping:  # Added: Sex mapping
                valid_label = sex_mapping[val]
            
            valid_labels.append(valid_label)
                
    return valid_groups, valid_labels

# ================= Main analysis logic =================
results = []
print("Starting statistical analysis...")

# --- 1. Symptom status -> Compare different cervical curvature types (keep >= 3 samples) ---
for symptom_code in sorted(data["Symptom status"].unique()):
    # Map symptom status numbers to English (remove "Symptom status" prefix)
    symptom_name = symptom_status_mapping.get(symptom_code, f"Unknown_{symptom_code}")
    symptom_data = data[data["Symptom status"] == symptom_code]
    
    groups, labels = filter_groups(symptom_data, "cervical curvature type", None, min_samples=3)
    
    if len(groups) > 1:
        # Subgroup info only retains the English name of symptom status (no "Symptom status" prefix)
        subgroup_info = symptom_name
        res = perform_adaptive_analysis(groups, labels, subgroup_info)
        if res: results.append(res)

# --- 2. Symptom status + curvature -> Compare sex (keep >= 3 samples) ---
for symptom_code in sorted(data["Symptom status"].unique()):
    symptom_name = symptom_status_mapping.get(symptom_code, f"Unknown_{symptom_code}")
    symptom_data = data[data["Symptom status"] == symptom_code]
    
    for curvature_code in sorted(symptom_data["cervical curvature type"].unique()):
        curvature_name = curvature_type_mapping.get(curvature_code, f"Unknown_{curvature_code}")
        curvature_data = symptom_data[symptom_data["cervical curvature type"] == curvature_code]
        
        groups, labels = filter_groups(curvature_data, "Sex", [0, 1], min_samples=3)
        
        if len(groups) > 1:
            # Subgroup info only retains symptom status + curvature names (no prefixes)
            subgroup_info = f"{symptom_name}, {curvature_name}"
            res = perform_adaptive_analysis(groups, labels, subgroup_info)
            if res: results.append(res)

# --- 3. Symptom status + curvature -> Compare age groups (modified: threshold >= 10 samples) ---
print("Processing age group comparisons (threshold of 10 samples)...")
for symptom_code in sorted(data["Symptom status"].unique()):
    symptom_name = symptom_status_mapping.get(symptom_code, f"Unknown_{symptom_code}")
    symptom_data = data[data["Symptom status"] == symptom_code]
    
    for curvature_code in sorted(symptom_data["cervical curvature type"].unique()):
        curvature_name = curvature_type_mapping.get(curvature_code, f"Unknown_{curvature_code}")
        curvature_data = symptom_data[symptom_data["cervical curvature type"] == curvature_code]
        
        # Here min_samples is set to 10, and age labels have no "age" prefix
        groups, labels = filter_groups(curvature_data, "Age group", age_labels, min_samples=10)
        
        # Perform comparison as long as the number of remaining valid groups > 1
        if len(groups) > 1:
            subgroup_info = f"{symptom_name}, {curvature_name}"
            res = perform_adaptive_analysis(groups, labels, subgroup_info)
            if res: results.append(res)

# --- 4. Symptom status + curvature + sex -> Compare age groups (modified: threshold >= 10 samples) ---
for symptom_code in sorted(data["Symptom status"].unique()):
    symptom_name = symptom_status_mapping.get(symptom_code, f"Unknown_{symptom_code}")
    symptom_data = data[data["Symptom status"] == symptom_code]
    
    for curvature_code in sorted(symptom_data["cervical curvature type"].unique()):
        curvature_name = curvature_type_mapping.get(curvature_code, f"Unknown_{curvature_code}")
        curvature_data = symptom_data[symptom_data["cervical curvature type"] == curvature_code]
        
        for gender in [0, 1]:
            gender_data = curvature_data[curvature_data["Sex"] == gender]
            
            # Here min_samples is set to 10
            groups, labels = filter_groups(gender_data, "Age group", age_labels, min_samples=10)
            
            if len(groups) > 1:
                # Added: map sex numbers to Male/Female
                subgroup_info = f"{symptom_name}, {curvature_name}, {sex_mapping[gender]}"
                res = perform_adaptive_analysis(groups, labels, subgroup_info)
                if res: results.append(res)

# --- 5. Symptom status + curvature + age group -> Compare sex (keep >= 3 samples) ---
for symptom_code in sorted(data["Symptom status"].unique()):
    symptom_name = symptom_status_mapping.get(symptom_code, f"Unknown_{symptom_code}")
    symptom_data = data[data["Symptom status"] == symptom_code]
    
    for curvature_code in sorted(symptom_data["cervical curvature type"].unique()):
        curvature_name = curvature_type_mapping.get(curvature_code, f"Unknown_{curvature_code}")
        curvature_data = symptom_data[symptom_data["cervical curvature type"] == curvature_code]
        
        for age_group in age_labels:
            age_data = curvature_data[curvature_data["Age group"] == age_group]
            
            groups, labels = filter_groups(age_data, "Sex", [0, 1], min_samples=3)
            
            if len(groups) > 1:
                # Age group has no "age" prefix, symptom status/curvature have no prefixes
                subgroup_info = f"{symptom_name}, {curvature_name}, {age_group}"
                res = perform_adaptive_analysis(groups, labels, subgroup_info)
                if res: results.append(res)

# ================= Save results =================
results_df = pd.DataFrame(results)

if not results_df.empty:
    try:
        results_df.to_excel(output_file, index=False)
        print(f"Statistical analysis completed! Successfully generated {len(results_df)} comparison results.")
        print(f"Results have been saved to: {output_file}")
    except PermissionError:
        print(f"Error: Unable to write to file {output_file}. Please check if the file is open.")
else:
    print("No valid statistical results were generated (possibly because all groups have insufficient sample sizes).")