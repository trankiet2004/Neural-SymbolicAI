import random
from sympy import symbols, Eq, solve, expand
import csv

def generate_quadratic():
    x = symbols('x')
    a = random.randint(1, 10) * random.choice([-1, 1]) 
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    equation = Eq(a * x**2 + b * x + c, 0)
    solutions = solve(equation, x)

    return f"{a}x^2 + {b}x + {c} = 0", solutions

def generate_cubic_beautiful():
    x = symbols('x')
    root1 = random.randint(-5, 5)
    root2 = random.randint(-5, 5)
    root3 = random.randint(-5, 5)
    equation = expand((x - root1) * (x - root2) * (x - root3))
    a = random.randint(1, 5) * random.choice([-1, 1])
    equation = a * equation
    solutions = [root1, root2, root3]
    return f"{equation} = 0", solutions

def write_to_csv(filename, equations):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Equation", "Solutions"])
        for equation, solutions in equations:
            writer.writerow([str(equation), str(solutions)])

if __name__ == "__main__":
    num_tests = 10
    quadratic_equations = [generate_quadratic() for _ in range(num_tests)]
    write_to_csv("quadratic_equations.csv", quadratic_equations)
    cubic_equations = [generate_cubic_beautiful() for _ in range(num_tests)]
    write_to_csv("cubic_equations.csv", cubic_equations)

    print("Phương trình và nghiệm đã được ghi vào các file CSV:\n- quadratic_equations.csv\n- cubic_equations.csv")
