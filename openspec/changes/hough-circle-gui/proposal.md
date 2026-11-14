# Proposal

## Why

RT 视觉组培训任务三需要一个可交互的霍夫圆检测工具，让使用者直观看到 `dp`、`minDist`、`param1`、`param2` 与半径范围对检测结果的影响。当前仓库只有初始化与 OpenSpec 配置，`src/` 尚无实现，两张验收图也未产生可复现的检测结果。

## What Changes

- 新增霍夫圆检测核心：读取图片、灰度化、模糊、调用 `cv2.HoughCircles`，返回圆心与半径，并绘制标注图。
- 新增 tkinter 图形界面：导入本地图片、六个参数控件（`dp`、`minDist`、`param1`、`param2`、最小半径、最大半径）、实时预览、导出标注图。
- 界面默认参数固定为 `dp=1.2`、`minDist=300`、`param1=100`、`param2=100`、最小半径 0、最大半径 0，并作为两张验收图共用的验收参数。
- 增加参数合法性与异常处理（未导入图片、图片读取失败、半径范围非法、检测无结果、导出失败）。
- 用 `examples/coins.jpg` 与 `examples/cookie-plate.jpg` 验收，结果图写入 `docs/`，并把实际生效参数补进 README 验收表。
- 不新增 pip 依赖；仅使用 Python 标准库、tkinter、OpenCV、NumPy。

## Capabilities

### New Capabilities

- `circle-detection`: 霍夫圆检测的参数语义、输入校验、检测与标注输出行为，以及两张验收图的判定场景。
- `detection-gui`: tkinter 界面的图片导入、参数调节、实时预览、导出与错误提示行为。

### Modified Capabilities

无。项目当前没有已建立的主规格。

## Impact

- 代码：新增 `src/hough_circle_gui.py`（入口与界面）与 `src/circle_detector.py`（检测与标注逻辑）。
- 文档：`README.md` 补全运行说明、默认参数与验收参数、结果图；`docs/` 新增验收输出图。
- 依赖：无新增；保持系统包提供的 Python 3.12、OpenCV 4.6.0、NumPy 1.26.4、tkinter 8.6。
- 运行环境：GUI 依赖 WSLg；无图形环境时可用无头方式验证检测核心。
