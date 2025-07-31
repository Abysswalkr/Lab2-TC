import sys
from typing import List, Tuple

OPENERS = {'(': ')', '[': ']', '{': '}'}
CLOSERS = {')', ']', '}'}

def balance_expression(expr: str) -> Tuple[bool, List[str]]:
    stack: List[str] = []
    pasos: List[str] = []
    in_class = False

    i = 0
    while i < len(expr):
        c = expr[i]

        if c == '\\':
            if i + 1 < len(expr):
                pasos.append(f"{i:03d}: ESC '\\{expr[i+1]}' (ignorado para balance) | Pila={stack}")
                i += 2
                continue
            else:
                pasos.append(f"{i:03d}: '\\' final sin carácter a escapar | Pila={stack}")
                return False, pasos

        if in_class:
            if c == ']':
                if stack and stack[-1] == '[':
                    stack.pop()
                    in_class = False
                    pasos.append(f"{i:03d}: POP ']' | Pila={stack}")
                else:
                    pasos.append(f"{i:03d}: ERROR ']' sin '[' | Pila={stack}")
                    return False, pasos
            else:
                pasos.append(f"{i:03d}: dentro de clase '[...]' lee '{c}' | Pila={stack}")
            i += 1
            continue

        if c in OPENERS:
            stack.append(c)
            pasos.append(f"{i:03d}: PUSH '{c}' | Pila={stack}")
            if c == '[':
                in_class = True
        elif c in CLOSERS:
            if not stack:
                pasos.append(f"{i:03d}: ERROR '{c}' sin abridor | Pila={stack}")
                return False, pasos
            top = stack.pop()
            if OPENERS.get(top) != c:
                pasos.append(f"{i:03d}: ERROR esperaba '{OPENERS.get(top)}' y llegó '{c}' | Pila={stack}")
                return False, pasos
            pasos.append(f"{i:03d}: POP '{c}' | Pila={stack}")
        else:
            pasos.append(f"{i:03d}: lee '{c}' | Pila={stack}")

        i += 1

    if in_class:
        pasos.append("FIN: ERROR clase de caracteres sin ']'")
        return False, pasos
    if stack:
        pasos.append(f"FIN: ERROR quedan abridores sin cerrar: {stack}")
        return False, pasos
    pasos.append("FIN: Expresión balanceada (pila vacía)")
    return True, pasos


def main():
    if len(sys.argv) < 2:
        print("Uso: python balanceo.py <expresiones.txt>")
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
        print("-"*80)
        ok, pasos = balance_expression(expr)
        print("BALANCEO:", "OK" if ok else "NO BALANCEADA")
        for p in pasos:
            print(" ", p)

if __name__ == "__main__":
    main()
