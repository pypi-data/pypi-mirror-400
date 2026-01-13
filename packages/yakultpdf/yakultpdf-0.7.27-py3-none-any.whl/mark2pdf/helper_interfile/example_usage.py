#!/usr/bin/env python3

"""
mark2pdf.helper_interfile 使用示例
"""

from pathlib import Path

from mark2pdf.helper_interfile.interfile_manager import (
    cleanup_tmpfile,
    create_md_tmpfile,
    write_to_tmpfile,
)


def example_usage():
    """示例用法"""

    # 创建一个测试文件
    test_file = "test_input.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("# Original Content\n\nThis is the original markdown file.")

    print(f"📄 创建测试文件：{test_file}")

    try:
        # 1. 创建临时文件
        temp_fd, temp_path = create_md_tmpfile(test_file, prefix="example_")
        print(f"✅ 创建临时文件：{temp_path}")

        # 2. 写入处理后的内容
        processed_content = "# Processed Content\n\nThis is processed markdown content."
        write_to_tmpfile(temp_fd, processed_content)
        print("✅ 成功写入临时文件")

        # 验证写入的内容
        with open(temp_path, encoding="utf-8") as f:
            content = f.read()
        print(f"📝 临时文件内容:\n{content}")

    finally:
        # 3. 清理临时文件
        if "temp_path" in locals():
            cleanup_tmpfile(temp_path)
            print("✅ 成功清理临时文件")

        # 清理测试文件
        if Path(test_file).exists():
            Path(test_file).unlink()
            print("✅ 清理测试文件")


if __name__ == "__main__":
    example_usage()
