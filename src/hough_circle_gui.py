"""带 tkinter 界面的霍夫圆检测工具。"""

import os

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

from circle_detector import (
    HoughParams,
    annotate,
    detect_circles,
    load_image,
    save_image,
    validate,
)

PREVIEW_WIDTH = 760
PREVIEW_HEIGHT = 520
DEBOUNCE_MS = 80

IMAGE_FILE_TYPES = [
    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
    ("所有文件", "*.*"),
]


class HoughCircleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("霍夫圆检测")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._image: np.ndarray | None = None
        self._annotated: np.ndarray | None = None
        self._circles: list[tuple[int, int, int]] = []
        self._source_path = ""
        self._photo: tk.PhotoImage | None = None
        self._detect_job: str | None = None
        self._render_job: str | None = None
        self._scales: dict[str, tk.Scale] = {}

        self._build_preview()
        self._build_controls()
        self._build_status()

    # ---- 界面搭建 ----

    def _build_preview(self) -> None:
        container = tk.Frame(
            self.root,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            bg="#202020",
        )
        container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        container.grid_propagate(False)
        container.pack_propagate(False)
        self._preview = tk.Label(
            container, bg="#202020", fg="#cccccc", text="请导入图片"
        )
        self._preview.pack(fill="both", expand=True)
        self._preview.bind("<Configure>", self._on_preview_resize)

    def _build_controls(self) -> None:
        panel = tk.Frame(self.root)
        panel.grid(row=0, column=1, sticky="n", padx=(0, 12), pady=8)
        panel.columnconfigure(1, weight=1)

        tk.Label(panel, text="HoughCircles 参数", anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        defaults = HoughParams()
        specs = [
            ("dp", "dp", 1.0, 3.0, 0.1, defaults.dp),
            ("minDist", "minDist", 1, 1000, 1, defaults.min_dist),
            ("param1", "param1", 1, 500, 1, defaults.param1),
            ("param2", "param2", 1, 300, 1, defaults.param2),
            ("minRadius", "最小半径", 0, 1000, 1, defaults.min_radius),
            ("maxRadius", "最大半径", 0, 1000, 1, defaults.max_radius),
        ]
        for index, (key, label, low, high, step, default) in enumerate(specs, start=1):
            tk.Label(panel, text=label, anchor="w").grid(
                row=index, column=0, sticky="w", padx=(0, 6)
            )
            scale = tk.Scale(
                panel,
                from_=low,
                to=high,
                resolution=step,
                orient="horizontal",
                length=200,
                command=self._on_param_change,
            )
            scale.set(default)
            scale.grid(row=index, column=1, sticky="ew")
            self._scales[key] = scale

        row = len(specs) + 2
        tk.Button(panel, text="导入图片", command=self._choose_image).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(12, 4)
        )
        self._export_button = tk.Button(
            panel,
            text="导出标注图",
            command=self._export_image,
            state="disabled",
        )
        self._export_button.grid(row=row + 1, column=0, columnspan=2, sticky="ew")

    def _build_status(self) -> None:
        self._status = tk.StringVar(value="就绪：请导入图片")
        self._status_label = tk.Label(
            self.root, textvariable=self._status, anchor="w", fg="#333333"
        )
        self._status_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8)
        )

    # ---- 参数与检测 ----

    def _current_params(self) -> HoughParams:
        return HoughParams(
            dp=float(self._scales["dp"].get()),
            min_dist=int(round(float(self._scales["minDist"].get()))),
            param1=int(round(float(self._scales["param1"].get()))),
            param2=int(round(float(self._scales["param2"].get()))),
            min_radius=int(round(float(self._scales["minRadius"].get()))),
            max_radius=int(round(float(self._scales["maxRadius"].get()))),
        )

    def _on_param_change(self, _value: str | None = None) -> None:
        self._schedule_detect()

    def _schedule_detect(self) -> None:
        if self._image is None:
            return
        if self._detect_job is not None:
            self.root.after_cancel(self._detect_job)
        self._detect_job = self.root.after(DEBOUNCE_MS, self._detect_now)

    def _detect_now(self) -> None:
        self._detect_job = None
        if self._image is None:
            return

        params = self._current_params()
        error = validate(params)
        if error is not None:
            self._set_error(f"参数错误：{error}")
            if self._annotated is None:
                self._render_preview()
                self._export_button.config(state="disabled")
            return
        try:
            circles = detect_circles(self._image, params)
        except ValueError as exc:
            self._set_error(f"检测失败：{exc}")
            return

        self._circles = circles
        self._annotated = annotate(self._image, circles)
        self._export_button.config(state="normal")
        self._render_preview()
        self._set_status(f"{self._source_path} · 检测到 {len(circles)} 个圆")

    # ---- 预览与显示 ----

    def _on_preview_resize(self, _event: tk.Event | None = None) -> None:
        if self._image is None:
            return
        if self._render_job is not None:
            self.root.after_cancel(self._render_job)
        self._render_job = self.root.after(DEBOUNCE_MS, self._render_preview)

    def _render_preview(self) -> None:
        self._render_job = None
        source = self._annotated if self._annotated is not None else self._image
        if source is None:
            return

        max_w = self._preview.winfo_width()
        max_h = self._preview.winfo_height()
        if max_w <= 1 or max_h <= 1:
            max_w, max_h = PREVIEW_WIDTH, PREVIEW_HEIGHT

        height, width = source.shape[:2]
        scale = min(max_w / width, max_h / height)
        if scale < 1.0:
            size = (max(1, int(width * scale)), max(1, int(height * scale)))
            display = cv2.resize(source, size, interpolation=cv2.INTER_AREA)
        else:
            display = source

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        ok, buffer = cv2.imencode(".ppm", rgb)
        if not ok:
            self._set_error("预览编码失败")
            return
        self._photo = tk.PhotoImage(data=buffer.tobytes())
        self._preview.config(image=self._photo, text="")

    def _set_status(self, text: str) -> None:
        self._status.set(text)
        self._status_label.config(fg="#333333")

    def _set_error(self, text: str) -> None:
        self._status.set(text)
        self._status_label.config(fg="#b00020")

    # ---- 导入与导出 ----

    def _choose_image(self) -> None:
        path = filedialog.askopenfilename(title="选择图片", filetypes=IMAGE_FILE_TYPES)
        if path:
            self._load_path(path)

    def _load_path(self, path: str) -> bool:
        """读取图片并立即检测；失败时保留原有图片状态。"""
        try:
            image = load_image(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("读取失败", str(exc))
            self._set_error(f"读取失败：{exc}")
            return False

        if self._detect_job is not None:
            self.root.after_cancel(self._detect_job)
            self._detect_job = None
        self._image = image
        self._source_path = path
        self._annotated = None
        self._circles = []
        self._detect_now()
        return True

    def _export_image(self) -> None:
        if self._annotated is None:
            return
        base = os.path.splitext(os.path.basename(self._source_path))[0]
        path = filedialog.asksaveasfilename(
            title="导出标注图",
            defaultextension=".png",
            initialfile=f"{base}-annotated.png",
            filetypes=[
                ("PNG 图片", "*.png"),
                ("JPEG 图片", "*.jpg *.jpeg"),
                ("所有文件", "*.*"),
            ],
        )
        if path:
            self._export_to(path)

    def _export_to(self, path: str) -> bool:
        """按原图分辨率写出当前标注图；失败时提示并返回 False。"""
        if self._annotated is None:
            self._set_error("没有可导出的标注图")
            return False
        if not os.path.splitext(path)[1]:
            path += ".png"
        try:
            save_image(path, self._annotated)
        except (OSError, ValueError, cv2.error) as exc:
            messagebox.showerror("导出失败", str(exc))
            self._set_error(f"导出失败：{exc}")
            return False
        self._set_status(f"已导出：{path}")
        messagebox.showinfo("导出成功", f"已保存到：\n{path}")
        return True


def main() -> None:
    root = tk.Tk()
    HoughCircleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
