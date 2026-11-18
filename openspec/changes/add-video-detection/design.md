# Design

## Context

见 `proposal.md`。现状：

- `src/circle_detector.py` 提供 `HoughParams`、`validate`、`detect_circles`、`annotate`、`load_image`、`save_image`；`detect_circles` 返回 `[(x, y, r)]`，没有结果时返回 `[]`。
- `src/hough_circle_gui.py` 是单图界面：导入图片、六个参数滑杆、80 ms 去抖后自动重检、导出标注图。
- 两张验收图（`examples/coins.jpg` 760×385、`examples/cookie-plate.jpg` 520×520）在默认参数 `dp=1.2, minDist=300, param1=100, param2=100, minRadius=0, maxRadius=0` 下分别得到 2 个与 1 个圆，结果与结果图已写入 README。

## Goals / Non-Goals

**Goals**

- 复用现有检测核心，不复制参数校验与 `HoughCircles` 调用。
- 逐帧结果可核对：帧号、时间戳、圆数量、各圆 `(x, y, r)`，缺测帧留空记录而不是跳过。
- 视频模式与单图模式共存，互不改变对方行为。

**Non-Goals**

- 不做目标跟踪、运动预测与跨帧身份关联。
- 不做相机实时接入、视频转码或剪辑。
- 不改单图模式的默认参数与验收结果。

## Decisions

### 抽帧策略

默认按固定帧间隔抽取（`frame_step`），而不是无条件逐帧检测：常见视频 30–60 fps，逐帧检测会让界面卡顿，也与现有 80 ms 去抖冲突。默认 `frame_step=1`（每帧），由调用方显式放宽。

### 接口（计划）

```python
def iter_video_frames(path: str, frame_step: int = 1) -> Iterator[tuple[int, float, np.ndarray]]
def detect_video(path: str, params: HoughParams, frame_step: int = 1) -> list[dict]
def write_video_results(rows: list[dict], path: str) -> None
```

- `rows` 每条对应一帧：`{"frame": int, "time_s": float, "circles": [(x, y, r), ...]}`；无结果时 `circles` 为空列表，沿用现有"空列表表示没有圆"的约定，不使用 `None`。
- 时间戳 = 帧号 / fps；fps 从 `VideoCapture` 读取，取不到时抛 `ValueError`。

### 与现有代码的边界

- `detect_circles`、`validate`、`annotate`、`load_image`、`save_image` 的签名与语义不改。
- 抽帧失败（文件不存在、编码不支持、读到 0 帧）抛 `ValueError`，与现有 `load_image` 的错误风格一致。
- GUI 只在选定视频源后启用播放控件。

## Risks / Trade-offs

- 逐帧检测仍是每帧一次 `HoughCircles`，长视频耗时线性增长；用 `frame_step` 抽样，不做自适应。
- CSV 中"一帧多圆"的表示方式尚未定稿，它决定后续验收怎么核对（见 Open Questions）。

## Migration Plan

非破坏性：只新增入口与函数，不改现有行为；单图验收参数与结果保持不变。实现完成后按 OpenSpec 流程归档，并把 `video-detection` 能力同步进 `openspec/specs/`。

## Open Questions

- CSV 中一帧多圆怎么表示：同一帧多行（每行一个圆），还是单行内用 JSON 单元格？
- 视频模式是"边检测边写"（流式）还是先全部检测再统一写？前者内存占用低，后者失败时不会留下半份结果。
