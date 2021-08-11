#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@authors: 

Angel Ramírez Martínez
"""
#imports
import ply.lex as lex
import ply.yacc as yacc

#palabras reservadas
reservadas={'MOV':'MOV','ADD':'ADD'}

tokens = [
        'MEMORY',
        'REGISTER',
        'COMMA',
        'SEMICOLON',
        'LABEL'
        ]+list(reservadas.values())

#ignore
t_ignore_COMMENT = r'//.* \n'
t_ignore = ' \n\f\r\t\v'

#regex tokens
t_COMMA=r','
t_SEMICOLON=r';'

#Complex tokens


def t_MEMORY(t):
    r"\b(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\b"
    return t

def t_REGISTER(t):
    r"\bR([0-9]{1}|1[0-5]{1})\b"
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservadas.get(t.value,'ID')    # Check for reserved words
    return t
def t_error(t):
    print("Error léxico")
    print("Caracter ilegal '%s' " % t.value[0])
    t.lexer.skip(1)
    exit()

lexer = lex.lex()
doc="""MOV R0, 0;
MOV R1, 1;
MOV 9, R2;
//Este es un comentario
"""

lexer.input(doc) #dar al lexer una entrada

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)