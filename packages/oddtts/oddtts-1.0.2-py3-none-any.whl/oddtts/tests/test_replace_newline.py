from sys import argv

def replace_n_with_newline(file_path):
    """
    将文件中的\\n字符序列替换为实际的换行符
    
    参数:
        file_path: 文本文件的路径
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 替换\n为实际换行符
        modified_content = content.replace('\\n', '\n')
        
        # 将修改后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print(f"成功替换文件 {file_path} 中的\\n为换行符")
    
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到")
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")

if __name__ == "__main__":
    if len(argv) != 2:
        print("请提供一个文件路径作为参数. 例如: python test_replace_newline.py test.md")
        exit(1)

    file_path = argv[1]

    if file_path.endswith(".txt") or file_path.endswith(".md"):
        replace_n_with_newline(file_path)
