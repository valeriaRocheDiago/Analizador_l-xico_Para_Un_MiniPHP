# Este trabajo fue realizado con apoyo en ChatGPT, un modelo de lenguaje desarrollado por OpenAI. 
# Se utilizó para generar y refinar el código del analizador léxico para MiniPHP, además de proporcionar explicaciones conceptuales y sugerencias sobre la implementación.

"""Analizador Léxico para un MiniPHP — implementado con PLY (lex)."""

import sys
import ply.lex as lex


# Diccionario de palabras clave reconocidas por MiniPHP.
KEYWORDS = {
    'and': 'AND',
    'array': 'ARRAY',
    'as': 'AS',
    'break': 'BREAK',
    'case': 'CASE',
    'class': 'CLASS',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'echo': 'ECHO',
    'else': 'ELSE',
    'elseif': 'ELSEIF',
    'extends': 'EXTENDS',
    'false': 'FALSE',
    'for': 'FOR',
    'foreach': 'FOREACH',
    'function': 'FUNCTION',
    'if': 'IF',
    'implements': 'IMPLEMENTS',
    'include': 'INCLUDE',
    'int': 'INT',
    'interface': 'INTERFACE',
    'namespace': 'NAMESPACE',
    'new': 'NEW',
    'null': 'NULL',
    'or': 'OR',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
    'require': 'REQUIRE',
    'return': 'RETURN',
    'static': 'STATIC',
    'string': 'STRING_TYPE',
    'switch': 'SWITCH',
    'true': 'TRUE',
    'var': 'VAR',
    'while': 'WHILE',
    'xor': 'XOR',
}

# Tokens base + palabras reservadas.
tokens = [
    'OPEN_TAG', 'CLOSE_TAG',
    'PLUS', 'PLUSPLUS', 'PLUSEQUAL',
    'MINUS', 'MINUSMINUS', 'MINUSEQUAL',
    'TIMES', 'TIMESEQUAL',
    'DIVIDE', 'DIVEQUAL',
    'MODULO', 'MODEQUAL',
    'EQUAL', 'ISEQUAL', 'DEQUAL',
    'LESS', 'LESSEQUAL',
    'GREATER', 'GREATEREQUAL',
    'ANDAND', 'OROR', 'NOT', 'QUESTION',
    'SEMICOLON', 'COMMA', 'DOT', 'COLON',
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'VARIABLE', 'NUMBER', 'STRING', 'ID',
] + list(KEYWORDS.values())

# --- Etiquetas de apertura / cierre PHP ---
t_OPEN_TAG = r'<\?php\b|<\?='
t_CLOSE_TAG = r'\?>'

# --- Operadores compuestos (van primero) ---
t_PLUSPLUS = r'\+\+'
t_PLUSEQUAL = r'\+='
t_MINUSMINUS = r'--'
t_MINUSEQUAL = r'-='
t_TIMESEQUAL = r'\*='
t_DIVEQUAL = r'/='
t_MODEQUAL = r'%='
t_ISEQUAL = r'=='
t_DEQUAL = r'!='
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='
t_ANDAND = r'&&'
t_OROR = r'\|\|'

# --- Operadores simples y delimitadores ---
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_EQUAL = r'='
t_LESS = r'<'
t_GREATER = r'>'
t_NOT = r'!'
t_QUESTION = r'\?'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'


# --- Registro de errores ---
errores = []


def registrar_error(linea, tipo, lexema, detalle):
    """Guarda y muestra un error léxico clasificado."""
    error = {
        'linea': linea,
        'tipo': tipo,
        'lexema': lexema,
        'detalle': detalle,
    }
    errores.append(error)

    print(
        f"[ERROR LÉXICO] Línea {linea}: {tipo}\n"
        f"    Lexema: {lexema!r}\n"
        f"    Detalle: {detalle}"
    )



# --- Errores específicos ---
def t_MALFORMED_VARIABLE(t):
    r'\$[0-9][a-zA-Z0-9_]*'
    registrar_error(
        t.lexer.lineno,
        'Variable mal formada',
        t.value,
        "Una variable debe comenzar con '$' seguido de una letra o '_'."
    )


def t_MALFORMED_NUMBER(t):
    r'\d+(\.\d+){2,}'
    registrar_error(
        t.lexer.lineno,
        'Número mal formado',
        t.value,
        'El número contiene más de un punto decimal.'
    )


def t_MALFORMED_NUMBER_WITH_LETTERS(t):
    r'\d+(\.\d+)?[a-zA-Z_][a-zA-Z0-9_]*'
    registrar_error(
        t.lexer.lineno,
        'Número mal formado',
        t.value,
        'Un número no puede estar seguido directamente por letras o "_".'
    )


def t_UNTERMINATED_STRING(t):
    r'("([^"\\\n]|\\.)*|\'([^\'\\\n]|\\.)*)$'
    registrar_error(
        t.lexer.lineno,
        'Cadena sin cerrar',
        t.value,
        'La cadena debe terminar con la misma comilla con la que comenzó.'
    )


def t_UNTERMINATED_COMMENT(t):
    r'/\*(?:(?!\*/)[\s\S])*$'
    t.lexer.lineno += t.value.count('\n')
    registrar_error(
        t.lexer.lineno,
        'Comentario de bloque sin cerrar',
        t.value,
        'El comentario debe terminar con */.'
    )



# --- Reglas de tokens ---
def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_COMMENT_LINE(t):
    r'//[^\n]*|\#[^\n]*'


def t_VARIABLE(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    return t


def t_STRING(t):
    r'''("([^"\\\n]|\\.)*"|'([^'\\\n]|\\.)*')'''
    return t


def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = KEYWORDS.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t\r'


# --- Errores genéricos ---
def t_error(t):
    """Clasifica caracteres que no pertenecen a ningún token conocido."""
    caracter = t.value[0]

    if caracter == '&':
        tipo = 'Operador mal formado'
        detalle = "Se encontró '&' solo; para AND lógico se esperaba '&&'."
    elif caracter == '|':
        tipo = 'Operador mal formado'
        detalle = "Se encontró '|' solo; para OR lógico se esperaba '||'."
    elif caracter == '@':
        tipo = 'Carácter no permitido'
        detalle = "El carácter '@' no está definido como token en este MiniPHP."
    elif caracter == '~':
        tipo = 'Operador no soportado'
        detalle = "El operador '~' no está definido en este MiniPHP."
    else:
        tipo = 'Carácter no reconocido'
        detalle = 'El carácter no pertenece al conjunto de tokens reconocido.'

    registrar_error(t.lexer.lineno, tipo, caracter, detalle)
    t.lexer.skip(1)


# --- Reporte de errores ---
def mostrar_resumen_errores():
    print('\n--- Resumen de errores ---')

    if not errores:
        print('No se encontraron errores léxicos.')
        return

    print(f'Total de errores léxicos: {len(errores)}')

    conteo = {}
    for error in errores:
        tipo = error['tipo']
        conteo[tipo] = conteo.get(tipo, 0) + 1

    print('\nErrores por tipo:')
    for tipo, cantidad in conteo.items():
        print(f'  - {tipo}: {cantidad}')



def mostrar_tokens(codigo, analizador):
    """Recorre el código fuente e imprime cada token encontrado."""
    errores.clear()
    analizador.lineno = 1
    analizador.input(codigo)

    while True:
        tok = analizador.token()
        if tok is None:
            break
        print(tok)

    mostrar_resumen_errores()


analizador = lex.lex()


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith('-')]
    archivo = argumentos[0] if argumentos else 'prueba_miniphp.php'

    try:
        with open(archivo, encoding='utf-8') as f:
            fuente = f.read()
    except FileNotFoundError:
        print(f"No se pudo abrir el archivo: '{archivo}'")
        sys.exit(1)

    print('--- Código fuente ---')
    print(fuente)
    print('--- Tokens ---')
    mostrar_tokens(fuente, analizador)


if __name__ == '__main__':
    main()