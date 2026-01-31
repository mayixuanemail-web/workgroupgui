#1,删除excel文件指定列
#2,批量删除指定目录下所有Excel文件中的某一列，如A列
import pandas as pd 
from pathlib import Path
def delete_excel_column(file_path, col_name):
    """
    删除Excel文件中的指定列
    file_path: Excel文件路径
    col_name: 需要删除的列
    """
    print(f"Processing: {file_path}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    if col_name not in df.columns:
        print(f"  Error: Column '{col_name}' not found in the file, skipping...")
        return False
    
    print(f"  Deleting column: {col_name}")
    
    # 删除指定列
    df.drop(columns=[col_name], inplace=True)
    
    # 覆盖原文件
    df.to_excel(file_path, index=False)
    print(f"  Column '{col_name}' deleted and file saved.")
    return True 

def batch_delete_column_in_directory(base_path, col_name, success=0, fail=0):
    """
    批量删除指定目录下所有Excel文件中的某一列
    
    base_path: 基础路径
    target_subpath: 目标子路径（相对于base_path）
    col_name: 需要删除的列名
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
                #table_dir = Path(r"C:\Users\ma\Desktop\workspace\1_5_1_43_fastp\Bacteria\part10\species_taxonomy_table")
                if not table_dir.exists():
                    continue
                # 查找所有xlsx文件
                xlsx_files = list(table_dir.glob("*.xlsx")) 
                for xlsx_file in xlsx_files:
                    print(f"\n{'=' * 60}")
                    print(f"{category_dir.name}/{part_dir.name}")
                    try:
                        delete_excel_column(xlsx_file, col_name)
                        success += 1
                    except Exception as e:
                        print(f"  Error: {e}")
                        fail += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"
    
    col_name = "taxid"
    #col_name = "种"
    success, fail = batch_delete_column_in_directory(Path(base_path), col_name)          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")
    print("=" * 60)