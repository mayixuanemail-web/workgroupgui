"""
PDF 首页转 PNG 产生的临时图片清理工具

功能：
- 删除 pdf_first_page_to_png.py 产生的所有临时 PNG 图片
- 清理格式为 "{number}_{category}_{part}_img" 的图片目录
- 显示清理详情和统计信息
"""

from pathlib import Path
import os


# ======== 配置区域（按需修改）========
# pdf_first_page_to_png 产生的图片所在的基目录
BASE_DIRS = [
    Path("files_debug"),
    Path("files_origin"),
    Path("files_origin1"),
]

# 图片子目录命名模式（通常是 {number}_{category}_{part}_img）
IMG_SUBDIR_PATTERN = "_img"

# =====================================


def find_image_subdirs(base_dir: Path) -> list:
    """递归查找符合 pdf_first_page_to_png 命名规则的图片子目录"""
    image_dirs = []
    
    if not base_dir.exists():
        return image_dirs
    
    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        # 检查目录名称是否以 "_img" 结尾
        if IMG_SUBDIR_PATTERN in root_path.name:
            image_dirs.append(root_path)
    
    return image_dirs


def delete_images_in_dir(dir_path: Path) -> tuple[int, int]:
    """删除指定目录中的所有 PNG 文件
    
    Returns:
        (成功删除数, 失败数)
    """
    success_count = 0
    fail_count = 0
    
    try:
        for file in dir_path.iterdir():
            if file.is_file() and file.suffix.lower() == ".png":
                try:
                    file.unlink()
                    print(f"  ✅ 删除: {file.name}")
                    success_count += 1
                except Exception as e:
                    print(f"  ❌ 删除失败: {file.name} - {e}")
                    fail_count += 1
        # 删除完图片后，若目录为空则删除目录
        if not any(dir_path.iterdir()):
            try:
                dir_path.rmdir()
                print(f"  🗑️ 目录已删除: {dir_path}")
            except Exception as e:
                print(f"  ⚠️ 目录删除失败: {dir_path} - {e}")
    except Exception as e:
        print(f"  ❌ 访问目录出错: {e}")
    return success_count, fail_count


def main():
    """主函数"""
    print("=" * 70)
    print("🧹 PDF 首页转 PNG 产生的图片清理工具")
    print("=" * 70)
    print()
    
    total_deleted = 0
    total_failed = 0
    total_dirs = 0
    
    for base_dir in BASE_DIRS:
        if not base_dir.exists():
            print(f"⚠️ 目录不存在: {base_dir}")
            continue
        
        print(f"📂 扫描目录: {base_dir}")
        
        # 查找图片子目录
        image_dirs = find_image_subdirs(base_dir)
        
        if not image_dirs:
            print(f"  ℹ️ 未找到符合规则的图片目录\n")
            continue
        
        print(f"  找到 {len(image_dirs)} 个图片目录")
        
        for img_dir in image_dirs:
            print(f"  📁 处理: {img_dir}")
            deleted, failed = delete_images_in_dir(img_dir)
            
            if deleted > 0:
                print(f"     💯 成功删除 {deleted} 个 PNG 文件")
            if failed > 0:
                print(f"     ⚠️ 删除失败 {failed} 个文件")
            
            if deleted > 0 or failed > 0:
                total_deleted += deleted
                total_failed += failed
                total_dirs += 1
        
        print()
    
    # 统计信息
    print("=" * 70)
    print("📊 清理统计")
    print("=" * 70)
    print(f"已处理目录数: {total_dirs}")
    print(f"成功删除文件: {total_deleted}")
    print(f"删除失败文件: {total_failed}")
    
    if total_deleted > 0:
        print()
        print(f"✅ 清理完成！共删除 {total_deleted} 个 PNG 图片文件")
    else:
        print()
        print("ℹ️ 未找到需要清理的 PNG 图片文件")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
