def get_source_code_line(source_code: str, lexpos: int):
    start = source_code.rfind('\n', 0, lexpos) + 1
    end = source_code.find('\n', lexpos)
    return source_code[start: end]

def get_column(source_code: str, lexpos: int):
    line_start = source_code.rfind('\n', 0, lexpos)
    return (lexpos - line_start)