from ply.lex import LexToken

def get_source_code_line(source_code: str, lexpos: int):
    start = source_code.rfind('\n', 0, lexpos) + 1
    end = source_code.find('\n', lexpos)
    return source_code[start: end]

def get_column(source_code: str, lexpos: int):
    line_start = source_code.rfind('\n', 0, lexpos)
    return (lexpos - line_start)

def manual_error_token(_type, value, lexpos, lineno) -> LexToken:
    error_token = LexToken()
    error_token.type = _type  # type: ignore
    error_token.value = value  # type: ignore
    error_token.lexpos = lexpos  # type: ignore
    error_token.lineno = lineno  # type: ignore
    return error_token
