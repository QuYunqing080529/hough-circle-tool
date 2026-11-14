"""霍夫圆检测核心：参数校验、检测、标注与图片读写。"""

from dataclasses import dataclass
import os

import cv2
import numpy as np


@dataclass(frozen=True)
class HoughParams:
    """六个霍夫圆参数；半径 0 表示不限制。"""

    dp: float = 1.2
    min_dist: int = 300
    param1: int = 100
    param2: int = 100
    min_radius: int = 0
    max_radius: int = 0


def validate(params: HoughParams) -> str | None:
    """校验参数：合法返回 None，否则返回可读错误说明。"""
    if params.dp <= 0:
        return "dp 必须大于 0"
    if params.min_dist <= 0:
        return "minDist 必须大于 0"
    if params.param1 <= 0:
        return "param1 必须大于 0"
    if params.param2 <= 0:
        return "param2 必须大于 0"
    if params.min_radius < 0:
        return "最小半径不能为负数"
    if params.max_radius < 0:
        return "最大半径不能为负数"
    unlimited = params.min_radius == 0 and params.max_radius == 0
    if not unlimited and params.max_radius <= params.min_radius:
        return "最大半径必须大于最小半径（两者同为 0 表示不限制半径）"
    return None


def detect_circles(image: np.ndarray, params: HoughParams) -> list[tuple[int, int, int]]:
    """检测圆，返回以左上角为原点的 (x, y, r) 列表；无结果时返回空列表。"""
    if image is None or image.size == 0:
        raise ValueError("图片为空")
    error = validate(params)
    if error is not None:
        raise ValueError(error)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=params.dp,
        minDist=params.min_dist,
        param1=params.param1,
        param2=params.param2,
        minRadius=params.min_radius,
        maxRadius=params.max_radius,
    )
    if circles is None:
        return []
    return [(int(round(x)), int(round(y)), int(round(r))) for x, y, r in circles[0]]


def annotate(image: np.ndarray, circles: list[tuple[int, int, int]]) -> np.ndarray:
    """在原图副本上绘制圆周与圆心，返回标注图。"""
    result = image.copy()
    for x, y, r in circles:
        cv2.circle(result, (x, y), r, (0, 255, 0), 2)
        cv2.circle(result, (x, y), 3, (0, 0, 255), -1)
    return result


def load_image(path: str) -> np.ndarray:
    """按 BGR 读取图片；路径使用 np.fromfile 以兼容非 ASCII 字符。"""
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        raise ValueError(f"无法读取图片文件: {path}")
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"无法解码图片文件: {path}")
    return image


def save_image(path: str, image: np.ndarray) -> None:
    """按扩展名编码写出图片；无扩展名时按 PNG 写出。"""
    ext = os.path.splitext(path)[1].lower() or ".png"
    try:
        ok, buffer = cv2.imencode(ext, image)
    except cv2.error as exc:
        raise ValueError(f"不支持的图片格式: {ext}") from exc
    if not ok:
        raise ValueError(f"无法编码图片: {path}")
    buffer.tofile(path)
