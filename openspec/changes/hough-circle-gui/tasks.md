# Tasks

## 1. 检测核心

- [ ] 1.1 新建 `src/circle_detector.py`，定义 `HoughParams` 数据类、`validate` 与 `(x, y, r)` 圆结果约定；用 `python3 -c` 调用 `validate` 覆盖合法参数、`dp<=0`、`maxRadius<=minRadius`（非双 0）三类输入并核对返回。
- [ ] 1.2 实现 `load_image` 与 `save_image`（`np.fromfile`/`cv2.imdecode` 与 `cv2.imencode`/`tofile`）；把 `examples/coins.jpg` 读入后写到临时路径再读回，确认形状一致、像素差为 0，验证后删除临时文件。
- [ ] 1.3 实现 `detect_circles`：灰度化、`medianBlur(5)`、`cv2.HOUGH_GRADIENT`，非法参数抛 `ValueError`；用 `examples/coins.jpg` 与两图共用参数 `dp=1.2, minDist=300, param1=100, param2=100, minRadius=0, maxRadius=0` 运行，确认结果恰为 2 个圆且半径分别为约 180 与 179。
- [ ] 1.4 实现 `annotate`：在输入副本上绘制圆周与圆心，返回 `np.ndarray`；对 1.3 的两个圆生成标注图，确认尺寸与输入一致、原数组未被修改。
- [ ] 1.5 用 `examples/cookie-plate.jpg` 与同一组参数 `dp=1.2, minDist=300, param1=100, param2=100, minRadius=0, maxRadius=0` 运行 `detect_circles`，确认结果恰为 1 个圆，圆心约为 `(263, 259)`、半径约为 244。

## 2. 图形界面

- [ ] 2.1 新建 `src/hough_circle_gui.py`，搭建窗口：预览区、六个 `tk.Scale`（范围与默认值按 `design.md`）、导入/导出按钮、状态栏；运行后确认控件齐全、参数初值与设计表一致。
- [ ] 2.2 实现导入：文件对话框过滤 JPEG/PNG 等格式，`load_image` 成功后按比例缩放并在预览区显示原始图，未导入时禁用导出；导入 `examples/coins.jpg` 确认图像完整显示且不拉伸。
- [ ] 2.3 实现 BGR→RGB→PPM→`tk.PhotoImage` 的显示链路并持有引用，避免无 Pillow 依赖；在 WSLg 中确认预览可见、窗口缩放后不崩溃。
- [ ] 2.4 接入参数回调与 80 ms 去抖：参数变化自动重检并刷新标注预览，状态栏更新圆数量；拖动 `param2` 确认预览无需点按钮即可变化。
- [ ] 2.5 实现错误路径：非法参数、无法解码的图片、检测 0 个圆时分别提示并保留上次有效预览；用文本文件冒充图片导入，确认提示后程序仍可继续导入正常图片。
- [ ] 2.6 实现导出：保存对话框选择路径，缺省补 `.png`，按原图分辨率写出当前标注图并提示路径；导出到不可写路径时显示失败提示且不退出。
- [ ] 2.7 在 README 补充运行命令、控件说明、默认参数表与“半径 0 表示不限”的说明，并确认命令 `python3 src/hough_circle_gui.py` 与文档一致。

## 3. 验收与集成

- [ ] 3.1 无头生成两张验收标注图到 `docs/coins_result.png` 与 `docs/cookie_plate_result.png`（使用规格中的参数），确认尺寸与原图一致、标注数量分别为 2 与 1。
- [ ] 3.2 在 WSLg 中启动 GUI，依次导入两张图片并保持默认参数（即验收参数），确认 `coins.jpg` 标出两个硬币外缘、`cookie-plate.jpg` 标出一个盘沿，并从界面导出一次核对文件可打开。
- [ ] 3.3 核对 README 验收表已填的共用参数与运行结果一致，补充圆数量与结果图路径并嵌入结果图。
- [ ] 3.4 运行 `python3 -c "import cv2, numpy, tkinter; print(cv2.__version__, numpy.__version__, tkinter.TkVersion)"` 确认仍为系统依赖版本，检查无新增 pip 依赖；清理验收过程中产生的临时脚本与临时文件。

## Workflow follow-up

- 按项目流程归档 `hough-circle-gui`，把两份增量规格同步到 `openspec/specs/`，并确认归档后 `openspec validate` 通过。
