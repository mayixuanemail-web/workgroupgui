#读取某个xlsx的某一列单元格值作为参考数据
#从某个目录下所有pdf文件中筛选出文件名包含参考数据的pdf文件
import pandas as pd
import os
from pathlib import Path
import shutil
def attract_pdf_good(file_path, pdf_dir, output_dir, target_col):
    """
    从指定目录下筛选出文件名包含Excel文件中某一列单元格值的PDF文件
    file_path: Excel文件路径
    pdf_dir: PDF文件目录
    output_dir: 筛选后PDF文件输出目录
    target_col: 参考数据所在列名
    """
    print(f"Processing: {file_path}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    if target_col not in df.columns:
        print(f"  Error: Column '{target_col}' not found in the file, skipping...")
        return False
    
    # 获取参考数据列表，去除空值并转换为字符串
    reference_values = df[target_col].dropna().astype(str).tolist()
    
    print(f"  Found {len(reference_values)} reference values in column '{target_col}'")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历PDF目录，筛选符合条件的PDF文件
    for pdf_file in Path(pdf_dir).glob("*.pdf"):
        pdf_name = pdf_file.stem  # 获取不带扩展名的文件名
        for ref_value in reference_values:
            if ref_value in pdf_name:
                # 复制符合条件的PDF文件到输出目录
                shutil.copy(pdf_file, Path(output_dir) / pdf_file.name)
                print(f"  Copied: {pdf_file.name}")
                break  # 找到匹配后跳出内层循环
    
    return True
def batch_attract_pdf_in_directory(base_path, target_col, success=0, fail=0):
    """
    批量筛选指定目录下所有Excel文件中的某一列单元格值，复制符合条件的PDF文件到输出目录
    base_path: 基础路径
    target_col: 参考数据所在列名
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
                if not xlsx_dir.exists():
                    print(f"  Error: Reference file '{xlsx_dir}' not found, skipping...")
                    continue
                # 构建 part_dir / damage_plot 目录路径
                pdf_dir = part_dir / "damage_plots"
                if not pdf_dir.exists():
                    print(f"  Error: PDF directory '{pdf_dir}' not found, skipping...")
                    continue
                # 查找所有xlsx文件
                xlsx_files = [xlsx_dir]
                for xlsx_file in xlsx_files:
                    print(f"\n{'=' * 60}")
                    print(f"{category_dir.name}/{part_dir.name}")
                    try:
                        #output_dir = Path(output_base_dir) / number_dir.name / category_dir.name / part_dir.name
                        attract_pdf_good(xlsx_file, pdf_dir, part_dir, target_col)
                    except Exception as e:
                        print(f"  Error processing file {xlsx_file}: {e}")
                        fail += 1
                    else:
                        success += 1
    return success, fail
if __name__ == "__main__":
    print("=" * 60)
    # 批量处理模式
    base_path = "files_debug"

    target_col = "好"
    success, fail = batch_attract_pdf_in_directory(Path(base_path), target_col)          
    print("\n" + "=" * 60)
    print(f"Batch processing completed. Success: {success}, Failed: {fail}")