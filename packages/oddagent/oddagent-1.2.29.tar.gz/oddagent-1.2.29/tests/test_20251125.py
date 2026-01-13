import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 数据准备
def create_accuracy_line_chart():
    # 模型和方法标签
    labels = ['Qwen2.5-0.5B 单次请求', 'Qwen2.5-0.5B 分解法', 
              'Qwen3-4B 单次请求', 'Qwen3-4B 分解法']
    
    # 意图通过率
    intent_accuracy = [89.71, 72.4, 86.76, 100]
    
    # 意图槽位通过率
    slot_accuracy = [95.59, 43.47, 91.18, 100]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 设置x轴位置
    x = np.arange(len(labels))
    width = 0.35
    
    # 绘制线图
    ax.plot(x, intent_accuracy, 'o-', linewidth=2, markersize=8, 
            label='意图通过率 (%)', color='#1f77b4')
    ax.plot(x, slot_accuracy, 's-', linewidth=2, markersize=8, 
            label='意图槽位通过率 (%)', color='#ff7f0e')
    
    # 在每个点上标注数值
    for i, v in enumerate(intent_accuracy):
        ax.text(i, v + 1, f'{v}%', ha='center', fontsize=10)
    
    for i, v in enumerate(slot_accuracy):
        ax.text(i, v + 1, f'{v}%', ha='center', fontsize=10)
    
    # 设置图表标题和标签
    ax.set_title('不同模型和方法的意图识别准确率对比', fontsize=16, pad=20)
    ax.set_xlabel('模型和方法', fontsize=12, labelpad=10)
    ax.set_ylabel('准确率 (%)', fontsize=12, labelpad=10)
    
    # 设置x轴刻度标签
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right')
    
    # 设置y轴范围，确保从0开始
    ax.set_ylim(0, 110)
    
    # 添加网格线
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 添加图例
    ax.legend(loc='lower right')
    
    # 添加水印或注释
    fig.text(0.5, 0.01, '数据来源：20251125 语音领航预研进展说明', 
             ha='center', fontsize=9, style='italic')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    output_file = 'charts/accuracy_comparison_line.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存至: {output_file}")
    return output_file

if __name__ == "__main__":
    create_accuracy_line_chart()