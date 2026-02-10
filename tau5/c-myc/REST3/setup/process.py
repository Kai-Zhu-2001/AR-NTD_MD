# 打开top文件
with open('process.top', 'r') as file:
    # 读取所有行
    lines = file.readlines()

# 遍历每一行，检查是否在指定范围内且第24列为数字
for i in range(963, 2540):  # 行索引从0开始
    line = lines[i]
    
    # 检查是否有足够的列
    if len(line) >= 24:
        # 检查第24列是否为数字
        if line[23].isdigit():
            # 在当前行的第18列后面加上下划线
            lines[i] = line[:17] + '_' + line[17:]

# 将修改后的内容写入新文件process.top
with open('processed.top', 'w') as new_file:
    new_file.writelines(lines)
