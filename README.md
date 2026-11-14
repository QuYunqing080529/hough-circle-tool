# hough_circle

RT 视觉组培训任务三：带图形界面的霍夫圆检测小工具。

## 功能

- 导入本地图片
- 调整 HoughCircles 参数（dp、minDist、param1、param2、半径范围）
- 实时预览检测结果
- 导出带标注的图片

## 环境

- Ubuntu 24.04（WSL2，WSLg 提供图形界面）
- Python 3.12
- OpenCV 4.6.0
- NumPy 1.26.4
- tkinter 8.6（GUI）

无需额外 pip 安装：上述依赖由系统包提供。

## 启动方式

```bash
python3 src/hough_circle_gui.py
```

（实现后补全参数说明）

## 验收图片与参数

| 图片 | 期望结果 | 验收参数 |
|---|---|---|
| `examples/coins.jpg` | 标出两个硬币外缘 | 待实现后填写 |
| `examples/cookie-plate.jpg` | 标出一个盘沿 | 待实现后填写 |

验收结果图放在 `docs/` 下，并在实现完成后嵌入本节。

## 目录结构

```
hough_circle/
├── README.md
├── .gitignore
├── src/          # 源码
├── examples/     # 验收图片（coins.jpg、cookie-plate.jpg）
├── docs/         # 标注结果图
└── openspec/     # OpenSpec 规格与变更记录
```

## 开发流程

使用 OpenSpec 管理变更：

1. 在 `openspec/changes/` 下建立变更提案
2. 确认规格与任务清单
3. 实现并记录验收结果
4. 归档变更

## 状态

- [x] 项目初始化与 OpenSpec 配置
- [ ] 霍夫圆检测核心逻辑
- [ ] 图形界面
- [ ] 两张验收图通过
- [ ] README 补全验收参数与结果图