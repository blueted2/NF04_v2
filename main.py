from lexer import *

with open("program.NF04", 'r') as fp:
    text = fp.read()

lexer.input(text)
while t := lexer.token():
    print(t)