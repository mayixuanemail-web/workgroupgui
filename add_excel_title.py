#为某一列命名为name
#如A列命名为"Kingdom"
import pandas as pd
import openpyxl 
import os
from pathlib import Path
def add_excel_title(file_path, new_title):
    """
    为Excel文件中指定列命名为新标题
    file_path: Excel文件路径
    new_title: 新的列标题
    """
    print(f"Processing: {file_path}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    print(f"  Adding new column with title: {new_title}")
    # 在最右侧插入新列，表头为“中文属名”
    df.insert(len(df.columns), new_title, "")
    
    # 覆盖原文件
    df.to_excel(file_path, index=False)
    print(f"  Column '{new_title}' added and file saved.")
    return True
def batch_add_title_in_directory(base_path, new_title, success=0, fail=0):
    """
    批量为指定目录下所有Excel文件中的某一列命名新标题   
    base_path: 基础路径
    new_title: 新的列标题
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
                
                # 构建 species_taxonomy_table 目录路径
                table_dir = part_dir / "species_taxonomy_table"
                if not table_dir.exists():
                    continue
                # 查找所有xlsx文件
                xlsx_files = list(table_dir.glob("*.xlsx")) 
                for xlsx_file in xlsx_files:
                    print(f"\n{'=' * 60}")
                    print(f"{category_dir.name}/{part_dir.name}")
                    try:
                        add_excel_title(xlsx_file, new_title)
                        success += 1
                    except Exception as e:
                        print(f"  Failed to process {xlsx_file}: {e}")
                        fail += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"  # 使用相对路径
    new_title = "中文属名"
    success, fail = batch_add_title_in_directory(Path(base_path), new_title)          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")
    '''
    new_title_ = "中文种名"
    success, fail = batch_add_title_in_directory(Path(base_path), new_title_)          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")
    '''