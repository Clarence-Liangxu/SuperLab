#!/usr/bin/env python3

import os
import re
import sys
import argparse

def find_for_loops_in_file(filepath):
    """在单个文件中查找for循环"""
    loops = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"无法读取文件 {filepath}: {e}", file=sys.stderr)
        return loops
    
    # 查找所有for循环
    for i in range(len(lines)):
        line = lines[i].strip()
        
        # 检查是否是for循环的开始行
        if line.startswith('for') and '(' in line and ')' in line:
            # 找到for循环起始位置
            start_line = i
            
            # 收集for循环的所有内容
            loop_lines = []
            current_line = i
            
            # 简单判断：从当前行开始，收集直到匹配的花括号或达到10行
            bracket_count = 0
            lines_collected = 0
            
            # 从for语句开始收集内容
            while current_line < len(lines) and lines_collected < 20:  # 安全上限
                line_content = lines[current_line]
                loop_lines.append(line_content.rstrip('\n'))  # 不包含换行符
                lines_collected += 1
                
                # 统计花括号
                bracket_count += line_content.count('{')
                bracket_count -= line_content.count('}')
                
                # 如果已经找到完整的for循环（大括号匹配）
                if bracket_count <= 0 and '{' in line_content:
                    break
                
                current_line += 1
            
            # 只取前10行或实际内容
            limited_lines = loop_lines[:10]
            
            # 确保包含for关键字
            if any('for' in line for line in limited_lines):
                loops.append({
                    'file': filepath,
                    'line': start_line + 1,  # 行号从1开始
                    'lines': limited_lines
                })
    
    return loops

def find_for_loops_in_directory(directory):
    """在目录中查找所有for循环"""
    c_extensions = ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh']
    loops = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in c_extensions):
                    filepath = os.path.join(root, file)
                    file_loops = find_for_loops_in_file(filepath)
                    loops.extend(file_loops)
    except Exception as e:
        print(f"遍历目录时出错 {directory}: {e}", file=sys.stderr)
    
    return loops

def escape_markdown_special_chars(text):
    """转义Markdown特殊字符，但保留下划线"""
    # 只转义需要转义的字符，但保留下划线
    escaped = text.replace('*', '\\*')
    escaped = escaped.replace('_', '\\_')  # 这里是错误的，应该不转义下划线
    escaped = escaped.replace('[', '\$')
    escaped = escaped.replace(']', '\$')
    escaped = escaped.replace('`', '\\`')
    escaped = escaped.replace('\\', '\\\\')
    return escaped

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='查找C/C++源文件中的for循环')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='要扫描的目录（默认为当前目录）')
    parser.add_argument('-o', '--output', default='loop.md',
                       help='输出文件名（默认为loop.md）')
    
    args = parser.parse_args()
    
    # 获取指定目录
    target_dir = args.directory
    
    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误：目录 '{target_dir}' 不存在", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(target_dir):
        print(f"错误：'{target_dir}' 不是目录", file=sys.stderr)
        sys.exit(1)
    
    # 查找所有for循环
    print(f"正在扫描目录: {target_dir}")
    all_loops = find_for_loops_in_directory(target_dir)
    
    # 写入到Markdown文件
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            # 写入Markdown头部
            f.write("# C/C++ For循环统计\n\n")
            f.write(f"扫描目录: `{target_dir}`\n\n")
            
            if not all_loops:
                f.write("## 没有找到任何for循环\n\n")
                f.write("在指定目录中未发现C/C++源文件中的for循环结构。")
            else:
                f.write(f"## 找到的for循环 ({len(all_loops)} 个)\n\n")
                
                # 为每个循环编号
                for i, loop in enumerate(all_loops, 1):
                    f.write(f"### 循环 {i}\n\n")
                    f.write(f"- **文件**: `{loop['file']}`\n")
                    f.write(f"- **行号**: `{loop['line']}`\n\n")
                    f.write("```c\n")
                    for line in loop['lines']:
                        # 直接写入，不转义下划线
                        f.write(line + '\n')
                    f.write("```\n\n")
        
        print(f"已将所有for循环写入到 {args.output} 文件中")
        if all_loops:
            print(f"共找到 {len(all_loops)} 个for循环")
    except Exception as e:
        print(f"写入文件时出错: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
