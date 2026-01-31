#将该excel文件的第一行设为表头
import pandas as pd 
import openpyxl
import os   
from pathlib import Path
def set_excel_title(file_path):
    """
    将Excel文件的第一行设为表头
    file_path: Excel文件路径
    """
    print(f"Processing: {file_path}")
    
    # 读取Excel文件，指定header=0表示第一行作为表头
    df = pd.read_excel(file_path, header=0)
    
    print(f"  Setting first row as header")
    
    # 覆盖原文件
    df.to_excel(file_path, index=False)
    print(f"  First row set as header and file saved.")
    return True
def batch_set_title_in_directory(base_path, success=0, fail=0):
    """
    批量将指定目录下所有Excel文件的第一行设为表头
    base_path: 基础路径
    """
    # 遍历所有类别目录 (xxxx)
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
                # 构建 part_dir / number.category.partxx.分类结果.xlsx 目录路径
                number=number_dir.name
                category=category_dir.name
                part=part_dir.name
                xlsx_dir = part_dir / f"{number}.{category}.{part}.分类结果.xlsx"
                
                try:
                    set_excel_title(xlsx_dir)
                    success += 1
                except Exception as e:
                    print(f"  Failed to process {xlsx_dir}: {e}")
                    fail += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"
    success, fail = batch_set_title_in_directory(Path(base_path))          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")    