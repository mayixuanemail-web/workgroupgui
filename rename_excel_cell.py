#批量重命名某列所有单元格为category_dir的category名
import pandas as pd
import openpyxl
import os   
from pathlib import Path
def rename_excel_cell(file_path, col_name, new_value):
    """
    重命名Excel文件中指定列的所有单元格为新值
    file_path: Excel文件路径
    col_name: 需要重命名的列
    new_value: 新的单元格值
    """
    print(f"Processing: {file_path}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    if col_name not in df.columns:
        print(f"  Error: Column '{col_name}' not found in the file, skipping...")
        return False
    
    print(f"  Renaming all cells in column: {col_name} to '{new_value}'")
    
    # 重命名指定列的所有单元格
    df[col_name] = new_value
    
    # 覆盖原文件
    df.to_excel(file_path, index=False)
    print(f"  Column '{col_name}' cells renamed and file saved.")
    return True
def batch_rename_column_in_directory(base_path, col_name, success=0, fail=0):
    """
    批量重命名指定目录下所有Excel文件中的某一列的单元格
    base_path: 基础路径     
    col_name: 需要重命名的列名
    new_value: 新的单元格值
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
                        rename_excel_cell(xlsx_file, col_name, category_dir.name)
                        success += 1
                    except Exception as e:
                        print(f"  Error processing file: {e}")
                        fail += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"
    col_name = "界"
    
    success, fail = batch_rename_column_in_directory(Path(base_path), col_name)          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")