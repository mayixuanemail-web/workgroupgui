"""
根据网格参数读取颜色信息（复用 image_point_color_check 的算法）。

依赖：Pillow
安装：pip install pillow

坐标系说明：
- 原点 (0, 0) 位于图像的左上角
- X轴向右增加
- Y轴向下增加
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple
import shutil

from PIL import Image


def read_grid_colors(
    image_path: Path,
    grid_origin: Tuple[float, float],
    grid_step_x: float,
    grid_step_y: float,
    grid_cols: int,
    grid_rows: int,
    grid_x_start: int,
    grid_y_start: int,
    white_threshold: int = 220,
) -> int:
    """
    按网格逐列扫描，统计有色格点数目。

    坐标系：原点在图像左上角 (0,0)，X向右增加，Y向下增加
    - grid_origin: (x, y) 网格原点在图像中的像素坐标
    - grid_step_x: 网格列间距（像素）
    - grid_step_y: 网格行间距（像素）
    - grid_cols: 网格列数
    - grid_rows: 网格行数
    - grid_x_start: 网格坐标系的起始列号
    - grid_y_start: 网格坐标系的起始行号

    返回值：有色格点的数目（整数）
    """
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width, height = img.size
    ox, oy = grid_origin

    def get_pixel_color(x: float, y: float) -> Tuple[int, int, int]:
        xi = round(x)
        yi = round(y)
        xi = max(0, min(xi, width - 1))
        yi = max(0, min(yi, height - 1))
        return pixels[xi, yi][:3]

    def is_white(r: int, g: int, b: int) -> bool:
        return r >= white_threshold and g >= white_threshold and b >= white_threshold

    colored_count = 0
    for col in range(grid_cols):
        for row in range(grid_rows):
            x = ox + col * grid_step_x
            y = oy - row * grid_step_y
            r, g, b = get_pixel_color(x, y)
            if not is_white(r, g, b):
                colored_count += 1
                break

    return colored_count


def calculate_colorless_percentage(
    image_path: Path,
    rect_left: int,
    rect_top: int,
    rect_right: int,
    rect_bottom: int,
    white_threshold: int = 220,
) -> float:
    """
    计算矩形区域内无色（白色）像素的百分比。

    坐标系：原点在图像左上角 (0,0)
    - rect_left: 矩形左边界像素坐标（X轴，向右增加）
    - rect_top: 矩形上边界像素坐标（Y轴，向下增加）
    - rect_right: 矩形右边界像素坐标（不包含）
    - rect_bottom: 矩形下边界像素坐标（不包含）
    - white_threshold: 白色判定阈值（默认220，RGB都大于等于此值认为是白色）

    返回值：
    - 无色像素占整个矩形的百分比（0-100）

    示例：
        # 获取图像左上角到(300,300)的矩形内无色百分比
        percentage = calculate_colorless_percentage(
            image_path=Path("image.png"),
            rect_left=0, rect_top=0, rect_right=300, rect_bottom=300
        )
    """
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width, height = img.size

    # 边界处理
    rect_left = max(0, rect_left)
    rect_top = max(0, rect_top)
    rect_right = min(width, rect_right)
    rect_bottom = min(height, rect_bottom)

    if rect_left >= rect_right or rect_top >= rect_bottom:
        return 0.0

    colorless_count = 0
    total_count = 0

    for y in range(rect_top, rect_bottom):
        for x in range(rect_left, rect_right):
            r, g, b = pixels[x, y][:3]
            total_count += 1
            # 判断是否为白色（无色）
            if r >= white_threshold and g >= white_threshold and b >= white_threshold:
                colorless_count += 1

    if total_count == 0:
        return 0.0

    percentage = (colorless_count / total_count) * 100
    return round(percentage, 2)


def batch_process_images(base_path: Path):
    GRID_ORIGIN = (193.5, 568)
    GRID_STEP_X = 23.15
    GRID_STEP_Y = 20.0
    GRID_COLS = 25
    GRID_ROWS = 25
    GRID_X_START = 1
    GRID_Y_START = 0
    WHITE_THRESHOLD = 240

    GRID2_ENABLE = True
    GRID2_ORIGIN = (840, 568)
    GRID2_STEP_X = 23.15
    GRID2_STEP_Y = 20.0
    GRID2_COLS = 25
    GRID2_ROWS = 25
    GRID2_X_START = 1
    GRID2_Y_START = 0
    for number_dir in sorted(base_path.iterdir()):
        if not number_dir.is_dir():
            continue
        for category_dir in sorted(number_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            # 遍历所有 partxx 目录
            for part_dir in sorted(category_dir.iterdir()):
                if not part_dir.is_dir() or not part_dir.name.startswith("part"):
                    continue
                # 构建 part_dir / number_category_partxx_img 目录路径
                number = number_dir.name
                category = category_dir.name
                img_subdir = base_path/number/category/part_dir.name / f"{number}_{category}_{part_dir.name}_img"
                #清空非常好文件夹
                target_dir = part_dir / "非常好"
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                if not img_subdir.exists():
                    continue
                for img_file in sorted(img_subdir.glob("*.png")):
                    print(f"Processing image: {img_file}")
                    grid1_colors = read_grid_colors(
                        img_file,
                        GRID_ORIGIN,
                        GRID_STEP_X,
                        GRID_STEP_Y,
                        GRID_COLS,
                        GRID_ROWS,
                        GRID_X_START,
                        GRID_Y_START,
                        white_threshold=WHITE_THRESHOLD,
                    )
                    print(f"  Grid 1 colored points: {grid1_colors}")

                    grid2_colors = 0
                    if GRID2_ENABLE:
                        grid2_colors = read_grid_colors(
                            img_file,
                            GRID2_ORIGIN,
                            GRID2_STEP_X,
                            GRID2_STEP_Y,
                            GRID2_COLS,
                            GRID2_ROWS,
                            GRID2_X_START,
                            GRID2_Y_START,
                            white_threshold=WHITE_THRESHOLD,
                        )
                        print(f"  Grid 2 colored points: {grid2_colors}")

                    total_colored = grid1_colors + grid2_colors
                    print(f"  Total colored points in both grids: {total_colored}")
                    if total_colored >= 6:
                        # 复制同名PDF到“非常好”文件夹
                        target_dir = part_dir / "非常好"
                        target_dir.mkdir(parents=True, exist_ok=True)
                        pdf_path = part_dir / (img_file.stem + ".pdf")
                        if pdf_path.exists():
                            shutil.copy2(pdf_path, target_dir / pdf_path.name)
                            print(f"  ✅ Copied PDF to: {target_dir / pdf_path.name}")
                        else:
                            print(f"  ⚠️ PDF not found for image: {pdf_path}")
                    if total_colored <= 2:
                        continue
                    if total_colored <= 5 and total_colored >= 3:
                        rect_colorless = calculate_colorless_percentage(
                            img_file,
                            rect_left=193,
                            rect_top=570,
                            rect_right=1400,
                            rect_bottom=640,
                            white_threshold=WHITE_THRESHOLD,
                        )
                        if rect_colorless <= 93.7:
                            # 复制同名PDF到“非常好”文件夹
                            target_dir = part_dir / "非常好"
                            target_dir.mkdir(parents=True, exist_ok=True)
                            pdf_path = part_dir / (img_file.stem + ".pdf")
                            if pdf_path.exists():
                                shutil.copy2(pdf_path, target_dir / pdf_path.name)
                                print(f"  ✅ Copied PDF to: {target_dir / pdf_path.name}")
                            else:
                                print(f"  ⚠️ PDF not found for image: {pdf_path}")
                         
if __name__ == "__main__":
    # 示例：按需替换为自己的参数（与 image_point_color_check 一致）
    BASE_PATH = Path("files_debug")
    batch_process_images(BASE_PATH)

