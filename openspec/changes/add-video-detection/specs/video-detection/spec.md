# Spec Delta

## Purpose

为现有霍夫圆检测工具增加视频输入能力：按固定帧间隔抽取画面，逐帧复用现有检测核心，产出可核对、可复现的逐帧结果，并明确"没有检测到"同样是需要记录的结果。

## ADDED Requirements

### Requirement: 视频抽帧
系统 MUST 能从本地视频文件按固定帧间隔抽取画面，并 MUST 为每帧提供从 0 开始的帧号、以秒为单位的时间戳与该帧图像。

#### Scenario: 按间隔抽帧
- **WHEN** 对一段 30 fps 的视频以 `frame_step=5` 抽帧
- **THEN** 得到的帧号序列为 0、5、10…，且每帧时间戳等于帧号除以 30

#### Scenario: 视频无法解码
- **WHEN** 传入的不是可解码的视频文件
- **THEN** 系统抛出可读的 `ValueError`，且不产生部分结果

### Requirement: 逐帧检测复用
系统 MUST 对每个抽到的帧调用现有单帧检测逻辑（同一套参数校验与 `HoughCircles` 调用），并 MUST NOT 改变单帧检测的语义。

#### Scenario: 与单图结果一致
- **WHEN** 对某一帧执行视频模式检测
- **THEN** 该帧的检测结果与直接对该帧执行单图检测所得结果完全相同

### Requirement: 逐帧结果记录
系统 MUST 为每个抽到的帧输出一条记录，包含帧号、时间戳、圆数量与各圆 `(x, y, r)`；没有检测到圆的帧 MUST 仍然记录，并以空结果表示。

#### Scenario: 目标离开画面
- **WHEN** 某帧中不再存在可检测的圆
- **THEN** 该帧仍有记录，圆数量为 0，而不是被跳过或记为空值

### Requirement: 单图模式回归
新增视频能力 MUST NOT 改变现有单图模式的行为：默认参数、检测结果与导出结果保持不变。

#### Scenario: 两张验收图结果不变
- **WHEN** 使用默认参数对 `examples/coins.jpg` 与 `examples/cookie-plate.jpg` 执行单图检测
- **THEN** 仍分别得到 2 个与 1 个圆，圆心与半径与 README 记录一致
