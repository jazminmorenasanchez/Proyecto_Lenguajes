from graphviz import Digraph

state_counter = 0
transitions = []

def new_state():
    global state_counter
    state = state_counter
    state_counter += 1
    return state

def add_concatenation_symbols(expr):
    # Inserta puntos para concatenación implícita, por ejemplo: ab → a.b
    result = ""
    for i in range(len(expr)):
        result += expr[i]
        if i + 1 < len(expr):
            if (expr[i].isalnum() or expr[i] == ')' or expr[i] == '*') and \
               (expr[i+1].isalnum() or expr[i+1] == '('):
                result += '.'
    return result

def hash(expr):
    # Agrega paréntesis si hace falta, útil para asegurar estructura al parsear
    if len(expr) > 1 and not expr.startswith('('):
        expr = '(' + expr + ')'
    return expr



def kleene_recursive(expr):
     # Caso especial: lenguaje vacío (∅) → no acepta nada
    if expr == 'v':
        start = new_state()
        end = new_state()
        # No agregamos ninguna transición
        return start, end
    
     # Caso: cadena vacía (λ)
    global transitions
    if len(expr) == 0:
        start = new_state()
        end = new_state()
        transitions.append((start, end, 'λ'))
        return start, end

    # Caso base: símbolo del alfabeto
    if len(expr) == 1:
        start = new_state()
        end = new_state()
        transitions.append((start, end, expr))
        return start, end

    if expr.startswith('(') and expr.endswith(')'):
        expr = expr[1:-1]


    # Procesar unión
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '+' and depth == 0:
            left = expr[:i]
            right = expr[i+1:]
            left_start, left_end = kleene_recursive(left)
            right_start, right_end = kleene_recursive(right)

            start = new_state()
            end = new_state()

            transitions.append((start, left_start, 'λ'))
            transitions.append((start, right_start, 'λ'))
            transitions.append((left_end, end, 'λ'))
            transitions.append((right_end, end, 'λ'))

            return start, end

    # Procesar concatenación
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '.' and depth == 0:
            left = expr[:i]
            right = expr[i+1:]
            left_start, left_end = kleene_recursive(left)
            right_start, right_end = kleene_recursive(right)

            transitions.append((left_end, right_start, 'λ'))

            return left_start, right_end

    # Procesar estrella
    if expr[-1] == '*':
        subexpr = expr[:-1]
        sub_start, sub_end = kleene_recursive(subexpr)

        start = new_state()
        end = new_state()

        transitions.append((start, sub_start, 'λ'))
        transitions.append((sub_end, sub_start, 'λ'))
        transitions.append((start, end, 'λ'))
        transitions.append((sub_end, end, 'λ'))

        return start, end
    
    # Procesar operador hash (#): e# = e.e + e
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '#' and depth == 0:
            if i == 0:
                raise ValueError("Símbolo '#' sin expresión anterior")

            e = expr[:i]           # lo que está antes del #
            rest = expr[i+1:]      # lo que está después del #
        
            left_expr = f"({e}.{e})"
            right_expr = e
            combined_expr = f"({left_expr}+{right_expr}){rest}"

            combined_expr = add_concatenation_symbols(combined_expr)
            return kleene_recursive(combined_expr)
        
     # Procesar operador hash (#): e1!e2=e1(e1+e2)
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '!' and depth == 0:
            if i == 0:
                raise ValueError("Símbolo '!' sin expresión anterior")

            e = expr[:i]           # lo que está antes del !
            rest = expr[i+1:]      # lo que está después del !

            left_expr = f"({e}*)"
            right_expr = f"({e}+{rest})"
            combined_expr = f"({left_expr}{right_expr})"

            combined_expr = add_concatenation_symbols(combined_expr)
            return kleene_recursive(combined_expr)


    # Si llega acá, hay un error de parsing
    raise ValueError(f"Expresion no valida o no reconocida: {expr}")

def draw_nfa(expr):
    global transitions, state_counter
    transitions = []
    state_counter = 0

    expr = hash(expr)
    expr = add_concatenation_symbols(expr)
    start, end = kleene_recursive(expr)

    graph = Digraph(format="png")
    graph.attr(rankdir="LR")

    # Crear nodos
    for state in range(state_counter):
        shape = "doublecircle" if state == end else "circle"
        color = "green" if state == start else "black"
        graph.node(str(state), shape=shape, color=color)

    # Crear transiciones
    for from_state, to_state, symbol in transitions:
        symbol = "λ" if symbol == "ε" else symbol  # Reemplaza "ε" por "λ"
        graph.edge(str(from_state), str(to_state), label=symbol)

    graph.render("AFN_Kleene", view=True)

if __name__ == "__main__":
    expr_input = input("Ingrese una expresion regular (usa +, *, y concatenacion implicita como ab o a(b+c)*): ")
    draw_nfa(expr_input)
