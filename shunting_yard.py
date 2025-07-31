import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ---------------- Tokens ----------------
@dataclass
class Token:
    kind: str 
    value: Optional[str] = None

def tokenize(expr: str) -> List[Token]:
    """Tokeniza respetando escapes y clases de caracteres."""
    tokens: List[Token] = []
    i, n = 0, len(expr)
    while i < n:
        c = expr[i]
        if c == '\\':
            # literal escapado
            if i + 1 < n:
                tokens.append(Token('LIT', expr[i+1]))
                i += 2
            else:
                tokens.append(Token('LIT', '\\'))
                i += 1
        elif c == '[':
            # clase de caracteres
            j = i + 1
            contenido = ''
            cerrado = False
            while j < n:
                if expr[j] == '\\' and j + 1 < n:
                    contenido += '\\' + expr[j+1]
                    j += 2
                    continue
                if expr[j] == ']':
                    cerrado = True
                    break
                contenido += expr[j]
                j += 1
            if cerrado:
                tokens.append(Token('CLASS', contenido))
                i = j + 1
            else:
                tokens.append(Token('LIT', '['))  # tolerante si no cierra
                i += 1
        elif c == '.':
            tokens.append(Token('ANY', '.')); i += 1
        elif c in '()*+?|':
            kind = {'(':'LP', ')':'RP', '*':'STAR', '+':'PLUS', '?':'QMARK', '|':'ALT'}[c]
            tokens.append(Token(kind, c)); i += 1
        elif c == '{':
            # cuantificador {m}, {m,}, {m,n} (validación simple)
            j = i + 1
            interior = ''
            valido = False
            while j < n and expr[j] != '}':
                interior += expr[j]
                j += 1
            if j < n and expr[j] == '}':
                s = interior.strip()
                if s and all(ch.isdigit() or ch == ',' for ch in s):
                    tokens.append(Token('REPEAT', '{' + s + '}'))
                    i = j + 1
                    valido = True
            if not valido:
                tokens.append(Token('LIT', '{'))
                i += 1
        elif c.isspace():
            i += 1
        else:
            tokens.append(Token('LIT', c)); i += 1
    return tokens

def needs_concat(prev: Token, nxt: Token) -> bool:
    """Decide si debe insertarse '·' entre prev y nxt."""
    if prev.kind in ('LP', 'ALT'):
        return False
    starts_atom = nxt.kind in ('LIT','ANY','CLASS','LP')
    ends_atom = prev.kind in ('LIT','ANY','CLASS','RP','STAR','PLUS','QMARK','REPEAT')
    return ends_atom and starts_atom

def add_concat(tokens: List[Token]) -> List[Token]:
    res: List[Token] = []
    for t in tokens:
        if res and needs_concat(res[-1], t):
            res.append(Token('CONCAT', '·'))
        res.append(t)
    return res

# ------------- Shunting-Yard -------------
PRECEDENCE = {
    'ALT': 1,     # |
    'CONCAT': 2,  # ·
}

@dataclass
class Step:
    i: int
    accion: str
    token: str
    salida: str
    pila: str

def shunting_yard(tokens: List[Token]) -> Tuple[List[str], List[Step]]:
    out: List[str] = []
    ops: List[Token] = []
    pasos: List[Step] = []

    for i, tok in enumerate(tokens):
        if tok.kind in ('LIT','ANY','CLASS'):
            atom = ('.' if tok.kind == 'ANY' else ('['+tok.value+']' if tok.kind=='CLASS' else tok.value))
            out.append(atom)
            pasos.append(Step(i, 'EMIT', atom, ' '.join(out), ''.join(o.value or o.kind for o in ops)))
        elif tok.kind in ('STAR','PLUS','QMARK','REPEAT'):
            out.append(tok.value or {'STAR':'*','PLUS':'+','QMARK':'?','REPEAT':'{?}'}[tok.kind])
            pasos.append(Step(i, 'EMIT_POSF', tok.value or tok.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))
        elif tok.kind == 'LP':
            ops.append(tok)
            pasos.append(Step(i, 'PUSH', '(', ' '.join(out), ''.join(o.value or o.kind for o in ops)))
        elif tok.kind == 'RP':
            while ops and ops[-1].kind != 'LP':
                p = ops.pop()
                out.append(p.value or p.kind)
                pasos.append(Step(i, 'POP->EMIT', p.value or p.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))
            if not ops:
                raise ValueError("Paréntesis desbalanceados (falta '(')")
            ops.pop()  # descarta '('
            pasos.append(Step(i, 'POP', ')', ' '.join(out), ''.join(o.value or o.kind for o in ops)))
        elif tok.kind in ('ALT','CONCAT'):
            while ops and ops[-1].kind in ('ALT','CONCAT') and PRECEDENCE[ops[-1].kind] >= PRECEDENCE[tok.kind]:
                p = ops.pop()
                out.append(p.value or p.kind)
                pasos.append(Step(i, 'POP->EMIT', p.value or p.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))
            ops.append(tok)
            pasos.append(Step(i, 'PUSH', tok.value or tok.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))
        else:
            # fallback: literal
            out.append(tok.value or tok.kind)
            pasos.append(Step(i, 'EMIT(?)', tok.value or tok.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))

    while ops:
        p = ops.pop()
        if p.kind == 'LP':
            raise ValueError("Paréntesis desbalanceados al final")
        out.append(p.value or p.kind)
        pasos.append(Step(len(tokens), 'POP->EMIT', p.value or p.kind, ' '.join(out), ''.join(o.value or o.kind for o in ops)))

    return out, pasos

# --------- Expansión de + y ? (post-procesamiento) ----------
def expand_plus_qmark(postfix: List[str]) -> List[str]:
    stack: List[List[str]] = []
    for t in postfix:
        if t == '*':
            a = stack.pop(); stack.append(a + ['*'])
        elif t == '+':
            a = stack.pop(); stack.append(a + a + ['*', '·'])
        elif t == '?':
            a = stack.pop(); stack.append(a + ['ε', '|'])
        elif t == '·':
            b = stack.pop(); a = stack.pop(); stack.append(a + b + ['·'])
        elif t == '|':
            b = stack.pop(); a = stack.pop(); stack.append(a + b + ['|'])
        elif t.startswith('{') and t.endswith('}'):
            a = stack.pop(); stack.append(a + [t])
        else:
            stack.append([t])
    if len(stack) != 1:
        raise ValueError("Postfix inválido (sobraron elementos)")
    return stack[0]

# ----------------- CLI -----------------
def main():
    if len(sys.argv) < 2:
        print("Uso: python shunting_yard.py <archivo.txt>")
        sys.exit(1)
    filename = sys.argv[1]
    try:
        with open(filename, encoding='utf-8') as f:
            lineas = [ln.rstrip('\n') for ln in f if ln.strip()]
    except Exception as e:
        print("No se pudo abrir el archivo:", e)
        sys.exit(1)

    for expr in lineas:
        print("="*80)
        print("Expresión:", expr)
        # Tokenizar e insertar concatenación
        toks = add_concat(tokenize(expr))
        toks_str = ' '.join(('['+t.value+']') if t.kind=='CLASS' else (t.value if t.value else t.kind) for t in toks)
        print("TOKENS: ", toks_str)

        # Shunting Yard
        postfix, pasos = shunting_yard(toks)
        print("POSTFIX (crudo):", ' '.join(postfix))

        print("\nPasos Shunting-Yard (i, acción, token, OUT, OPSTACK):")
        for st in pasos:
            print(f"  [{st.i:02d}] {st.accion:10s} {st.token:10s} OUT: {st.salida:30s} OPS: {st.pila}")

        # Expandir + y ?
        try:
            expanded = expand_plus_qmark(postfix)
            print("\nPOSTFIX (expandido + y ?):", ' '.join(expanded))
        except Exception as e:
            print("\nNo se pudo expandir +/?:", e)

if __name__ == "__main__":
    main()
