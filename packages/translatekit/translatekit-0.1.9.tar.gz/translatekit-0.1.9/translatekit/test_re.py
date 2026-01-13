def main():
    import json

    _in = list()
    while True:
        line = input()
        if line == "ok":
            break
        _in.append(line)

    Language = json.loads("".join(_in))
    final_dict = {}
    for i in Language:
        LanguageID = Language[i]
        final_dict[LanguageID] = i

    # 直接使用json.dumps输出，确保格式正确
    result = json.dumps(final_dict, ensure_ascii=False, indent=2, separators=(',', ': '))

    # 按行输出，但不修改JSON本身的结构，以确保有效性
    lines = result.split('\n')
    for line in lines:
        print(line)

    def print_compact_json(data, max_line_len=90):
        """
        打印紧凑的JSON格式，每行最多max_line_len个字符
        在不超过限制的前提下，每行尽可能包含更多键值对
        """
        # 先获取紧凑格式的JSON
        compact_json = json.dumps(data, ensure_ascii=False, separators=(',', ': '))
        
        # 如果整体长度不超过限制，直接输出
        if len(compact_json) <= max_line_len:
            print(compact_json)
            return
        
        # 否则使用带缩进的格式并进行自定义处理
        indented_json = json.dumps(data, ensure_ascii=False, indent=8)
        lines = indented_json.split('\n')
        
        # 重新组织行，尝试合并短行
        result_lines = []
        i = 0
        while i < len(lines):
            current_line = lines[i]
            
            # 如果当前行不是对象/数组的开始或结束，且长度小于限制
            if (len(current_line) < max_line_len and 
                not current_line.strip() in ['{', '}', '[', ']']):
                
                # 尝试与后续行合并（如果它们有相同的缩进级别）
                j = i + 1
                while j < len(lines):
                    # 检查是否有相同缩进的行可以合并
                    current_indent = len(current_line) - len(current_line.lstrip())
                    next_indent = len(lines[j]) - len(lines[j].lstrip())
                    
                    # 如果缩进相同且合并后不会超过长度限制，则合并
                    if (next_indent == current_indent and 
                        len(current_line + lines[j].strip()) < max_line_len and
                        lines[j].strip().endswith(',')):
                        
                        current_line = current_line.rstrip() + ' ' + lines[j].strip()
                        j += 1
                    else:
                        break
                result_lines.append(current_line)
                i = j
            else:
                result_lines.append(current_line)
                i += 1
        
        for line in result_lines:
            print(line)

    print_compact_json(final_dict)
    
if __name__ == "__main__":
    while True:
        main()