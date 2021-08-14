#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@authors: 

Angel Ramírez Martínez
"""
# imports
import ply.lex as lex
import ply.yacc as yacc

# palabras reservadas
TAGS = {}
preLineas = []
LINEAS = {}
reservadas = {'MOV': 'MOV', 'ADD': 'ADD', 'SUB': 'SUB', 'JMPZ': 'JMPZ'}

tokens = [
    'MEMORY',
    'REGISTER',
    'COMMA',
    'SEMICOLON',
    'TAG',
    'LABEL',
    'CONSTANT'
]+list(reservadas.values())

# ignore
t_ignore_COMMENT = r"//.* "
t_ignore = ' \f\r\t\v'

# regex tokens
t_COMMA = r','
t_SEMICOLON = r';'


def t_MEMORY(t):
    r"\b(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\b"
    return t


def t_REGISTER(t):
    r"\bR([0-9]{1}|1[0-5]{1})\b"
    return t


def t_CONSTANT(t):
    r"\#(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\b"
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_TAG(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*:'
    t.type = reservadas.get(t.value, 'TAG')    # Check for reserved words
    if TAGS.get(t.value, None) == None:
        TAGS[t.value] = t.lineno
    return t


def t_LABEL(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservadas.get(t.value, 'LABEL')    # Check for reserved words
    return t


def t_error(t):
    print("Error léxico")
    print("Caracter ilegal '%s' " % t.value[0])
    t.lexer.skip(1)
    exit()


lexer = lex.lex()
doc = """
// Example 8.4
// This program counts the number of words not equal
// to 0 in data memory locations 4 and 5, storing
// the final count in R0

MOV R0, #0; // initialize result to 0
MOV R1, #1; // constant 1 for incrementing result
MOV R2, 4; // get data memory location 4
JMPZ R2, lab1; // if zero, skip next instruction
ADD R0, R0, R1; // not zero, so increment result
lab1: MOV R2, 5; // get data memory location 5
JMPZ R2, lab2; // if zero, skip next instruction
ADD R0, R0, R1; //not zero, so increment result
lab2: MOV 9, R0; // store result in data memory location 9
"""
lexer.input(doc)  # dar al lexer una entrada

while True:
    tok = lexer.token()
    if not tok:
        break
    if tok.lineno not in preLineas:
        preLineas.append(tok.lineno)
    # print(tok)
index = [i for i in range(1, len(preLineas)+1)]
LINEAS = dict(zip(preLineas, index))
for tag in TAGS.keys():
    TAGS[tag] = LINEAS[TAGS[tag]]
# reglas de producción


def p_expresion_PROGRAMA(p):
    'PROGRAMA : LISTA_DE_INSTRUCCIONES'
    p[0] = p[1]


def p_LISTA_DE_INSTRUCCIONES_1(p):
    'LISTA_DE_INSTRUCCIONES : INSTRUCCION SEMICOLON'
    p[0] = str(p[1])+"\n"


def p_LISTA_DE_INSTRUCCIONES_2(p):
    'LISTA_DE_INSTRUCCIONES : INSTRUCCION SEMICOLON LISTA_DE_INSTRUCCIONES'
    p[0] = str(p[1])+"\n"+str(p[3])


def p_LISTA_DE_INSTRUCCIONES_3(p):
    'LISTA_DE_INSTRUCCIONES : TAG INSTRUCCION SEMICOLON'
    p[0] = str(p[2])+"\n"


def p_LISTA_DE_INSTRUCCIONES_4(p):
    'LISTA_DE_INSTRUCCIONES : TAG INSTRUCCION SEMICOLON LISTA_DE_INSTRUCCIONES'
    p[0] = str(p[2])+"\n"+str(p[4])


def p_expresion_INSTRUCCION_LOAD(p):
    "INSTRUCCION  : MOV REGISTER COMMA MEMORY"
    nemonic = "0000"
    register = "{0:04b}".format(int(str(p[2]).replace("R", '')))
    memory = "{0:08b}".format(int(p[4]))
    p[0] = nemonic+register+memory


def p_expresion_INSTRUCCION_STORE(p):
    "INSTRUCCION : MOV MEMORY COMMA REGISTER"
    nemonic = "0001"
    register = "{0:04b}".format(int(str(p[4]).replace("R", '')))
    memory = "{0:08b}".format(int(p[2]))
    p[0] = nemonic+register+memory


def p_expresion_INSTRUCCION_ADD(p):
    "INSTRUCCION : ADD REGISTER COMMA REGISTER COMMA REGISTER"
    nemonic = "0010"
    registerA = "{0:04b}".format(int(str(p[2]).replace("R", '')))
    registerB = "{0:04b}".format(int(str(p[4]).replace("R", '')))
    registerC = "{0:04b}".format(int(str(p[6]).replace("R", '')))
    p[0] = nemonic+registerA+registerB+registerC


def p_expresion_INSTRUCCION_LOAD_CONSTANT(p):
    "INSTRUCCION : MOV REGISTER COMMA CONSTANT"
    nemonic = "0011"
    register = "{0:04b}".format(int(str(p[2]).replace("R", '')))
    constant = "{0:08b}".format(int(str(p[4]).replace("#", '')))
    p[0] = nemonic+register+constant


def p_expresion_INSTRUCCION_SUBSTRACT(p):
    "INSTRUCCION : SUB REGISTER COMMA REGISTER COMMA REGISTER"
    nemonic = "0100"
    registerA = "{0:04b}".format(int(str(p[2]).replace("R", '')))
    registerB = "{0:04b}".format(int(str(p[4]).replace("R", '')))
    registerC = "{0:04b}".format(int(str(p[6]).replace("R", '')))
    p[0] = nemonic+registerA+registerB+registerC


def tobin(x, count=8): return "".join(
    map(lambda y: str((x >> y) & 1), range(count-1, -1, -1)))


def p_expresion_INSTRUCCION_JUMPIFZERO(p):
    "INSTRUCCION : JMPZ REGISTER COMMA LABEL"
    nemonic = "0101"
    register = "{0:04b}".format(int(str(p[2]).replace("R", '')))
    offset = tobin(
        TAGS[p[4]+":"]-LINEAS[int(p.slice[1].lineno-len(doc.splitlines()))])
    p[0] = nemonic+register+offset


def p_error(p):
    print('ERROR DE SINTAXIS')
    print('Error en ' + p.value)
    exit()


parser = yacc.yacc()
res = parser.parse(doc)
# print(TAGS)
print(res)
