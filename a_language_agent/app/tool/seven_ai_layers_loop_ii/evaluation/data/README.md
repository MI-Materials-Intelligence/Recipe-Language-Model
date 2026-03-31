# Data Overview

This directory contains all data files required to run the project.

## Data Files Description

### 1. 预测器模型文件 (`predictor_inputs/`)

**预测器类型：**
- `ff/` - 填充因子(FF)预测所需文件
- `jsc/` - 短路电流密度(Jsc)预测器所需文件  
- `pce/` - 光电转换效率(PCE)预测器所需文件
- `voc/` - 开路电压(Voc)预测器所需文件

**各预测器目录包含以下文件：**

| 文件 | 格式 | 说明 |
|------|------|------|
| `xgb_col_*.pkl` | Pickle | XGBoost模型特征列 |
| `xgb_scaler_*.pkl` | Pickle | 数据标准化器 |
| `xgb_model_*.pkl` | Pickle | 训练好的XGBoost模型 |
| `encoding_mappings_*.json` | JSON | 类别特征编码映射 |

### 2. 配置文件

#### `compound_mapping.json`
- **格式**: JSON
- **说明**: 化合物名称映射表，用于统一不同来源的化合物命名
- **示例**:
```json
{
  "2-AEP": "2-AEP (2-aminoethylphosphonic acid)",
  "2PACz": "2PACz (2-(9H-carbazol-9-yl)ethylphosphonic acid)"
}
```

#### `five_dimension_rubrics_new_zhao.json`
- **格式**: JSON
- **说明**: 机理推理中5个维度的评价标准
- **示例**:
```json
{
  "score_range": "9-10",
  "label": "",
  "description": "• All chemical names, structures, and ionic compositions are fully correct; no contradictions.• Complex species (e.g., PEA⁺, PACz derivatives) are accurately described; abbreviations and full names match."
}
```

#### `materials_dict_2025_11_11.pickle`
- **格式**: Pickle
- **说明**: 材料字典，用于补充同一化合物的不同形式

## Source

1. `predictor_inputs/`： 模型训练输出的文件，包含训练好的模型及其相关配置
2. 其他：由实验团队提供

## Notes

### 使用限制
- 模型文件仅适用于钙钛矿太阳能电池相关预测
- 材料字典主要包含常见钙钛矿材料，新材料需要手动添加

### 更新维护
- 模型文件会随着新数据的加入而更新
- 材料字典定期扩充
- 如发现错误或缺失，请联系团队更新