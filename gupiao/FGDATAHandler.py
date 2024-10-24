# -*- coding: utf-8 -*-
# -------------------------- 期权数据处理 --------------------------#

import os

CODE = "FG001"
# 定义目录和目标文件
directory = './gupiao/QIQDATA/FG/source'
output_file = f'./gupiao/QIQDATA/FG/data/{CODE}.txt'

# 打开目标文件以写入
with open(output_file, 'w') as target_file:
    target_file.write("date|code|pre_js|open|high|low|close|cur_js|zd_one|zd_two|cj_volume|cc_volume|zj_volume|cj_amount|jgjsj\n")
    files = os.listdir(directory)
    # 对文件列表进行排序（正序）
    files_sorted = sorted(files)
    # 遍历目录中的所有文件
    for filename in files_sorted:
        # 确保只处理文本文件
        if filename.endswith('.txt'):
            print(f"读取文件{filename}")
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as source_file:
                # 跳过前两行
                next(source_file)
                next(source_file)

                # 遍历每一行
                for line in source_file:
                    # 按照 "|" 分割行数据
                    fields = line.strip().split('|')
                    
                    # 检查字段是否以 "SA401" 开头
                    if fields[1].startswith(CODE):
                        # 将 line 中的 "," 去掉，有些金额带，无法转 float，需要移除“，”
                        cleaned_line = line.replace(',', '')
                        # 写入整行数据到目标文件
                        target_file.write(cleaned_line)

print(f"提取完成，结果已写入 {CODE}.txt")

