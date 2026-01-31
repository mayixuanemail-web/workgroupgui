"""
Excel处理脚本
功能：
1. 读取表头为属的列的数据，将相同字符串对应的reads列值求和
2. 保留相同字符串的第一行，reads列值改为原数据的求和
3. 覆盖原文件
"""
import os
import sys
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
def process_excel(file_path):
    '''
    process_excel 的 Docstring
    
    :param file_path: 说明
    '''
    print(f"Processing: {file_path}")
    # 读取Excel文件
    df = pd.read_excel(file_path)
    # 获取列名
    cols = df.columns.tolist()
    if "属" not in cols or "reads" not in cols:
        print(f"  Error: Required columns '属' or 'reads' not found in the file, skipping...")
        return False
    genus_col = "属"
    read_col = "reads"
    print(f"  Original rows: {len(df)}")
    # 计算每个属对应的reads求和
    sum_values = df.groupby(genus_col)[read_col].sum()
    # 在reads列中更新为求和结果，只保留每个属的第一行
    df = df.drop_duplicates(subset=[genus_col]).copy()
    df[read_col] = df[genus_col].map(sum_values)
    print(f"  Processed rows: {len(df)}")
    # 覆盖原文件
    df.to_excel(file_path, index=False)
    print(f"  File saved with updated '{read_col}' values.")
    return True
def batch_process_excel_in_directory(base_path, success=0, fail=0):
    """
    批量处理指定目录下所有Excel文件
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
                        process_excel(xlsx_file)
                        success += 1
                    except Exception as e:
                        print(f"  Failed to process {xlsx_file}: {e}")
                        fail += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"
    #base_path = r"C:\Users\ma\Desktop\workgroup2\files_debug\1_3_1_3_fastp" 
    success, fail = batch_process_excel_in_directory(Path(base_path))          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")
