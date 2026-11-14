# Design

## Context

见 `proposal.md`。当前 `src/` 为空、没有主规格；README 约定的入口是 `python3 src/hough_circle_gui.py`。环境固定为 Python 3.12 + OpenCV 4.6.0 + NumPy 1.26.4 + tkinter 8.6，且禁止新增 pip 依赖。两张验收图分别为 760×385 与 520×520。

## Goals / Non-Goals

**Goals:**

- 检测逻辑与界面分离，检测核心可在无图形环境下直接调用验收。
- 界面零额外依赖，使用 tkinter 原生控件与 `PhotoImage` 显示预览。
- 参数改动即时重检，导出使用原图分辨率。

**Non-Goals:**

- 不实现批量处理、视频、目标跟踪、圆拟合或亚像素精度。
- 不保存/加载参数预设，不做多语言，不做撤销历史。
- 不修改 `examples/` 中的验收输入图片。

## Decisions

### 模块划分

- `src/circle_detector.py`：纯逻辑，包含参数校验、图片读写、检测、标注。
- `src/hough_circle_gui.py`：tkinter 界面与事件调度，只通过检测核心获取结果。
- 不建包、不加 `__init__.py`；入口脚本所在目录天然在 `sys.path`，直接 `import circle_detector` 即可。

理由：满足"无头可验收"并避免 UI 与算法耦合。备选单文件实现更短，但验收只能通过 GUI，不利于命令行验证。

### 核心接口

```python
@dataclass(frozen=True)
class HoughParams:
    dp: float
    min_dist: int
    param1: int
    param2: int
    min_radius: int
    max_radius: int

def validate(params: HoughParams) -> str | None
def detect_circles(image, params) -> list[tuple[int, int, int]]  # (x, y, r)
def annotate(image, circles) -> np.ndarray                        # 原图副本
def load_image(path: str) -> np.ndarray                          # BGR
def save_image(path: str, image) -> None
```

- 无效参数由 `detect_circles` 抛出 `ValueError`，界面捕获后显示文本并保留上次预览。
- 圆以整数 `(x, y, r)` 元组表示，数量为 0 时返回空列表；不引入 OpenCV 形状数组作为公共接口。

### 预处理与检测

- 灰度化后使用固定 `medianBlur(5)` 抑制噪声，再调用 `cv2.HOUGH_GRADIENT`。
- 六个参数直接映射到 `HoughCircles`；`max_radius=0` 且 `min_radius=0` 时表示不限制半径，其余情况要求 `max_radius > min_radius`。
- 检测使用原图坐标，不做缩放；缩放只发生在显示层。

### 参数控件

| 参数 | 范围 | 步长 | 默认值 |
|---|---|---|---|
| `dp` | 1.0–3.0 | 0.1 | 1.2 |
| `minDist` | 1–1000 | 1 | 300 |
| `param1` | 1–500 | 1 | 100 |
| `param2` | 1–300 | 1 | 100 |
| `minRadius` | 0–1000 | 1 | 0（不限） |
| `maxRadius` | 0–1000 | 1 | 0（不限） |

使用横向 `tk.Scale`，旁边显示当前值；所有控件 `command` 触发同一条重检路径。`param1` 上限高于 `param2` 是因为前者是高阈值、后者是圆心累加阈值，实际常调区间不同；滑杆范围只限制输入，检测语义仍由 OpenCV 决定。

### 实时预览与去抖

控件回调不直接执行检测，而是 `after(80, redraw)`：连续拖动只在停顿后检测一次，避免滑杆每移动 1 像素都跑一次霍夫变换。验收图尺寸下单次检测为毫秒级，同步执行即可，不需要线程；规模更大的图片可能短暂阻塞界面，属于当前范围外。

### 显示：tkinter 无 Pillow 方案

OpenCV 的 BGR 数组经 `cv2.cvtColor` 转 RGB，再 `cv2.imencode(".ppm", rgb)` 得到 PPM 字节，交给 `tk.PhotoImage(data=...)`。PPM 是 Tk 内置支持的格式，避免引入 Pillow。显示前按预览区可用尺寸等比缩放（`INTER_AREA`），并保存 `PhotoImage` 引用防止被回收。

### 图片读写与路径

`cv2.imread`/`imwrite` 在 Linux 下对非 ASCII 路径不可靠，因此统一使用 `np.fromfile` + `cv2.imdecode` 读取、`cv2.imencode` + `tofile` 写出。导出默认 `.png`；用户未写扩展名时补 `.png`，JPEG 用 `.jpg`/`.jpeg`。

### 验收方式

- 无头：直接调用 `detect_circles` 校验两张图的圆数量与圆心/半径，并把 `annotate` 结果写入 `docs/`。
- 有头：在 WSLg 中启动 GUI，导入两张图、确认实时预览、导出结果并核对状态区。
- 两张图共用一组验收参数，与界面默认值一致：`dp=1.2`、`minDist=300`、`param1=100`、`param2=100`、最小半径 0、最大半径 0（半径 0 表示不限制）。

## Risks / Trade-offs

- **Hough 对参数敏感** → 规格给出两张图的可复现参数；README 记录实际生效值，避免依赖模糊默认值。
- **OpenCV 版本差异** → 验收固定 4.6.0，换版本后需重新确认圆数量与半径。
- **超大图片同步检测阻塞 UI** → 接受当前范围；去抖 80ms 降低重复计算，必要时后续再引入线程。
- **滑杆连续值造成瞬时非法组合** → 参数校验失败只提示并保留上次有效预览，不写入导出。
- **WSLg 不可用时无法验证 GUI** → 核心逻辑可无头验收；GUI 部分在具备显示服务时人工验证并记录。
- **PPM 转换内存开销** → 只在缩放后的显示尺寸上编码，不处理原图全尺寸副本。

## Migration Plan

新功能，无数据迁移。实现完成后更新 README 的运行说明与验收表，并把验收图放入 `docs/`；变更归档时把两份增量规格合并进 `openspec/specs/`。
