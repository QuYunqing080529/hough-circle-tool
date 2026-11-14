# AGENTS.md

本文件面向在本仓库工作的 AI 代理与开发者。约束优先于个人偏好；与 README 冲突时以 README 为准并同步修正。

## 项目目标

RT 视觉组培训任务三：带图形界面的霍夫圆检测小工具。核心能力：

- 导入本地图片
- 调整 `HoughCircles` 参数（`dp`、`minDist`、`param1`、`param2`、半径范围）
- 实时预览检测结果
- 导出带标注的图片

当前状态：仅完成项目初始化与 OpenSpec 配置，`src/` 尚无实现。未实现的能力不得在文档中描述为已可用。

## 技术栈与依赖

- OS：Ubuntu 24.04（WSL2，WSLg 提供图形界面）
- Python 3.12
- OpenCV 4.6.0（`cv2`）
- NumPy 1.26.4
- tkinter 8.6（GUI）

依赖全部由系统包提供，**不要新增 pip 依赖**；确需引入时先说明理由并更新本文件。验证环境：

```bash
python3 -c "import cv2, numpy, tkinter; print(cv2.__version__, numpy.__version__, tkinter.TkVersion)"
```

预期输出 `4.6.0 1.26.4 8.6`。

## 目录结构

```
hough_circle/
├── AGENTS.md          # 本文件：代理/开发约定
├── README.md          # 项目说明、验收表、进度
├── .gitignore
├── src/               # 源码（入口 src/hough_circle_gui.py，待实现）
├── examples/          # 验收图片：coins.jpg、cookie-plate.jpg
├── docs/              # 验收标注结果图
├── openspec/
│   ├── config.yaml    # schema: spec-driven
│   ├── specs/         # 主规格
│   └── changes/       # 变更提案；archive/ 存放已归档变更
└── .agents/skills/    # OpenSpec 工作流技能说明
```

约定：源码只放 `src/`，验收输入只放 `examples/`，验收输出图只放 `docs/`，生成物（`out/`、`output/`、缓存）不得提交。

## 开发约定

### OpenSpec 管理变更

所有非琐碎改动走 OpenSpec（`openspec/` 已配置 `schema: spec-driven`）：

1. 在 `openspec/changes/<change-id>/` 下创建提案：规格增量、设计、任务清单
2. 确认规格与任务清单后再实现
3. 实现时逐项勾选任务，并记录验收结果
4. 完成后归档到 `openspec/changes/archive/`

不要绕过提案直接改动行为；小修复（拼写、注释）可直接提交。

### 提交信息

格式：`<type>: <short description>`，描述用简短清晰的英文。

- `type` 仅取：`feat`、`fix`、`refactor`、`docs`、`chore`、`test`、`build`
- 示例：`feat: implement hough circle detection core`

### 分支命名

格式：`<type>/<short-description>`，`type` 与提交信息取值一致。

- 示例：`feat/hough-circle-gui`、`fix/param2-slider-range`
- `main` 保持可运行；合并前确认验收通过

## 运行与验收

### 运行

```bash
python3 src/hough_circle_gui.py
```

当前入口尚未实现，此命令在实现前会失败。GUI 依赖 WSLg；无图形环境时仅能做无头逻辑验证（直接调用检测函数并写图）。

### 验收

| 图片 | 期望结果 | 验收参数 |
|---|---|---|
| `examples/coins.jpg` | 标出两个硬币外缘 | 实现后填写 |
| `examples/cookie-plate.jpg` | 标出一个盘沿 | 实现后填写 |

通过标准：

1. GUI 能导入上述两张图片并实时预览
2. 检测结果符合表中期望，导出图保存到 `docs/` 并嵌入 README 验收章节
3. README 验收表的参数列补全为实际生效值

记录验收时写明：图片、实际参数、输出图路径。不要用未实际运行的结果填充验收表。
