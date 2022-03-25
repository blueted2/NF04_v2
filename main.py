# from lexer import lexer
from parser import parser


with open("program.NF04", 'r') as fp:
    text = fp.read()

result = parser.parse(text, debug=True)
print(result)