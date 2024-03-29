import argparse
import sys

import numpy as np
from scipy.integrate import quad
from tabulate import tabulate

from lw5_helpers import function_tabulation, secants_method, get_input


def print_header():
    print("Задание #5.1. Приближенное вычисление определённых интегралов\n"
          "Вариант 7\n"
          "Исходные параметры задачи:\n"
          f"   A = 0   B = 1   n = 2   ρ(x) = sqrt(1-x)   f(x) = e^x\n")


def custom_tabulate(arr: np.ndarray | list, char: str, pres: int = 2, note: str = ''):
    replacements = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₆', '6': '₅', '7': '₇', '8': '₈', '9': '₉'}
    indexes = list()
    for i in range(len(arr)):
        new_index = str(i)
        for k, v in replacements.items():
            new_index = new_index.replace(k, v)
        indexes.append(new_index)
    headers = list(map(lambda index: char + index, indexes))
    return tabulate([arr], headers=headers, tablefmt="mixed_outline", numalign="center", floatfmt=f".{pres}f") + note


def pho(x: np.float64) -> np.ndarray:
    return np.sqrt(1 - x)


def function(x: np.float64) -> np.ndarray:
    return np.exp(x)


def create_parser():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-n', '--number_of_nodes', type=int, help="Number of nodes")
    return args_parser


def print_results(n: int, a: float, b: float):
    # Task 1
    print("\n――――――――――――task 1――――――――――――――")
    integral_value = quad(func=(lambda x: np.multiply(function(x), pho(x))), a=a, b=b)[0]
    print(f"Точное значение интеграла: {integral_value:.12f}")

    h = 1 / n
    x_values = np.array([i * h for i in range(n + 1)])

    # Task 3
    print("\n――――――――――――task 3――――――――――――――")
    print(custom_tabulate(x_values, 'x', 2, ' ↖ узлы КФ'))

    x_matrix = np.array([np.power(x_values, degree) for degree in range(n + 1)])
    mu_values = [quad(func=(lambda x: np.multiply(np.power(x, i), pho(x))), a=a, b=b)[0] for i in range(n + 1)]
    print(custom_tabulate(mu_values, 'μ', 5, ' ↖ моменты весовой функции'))

    a_values = np.linalg.solve(x_matrix, mu_values)
    print(custom_tabulate(a_values, 'A', 5, ' ↖ коэффициенты КФ'))

    approximate_value = sum([a_i * function(x_i) for a_i, x_i in zip(a_values, x_values)])
    print(f"Значение интеграла, полученное вычислением квадратур = {approximate_value:.12f}")
    print(f"Фактическая погрешность = {abs(integral_value - approximate_value):.12f}")

    # Task 5
    print("\n――――――――――――task 5――――――――――――――")

    mu_values = [quad(func=(lambda x: np.multiply(np.power(x, i), pho(x))), a=a, b=b)[0] for i in range(n * 2)]
    print(custom_tabulate(mu_values, 'μ', 5, ' ↖ моменты весовой функции'))

    mu_matrix_left = [list(reversed(mu_values[i:n + i])) for i in range(n)]
    mu_matrix_right = list(map(lambda mu: -mu, mu_values[n:n * 2]))
    a_values: np.ndarray = np.array([1, *np.linalg.solve(mu_matrix_left, mu_matrix_right)])
    print(custom_tabulate(a_values, 'a', 5, ' ↖ коэффициенты a₀xⁿ + a₁xⁿ⁻¹ + ··· + aₙ₋₁x + aₙ = 0'))

    def monomial(x: np.float64, degree: int, a_i: np.float64) -> np.float64:
        return np.multiply(np.power(x, degree), a_i)

    def polynomial(x: np.float64) -> np.ndarray:
        return np.sum([monomial(x, i, a_i) for i, a_i in enumerate(reversed(a_values))])

    segments = function_tabulation(n * 10, a, b, polynomial)
    roots = [secants_method(segment, polynomial) for segment in segments]
    print(custom_tabulate(roots, 'x', 5, ' ↖ корни xⁿ + a₁xⁿ⁻¹ + ··· + aₙ₋₁x + aₙ = 0'))

    x_matrix = [[root_i ** degree for root_i in roots] for degree in range(n)]
    csf_values = np.linalg.solve(x_matrix, mu_values[:n])
    print(custom_tabulate(csf_values, 'A', 5, ' ↖ коэффициенты КФ'))

    approximate_value = sum([a_i * function(x_i) for a_i, x_i in zip(csf_values, roots)])
    print(f"Значение интеграла, полученное по формуле типа Гаусса = {approximate_value:.14f}")
    print(f"Фактическая погрешность = {abs(integral_value - approximate_value):.14f}")


def main():
    print_header()

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    n = 2 if namespace.number_of_nodes is None else namespace.number_of_nodes

    choice = '1'
    try:
        while True:
            if choice == '1':
                a = get_input('A', 'нижний предел интегрирования', 0)
                b = get_input('B', 'верхний предел интегрирования', 1)
                if a >= b:
                    print(f"❌ A должно быть строго меньше, чем B...")
                    continue
                if b > 1:
                    print(f"❌ Отрезок интегрирования не принадлежит области определения ρ(x) = sqrt(1-x)...")
                    continue
                print_results(n, a, b)
            else:
                print(f"Выход из программы...")
                break
            choice = input(">>> Напишите \"1\", если хотите ввести новые значения:   ")
    except (Exception, KeyboardInterrupt):
        print(f"Ошибка!\nВыход из программы...")
        return


if __name__ == "__main__":
    main()
