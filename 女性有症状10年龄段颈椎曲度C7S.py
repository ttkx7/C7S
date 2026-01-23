import pandas as pd
import os

# 读取Excel文件
input_file = r"C:/Users/Administrator/Desktop/sva/1万人的基线和数据-武灵敏.xlsx"
output_dir = r"C:/Users/Administrator/Desktop/女性有症状10年龄段颈椎曲度SVA.xlsx"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "女性有症状10年龄段颈椎曲度SVA.xlsx")

# 读取Excel数据，并重命名列
data = pd.read_excel(input_file)
data.columns = ["排序", "性别", "年龄", "疾病分型", "颈椎曲度情况", "SVA"]

# 定义年龄分组区间
age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
age_labels = ['0-9岁', '10-19岁', '20-29岁', '30-39岁', '40-49岁', '50-59岁', '60-69岁', '70-79岁', '80-89岁']
data["年龄分组"] = pd.cut(data["年龄"], bins=age_bins, labels=age_labels, right=False)

# 筛选疾病分型为有症状且性别为女的数据
symptomatic_data = data[(data["疾病分型"] == 1) & (data["性别"] == 1)]

# 准备存储结果
results = []

# 统计每个年龄分组中颈椎曲度情况的SVA均值和标准差
for age_group in age_labels:
    age_group_data = symptomatic_data[symptomatic_data["年龄分组"] == age_group]
    for curvature in range(1, 6):  # 颈椎曲度情况：1-5
        curvature_data = age_group_data[age_group_data["颈椎曲度情况"] == curvature]
        if len(curvature_data) > 0:
            mean_sva = curvature_data["SVA"].mean()
            std_sva = curvature_data["SVA"].std()
            results.append({
                "年龄分组": age_group,
                "颈椎曲度情况": curvature,
                "SVA均值": round(mean_sva, 2),
                "SVA标准差": round(std_sva, 2)
            })
        else:
            results.append({
                "年龄分组": age_group,
                "颈椎曲度情况": curvature,
                "SVA均值": "无数据",
                "SVA标准差": "无数据"
            })

# 转换为DataFrame
results_df = pd.DataFrame(results)

# 输出Excel文件
try:
    results_df.to_excel(output_file, index=False)
    print(f"统计结果已保存至 {output_file}")
except PermissionError:
    print(f"无法写入文件，请关闭文件：{output_file}")
