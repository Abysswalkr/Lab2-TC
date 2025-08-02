# Proyecto Lab2-TC

Este repositorio contiene la implementación de dos herramientas en Python para la teoría de la computación:

1. **Verificador de balanceo de expresiones** (Problema 1)
2. **Conversión Infix → Postfix (Shunting-Yard)** para expresiones regulares (Problema 2)

Además, se utilizan ramas (branches) de Git para aislar cada problema y mantener el historial limpio.

---

## Estructura de ramas (branches)

* **main**: Rama principal. Contiene el punto de integración estable.
* **problema 1**: Rama dedicada al Problema 1, con el script de los incisos resueltos. 
* **problema 2**: Rama dedicada al Problema 2, con el script `balanceo.py` y los ejemplos de entrada.
* **problema 3**: Rama dedicada al Problema 3, con el script `shunting_yard.py` y los mismos ejemplos de entrada.

---

## Archivos principales

* `balanceo.py`: Script de Python que verifica el balance de expresiones usando una pila y muestra la traza paso a paso.
* `shunting_yard.py`: Script de Python que convierte expresiones regulares de formato infix a postfix usando el algoritmo Shunting Yard, muestra los tokens, la traza de la pila y realiza la expansión de `+` y `?`.
* `expresiones.txt`: Archivo de texto con una expresión regular por línea, usado como entrada para ambos scripts.

---

## Comandos de ejecución

Asegúrate de tener Python 3.9+ instalado y estar en el directorio raíz del proyecto.

1. **Problema 2: Verificador de balanceo**

   ```bash
   # Usando "expresiones.txt" como archivo de entrada
   python balanceo.py expresiones.txt

   # O si tu sistema usa "python3"
   python3 balanceo.py expresiones.txt
   ```

2. **Problema 3: Shunting-Yard para regex**

   ```bash
   python shunting_yard.py expresiones.txt

   # O
   python3 shunting_yard.py expresiones.txt
   ```

Si usas otro nombre de archivo (por ejemplo `text.txt`), reemplaza `expresiones.txt` por el nombre correspondiente:

```bash
python balanceo.py text.txt
python shunting_yard.py text.txt
```

---

## Video de demostración

Puedes ver la ejecución paso a paso de ambos programas en el siguiente video:

🔗 [https://youtu.be/GfRwD6m0hz8](https://youtu.be/GfRwD6m0hz8)
