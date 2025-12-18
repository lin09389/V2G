#!/usr/bin/env python3
"""
前端资源压缩脚本
用于压缩CSS和JavaScript文件，替代Vite的功能
"""

import os
import re
import shutil
from datetime import datetime


def read_file(file_path):
    """读取文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path, content):
    """写入文件内容"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def compress_css(css_content):
    """压缩CSS内容
    - 移除注释
    - 移除多余的空格和换行
    - 优化选择器和属性
    """
    # 移除CSS注释
    css_content = re.sub(r'\/\*[\s\S]*?\*\/', '', css_content)
    
    # 移除多余的空格和换行
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r'\s*{\s*', '{', css_content)
    css_content = re.sub(r'\s*}\s*', '}', css_content)
    css_content = re.sub(r'\s*:\s*', ':', css_content)
    css_content = re.sub(r'\s*;\s*', ';', css_content)
    css_content = re.sub(r';}', '}', css_content)
    
    # 移除行首和行尾的空格
    css_content = css_content.strip()
    
    return css_content


def compress_js(js_content):
    """压缩JavaScript内容
    - 移除注释
    - 移除多余的空格和换行
    - 优化代码格式
    """
    # 移除单行注释
    js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
    
    # 移除多行注释
    js_content = re.sub(r'\/\*[\s\S]*?\*\/', '', js_content)
    
    # 移除多余的空格和换行
    js_content = re.sub(r'\s+', ' ', js_content)
    js_content = re.sub(r'\s*{\s*', '{', js_content)
    js_content = re.sub(r'\s*}\s*', '}', js_content)
    js_content = re.sub(r'\s*\(\s*', '(', js_content)
    js_content = re.sub(r'\s*\)\s*', ')', js_content)
    js_content = re.sub(r'\s*\.\s*', '.', js_content)
    js_content = re.sub(r'\s*,\s*', ',', js_content)
    js_content = re.sub(r'\s*;\s*', ';', js_content)
    
    # 移除行首和行尾的空格
    js_content = js_content.strip()
    
    return js_content


def create_build_directory():
    """创建构建目录"""
    build_dir = "build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    os.makedirs(os.path.join(build_dir, "styles"), exist_ok=True)
    os.makedirs(os.path.join(build_dir, "utils"), exist_ok=True)
    os.makedirs(os.path.join(build_dir, "pages"), exist_ok=True)
    return build_dir


def process_file(file_path, build_dir):
    """处理单个文件"""
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # 构建输出路径
    rel_path = os.path.relpath(file_path, os.getcwd())
    output_path = os.path.join(build_dir, rel_path)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    content = read_file(file_path)
    
    if file_ext == ".css":
        # 压缩CSS文件
        compressed_content = compress_css(content)
        write_file(output_path, compressed_content)
        original_size = len(content.encode('utf-8'))
        compressed_size = len(compressed_content.encode('utf-8'))
        print(f"✓ 压缩CSS: {file_path} ({original_size} → {compressed_size} bytes, 压缩率: {((original_size - compressed_size) / original_size * 100):.1f}%)")
    
    elif file_ext == ".js":
        # 压缩JavaScript文件
        compressed_content = compress_js(content)
        write_file(output_path, compressed_content)
        original_size = len(content.encode('utf-8'))
        compressed_size = len(compressed_content.encode('utf-8'))
        print(f"✓ 压缩JS: {file_path} ({original_size} → {compressed_size} bytes, 压缩率: {((original_size - compressed_size) / original_size * 100):.1f}%)")
    
    else:
        # 复制其他文件（如HTML）
        write_file(output_path, content)
        file_size = len(content.encode('utf-8'))
        print(f"✓ 复制文件: {file_path} ({file_size} bytes)")


def merge_css_files(build_dir):
    """合并CSS文件"""
    css_files = [
        "styles/main.css",
        "styles/components.css",
        "styles/index-styles.css",
        "web_style.css"
    ]
    
    merged_content = ""
    total_original_size = 0
    
    for css_file in css_files:
        if os.path.exists(css_file):
            content = read_file(css_file)
            merged_content += content + "\n"
            total_original_size += len(content.encode('utf-8'))
    
    # 压缩合并后的CSS
    compressed_content = compress_css(merged_content)
    
    # 输出到build目录
    output_path = os.path.join(build_dir, "styles/merged-styles.css")
    write_file(output_path, compressed_content)
    
    compressed_size = len(compressed_content.encode('utf-8'))
    print(f"✓ 合并并压缩CSS ({len(css_files)}个文件): {total_original_size} → {compressed_size} bytes, 压缩率: {((total_original_size - compressed_size) / total_original_size * 100):.1f}%")
    
    return "styles/merged-styles.css"

def merge_js_files(build_dir):
    """合并JS文件"""
    js_files = [
        "utils/api.js",
        "utils/validation.js",
        "utils/taskManager.js",
        "scripts/app.js",
        "web_script_new.js"
    ]
    
    merged_content = ""
    total_original_size = 0
    
    for js_file in js_files:
        if os.path.exists(js_file):
            content = read_file(js_file)
            merged_content += content + "\n"
            total_original_size += len(content.encode('utf-8'))
    
    # 压缩合并后的JS
    compressed_content = compress_js(merged_content)
    
    # 确保scripts目录存在
    scripts_dir = os.path.join(build_dir, "scripts")
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    
    # 输出到build目录
    output_path = os.path.join(build_dir, "scripts/merged-scripts.js")
    write_file(output_path, compressed_content)
    
    compressed_size = len(compressed_content.encode('utf-8'))
    print(f"✓ 合并并压缩JS ({len(js_files)}个文件): {total_original_size} → {compressed_size} bytes, 压缩率: {((total_original_size - compressed_size) / total_original_size * 100):.1f}%")
    
    return "scripts/merged-scripts.js"

def update_html_css_references(build_dir):
    """更新HTML文件中的CSS和JS引用"""
    html_files = ["index.html", "login.html"]
    
    for html_file in html_files:
        file_path = os.path.join(build_dir, html_file)
        if os.path.exists(file_path):
            content = read_file(file_path)
            
            # 移除所有现有的CSS引用
            css_links_pattern = r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)\.css["\']\s*>'
            content = re.sub(css_links_pattern, '', content)
            
            # 移除所有现有的JS引用
            js_links_pattern = r'<script\s+src=["\']([^"\']+)\.js["\']\s*></script>'
            content = re.sub(js_links_pattern, '', content)
            
            # 在head标签中添加合并后的CSS引用
            head_pattern = r'(<head>)([\s\S]*?)(</head>)'
            css_link = '<link rel="stylesheet" href="styles/merged-styles.css">\n'
            new_content = re.sub(head_pattern, r'\1\2\n    ' + css_link + r'    \3', content)
            
            # 在body标签闭合前添加合并后的JS引用
            body_pattern = r'(</body>)'
            js_script = '<script src="scripts/merged-scripts.js"></script>\n'
            new_content = re.sub(body_pattern, r'\n    ' + js_script + r'\1', new_content)
            
            write_file(file_path, new_content)
            print(f"✓ 更新HTML CSS和JS引用: {html_file}")

def main():
    """主函数"""
    print("🚀 开始压缩前端资源...")
    start_time = datetime.now()
    
    # 创建构建目录
    build_dir = create_build_directory()
    
    # 合并并压缩CSS文件
    merge_css_files(build_dir)
    
    # 合并并压缩JS文件
    merge_js_files(build_dir)
    
    # 需要处理的文件和目录（排除单独的CSS和JS文件）
    files_to_process = [
        "index.html",
        "login.html"
    ]
    
    # 处理文件
    for file_path in files_to_process:
        if os.path.exists(file_path):
            process_file(file_path, build_dir)
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    # 更新HTML文件中的CSS和JS引用
    update_html_css_references(build_dir)
    
    # 复制pages目录
    pages_dir = "pages"
    if os.path.exists(pages_dir):
        output_pages_dir = os.path.join(build_dir, pages_dir)
        shutil.copytree(pages_dir, output_pages_dir, dirs_exist_ok=True)
        print(f"✓ 复制目录: {pages_dir}")
    
    # 确保scripts目录存在于build中
    scripts_dir = os.path.join(build_dir, "scripts")
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 资源压缩完成！")
    print(f"📁 构建目录: {build_dir}")
    print(f"⏱️  耗时: {duration:.2f}秒")


if __name__ == "__main__":
    main()