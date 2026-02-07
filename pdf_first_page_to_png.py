"""
将指定目录下所有 PDF 的第一页导出为 PNG。

依赖：PyMuPDF (fitz)
安装：pip install pymupdf

用法：
    直接运行脚本前，先在下方配置 BASE_INPUT_DIR / BASE_OUTPUT_DIR
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


def export_first_page_to_png(pdf_path: Path, output_dir: Path, dpi: int = 200) -> Path:
    """导出单个 PDF 的第一页为 PNG，返回输出文件路径。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_path.stem}.png"

    with fitz.open(pdf_path) as doc:
        if doc.page_count == 0:
            return output_path
        page = doc.load_page(0)
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(output_path.as_posix())

    return output_path


def batch_export_pdfs(base_dir: Path, dpi: int = 200) -> None:
    for number_dir in sorted(base_dir.iterdir()):
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
                output_subdir = base_dir/number/category/part_dir.name / f"{number}_{category}_{part_dir.name}_img"
                for pdf_file in sorted(part_dir.glob("*.pdf")):
                    try:
                        output_path = export_first_page_to_png(pdf_file, output_subdir, dpi)
                        print(f"  ✅ Exported: {output_path}")
                    except Exception as e:
                        print(f"  ❌ Failed to export {pdf_file}: {e}")


OUTPUT_DPI = 200

if __name__ == "__main__":
    BASE_DIR = "files_debug"
    batch_export_pdfs(Path(BASE_DIR), dpi=OUTPUT_DPI)