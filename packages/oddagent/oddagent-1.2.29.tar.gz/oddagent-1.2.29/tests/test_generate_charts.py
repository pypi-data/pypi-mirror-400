import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 从测试结果中提取数据
models = [
    'qwen2.5-0.5b-instruct',
    'qwen2.5-0.5b-instruct2',
    'qwen3-30-a3b-instruct',
    'qwen3-4b-instruct',
    'qwen3-0.6b',
    'qwen3-0.6b_no_think'
]

# 各模型的性能指标
avg_times = [2.55, 2.30, 3.39, 2.35, 2.76, 2.39]  # 平均耗时(秒)
max_times = [3.00, 2.56, 5.69, 2.43, 4.10, 2.51]   # 最大耗时(秒)
min_times = [2.28, 2.09, 2.81, 2.24, 2.34, 2.26]   # 最小耗时(秒)
success_rates = [31.82, 22.73, 96.97, 100.00, 2.63, 1.52]  # 成功率(%)

# 创建图表目录
output_dir = 'charts'
os.makedirs(output_dir, exist_ok=True)

# 1. 平均耗时对比图（线图）
plt.figure(figsize=(10, 6))
plt.plot(models, avg_times, marker='o', color='skyblue', linewidth=2, markersize=8)
plt.title('各模型平均耗时对比')
plt.xlabel('模型')
plt.ylabel('平均耗时(秒)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 在数据点上添加数值标签
for i, value in enumerate(avg_times):
    plt.text(i, value + 0.05, f'{value:.2f}s', ha='center', va='bottom')

plt.savefig(os.path.join(output_dir, 'avg_time_comparison_line.png'), dpi=300)
plt.close()

# 2. 最大耗时对比图（线图）
plt.figure(figsize=(10, 6))
plt.plot(models, max_times, marker='s', color='salmon', linewidth=2, markersize=8)
plt.title('各模型最大耗时对比')
plt.xlabel('模型')
plt.ylabel('最大耗时(秒)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 在数据点上添加数值标签
for i, value in enumerate(max_times):
    plt.text(i, value + 0.05, f'{value:.2f}s', ha='center', va='bottom')

plt.savefig(os.path.join(output_dir, 'max_time_comparison_line.png'), dpi=300)
plt.close()

# 3. 最小耗时对比图（线图）
plt.figure(figsize=(10, 6))
plt.plot(models, min_times, marker='^', color='lightgreen', linewidth=2, markersize=8)
plt.title('各模型最小耗时对比')
plt.xlabel('模型')
plt.ylabel('最小耗时(秒)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 在数据点上添加数值标签
for i, value in enumerate(min_times):
    plt.text(i, value + 0.05, f'{value:.2f}s', ha='center', va='bottom')

plt.savefig(os.path.join(output_dir, 'min_time_comparison_line.png'), dpi=300)
plt.close()

# 4. 成功率对比图（线图）
plt.figure(figsize=(10, 6))
plt.plot(models, success_rates, marker='D', color='lightcoral', linewidth=2, markersize=8)
plt.title('各模型成功率对比')
plt.xlabel('模型')
plt.ylabel('成功率(%)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.ylim(0, 105)  # 设置y轴范围，让标签更清晰
plt.tight_layout()

# 在数据点上添加数值标签
for i, value in enumerate(success_rates):
    plt.text(i, value + 1, f'{value:.2f}%', ha='center', va='bottom')

plt.savefig(os.path.join(output_dir, 'success_rate_comparison_line.png'), dpi=300)
plt.close()

# 5. 综合性能对比图（耗时和成功率，线图）
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# 耗时对比（线图）
x = np.arange(len(models))

ax1.plot(x, min_times, marker='o', color='lightgreen', linewidth=2, markersize=8, label='最小耗时')
ax1.plot(x, avg_times, marker='s', color='skyblue', linewidth=2, markersize=8, label='平均耗时')
ax1.plot(x, max_times, marker='^', color='salmon', linewidth=2, markersize=8, label='最大耗时')
ax1.set_ylabel('耗时(秒)')
ax1.set_title('各模型耗时对比')
ax1.set_xticks(x)
ax1.set_xticklabels(models, rotation=45, ha='right')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()

# 成功率对比（线图）
ax2.plot(x, success_rates, marker='D', color='lightcoral', linewidth=2, markersize=8)
ax2.set_ylabel('成功率(%)')
ax2.set_title('各模型成功率对比')
ax2.set_xticks(x)
ax2.set_xticklabels(models, rotation=45, ha='right')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.set_ylim(0, 105)

# 在成功率数据点上添加数值标签
for i, v in enumerate(success_rates):
    ax2.text(i, v + 1, f'{v:.2f}%', ha='center')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'comprehensive_comparison_line.png'), dpi=300)
plt.close()

print("所有线图已生成并保存到charts目录中")
print("生成的图表文件：")
print("1. charts/avg_time_comparison_line.png - 平均耗时对比图（线图）")
print("2. charts/max_time_comparison_line.png - 最大耗时对比图（线图）")
print("3. charts/min_time_comparison_line.png - 最小耗时对比图（线图）")
print("4. charts/success_rate_comparison_line.png - 成功率对比图（线图）")
print("5. charts/comprehensive_comparison_line.png - 综合性能对比图（线图）")