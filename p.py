from graphviz import Digraph #Importa la clase Digraph de la librería graphviz de Python
                             #Esta clase se usa para dibujar grafos dirigidos, como los diagramas de autómatas.
state_counter = 0 #Es un contador global que sirve para asignar un número único a cada estado del autómata.Cada vez que se crea un nuevo estado, este número se incrementa.
transitions = [] #Es una lista global donde se van a guardar todas las transiciones del autómata.Cada transición es una tupla con la forma:(estado_origen, estado_destino, símbolo) ej: [(0, 1, 'a'), (1, 2, 'λ')]

def new_state(): #Esta función se encarga de crear un nuevo estado.
    global state_counter #Le dice a Python que va a usar la variable state_counter global (fuera de la función), no una nueva local.
    state = state_counter #Guarda el valor actual (ej: 0) como el ID del nuevo estado.
    state_counter += 1 #Incrementa el contador para que el próximo estado tenga un número distinto.
    return state #Devuelve el número de estado recién creado.

#  “Cada vez que necesitamos un nuevo estado en el autómata,
#  llamamos a new_state(). Esta función nos da un número único,
#  empezando desde 0, y va incrementando de a 1. Así garantizamos
#  que ningún estado se repita. Después guardamos las transiciones entre
#  esos estados en una lista global llamada transitions.”

def add_concatenation_symbols(expr): #Define una función que toma un string (expresión regular) como entrada.
    # Inserta puntos para concatenación implícita, por ejemplo: ab → a.b
    result = "" #Variable donde vamos a ir armando la nueva expresión con puntos agregados.
    for i in range(len(expr)): #Recorremos la expresión carácter por carácter.
        result += expr[i] #Primero agregamos el carácter actual al resultado.
        if i + 1 < len(expr): #Nos aseguramos de que exista un siguiente carácter, para evitar errores de índice.
            #Este if detecta dónde hay concatenación implícita.
            #Por ejemplo, si tenemos "ab" y estamos en 'a', verificamos si el siguiente es 'b'.
            #Si el actual es alfanumérico o ')' o '*' y el siguiente es alfanumérico o '(',
            #entonces hay una concatenación implícita y agregamos un punto entre ellos.

            if (expr[i].isalnum() or expr[i] == ')' or expr[i] == '*') and \
               (expr[i+1].isalnum() or expr[i+1] == '('):
                result += '.' # si la condición se cumple, agregamos un punto al resultado.
    
    return result # Al final, devolvemos la nueva expresión con los puntos de concatenación añadidos.
    

# Esta función se encarga de agregar paréntesis a la expresión regular
# para asegurar que la estructura sea correcta al parsear.
# Esto es útil para que el parser (kleene_recursive) tenga una estructura clara sobre dónde empieza y termina la expresión completa.
def hash(expr): #Se define la función hash, que recibe una cadena expr (la expresión regular que el usuario ingresó).
    # Agrega paréntesis si hace falta, útil para asegurar estructura al parsear
    if len(expr) > 1 and not expr.startswith('('): #Que la expresión tenga más de un carácter (len(expr) > 1), Si es una sola letra como a, no necesita paréntesis. Que no empiece ya con un paréntesis. Si ya está escrita como (ab+ba), no hace falta envolverla otra vez.
        expr = '(' + expr + ')' #Si se cumplen las condiciones, agrega paréntesis al principio y al final de la expresión.
    return expr # Devuelve la expresión modificada con paréntesis si era necesario.



#Toma una expresión regular (ya con puntos . agregados por add_concatenation_symbols) y construye:
#Estados (usando new_state())
#Transiciones (guardadas en la lista transitions)
#Devuelve una pareja de estados: (estado_inicial, estado_final) del AF para esa subexpresión


def kleene_recursive(expr): #Procesa recursivamente la expresión regular para construir el autómata finito no determinista (AFN) correspondiente.
    global transitions #Usa la variable global transitions para que pueda guardar las transiciones de cada llamada recursiva.
    #CASO BASE:
    # Si la expresión es vacía, crea un estado inicial y final, y agrega una transición vacía (λ) entre ellos.
    if len(expr) == 0: 
        start = new_state() #Crea un nuevo estado inicial
        end = new_state() #Crea un nuevo estado final
        transitions.append((start, end, 'λ')) #Agrega una transición vacía entre el estado inicial y final
        return start, end # Devuelve (start, end), que es el autómata correspondiente a la cadena vacía.
    # “Este es uno de los casos base de la recursión. Si la expresión está vacía, significa que queremos un autómata que acepte solo la cadena vacía. Para eso, creamos dos estados y una transición λ entre ellos. Esta es la construcción de Thompson para el símbolo vacío.”


    # CASO BASE:
    # Si la expresión es un solo carácter, crea un estado inicial y final, y agrega una transición con ese carácter.
    if len(expr) == 1:
        start = new_state()
        end = new_state()
        transitions.append((start, end, expr)) # ejemplo : (0, 1, 'a')
        return start, end
    # porque devolvemos start y end? Sin esos dos estados, no podrías unir correctamente sub-autómatas.
    # “Este es otro caso base. Si la expresión es un solo símbolo, por ejemplo a, construimos un autómata mínimo con dos estados y una transición entre ellos con ese símbolo. Esta es la forma básica de representar un símbolo individual en el autómata de Kleene.”


    # Quita los paréntesis externos si la expresión completa empieza y termina con ( y ).
    if expr.startswith('(') and expr.endswith(')'): # para que? trabajar mas facil con lo que hay dentro. 
        expr = expr[1:-1]
    #importante, no saca parentesis internos, solo los externos.
    # esto no verifica que los paréntesis estén balanceados, solo quita los externos si están presentes.
    # si la expr = "a" no entra al if, y si es "(a+b)" sí entra y se convierte en "a+b".


    # Esta parte detecta una unión (+) en la expresión regular y construye un autómata que acepte cualquiera de los dos caminos. Es parte clave de la construcción de Thompson.
    # detecta cuando la expresion es una unión (a + b) y construye un automata finito que acepte cualquiera de las dos ramas usando transiciones vacías.
    depth = 0 #Usa depth para saber si estamos dentro o fuera de paréntesis
    # Va analizando cada carácter. El depth sirve para ignorar signos + que están dentro de paréntesis.Ejemplo: En a+(b+c)
    # 👉 solo el + exterior importa, no el de adentro.

    for i in range(len(expr)): # Recorre la expresión carácter por carácter, Encuentra el + principal (afuera de paréntesis)
        
        if expr[i] == '(': # Va contando paréntesis para saber si el + está al nivel principal (afuera), o anidado.
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '+' and depth == 0: #entra en este else si todos los parentesis que hayo se cerraron luego, Significa que el + está afuera, no dentro de un paréntesis, y entonces separa la expresión en dos mitades. Detecta un operador + que no esté dentro de paréntesis, Ese es el + principal que separa dos partes de la expresión
            # Separa la expresión en dos mitades:
            left = expr[:i] # left = parte izquierda del +
            right = expr[i+1:] # right = parte derecha del +

            # Llama recursivamente a kleene_recursive para procesar ambas mitades
            #Llama recursivamente a cada mitad Construye los autómatas de left y right Y obtiene los estados iniciales/finales de cada uno
            # recursividad: Se va rompiendo la expresión en mitades hasta que cada parte sea tan simple como 'a', 'b', 'λ', etc.
            left_start, left_end = kleene_recursive(left)
            right_start, right_end = kleene_recursive(right)

            #“El algoritmo usa recursión para romper la expresión regular en subexpresiones cada vez más simples. Si detecta una unión (+), separa en izquierda y derecha y llama a sí mismo con cada parte. Esto se repite hasta que cada parte sea una expresión simple, como un símbolo individual, que es un caso base. Ahí ya se puede construir el autómata más pequeño, y luego se va reconstruyendo hacia arriba.”

            # Ahora viene la construcción del nuevo autómata que hace la unión
            # Crea un nuevo estado inicial y final para la unión
            start = new_state()
            end = new_state()

            # Desde el nuevo start, se conecta por transiciones vacías a ambos sub-autómatas
            transitions.append((start, left_start, 'λ'))
            transitions.append((start, right_start, 'λ'))
            # Desde los finales de ambos caminos (left y right), se llega al nuevo end
            transitions.append((left_end, end, 'λ'))
            transitions.append((right_end, end, 'λ'))

            return start, end
        # Devuelve los extremos del nuevo autómata que representa la unión

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
