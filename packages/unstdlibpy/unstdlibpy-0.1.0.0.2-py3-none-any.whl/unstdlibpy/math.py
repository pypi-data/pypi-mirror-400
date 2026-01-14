
"""
Math module providing various mathematical functions and calculations.
Includes functions for geometry, algebra, statistics, number theory, and more.
Imports specific mathematical functions from an internal module.
"""

from typing import Union, TypeAlias
from math import sqrt, log, exp, sin, cos, tan, pi, acos

num: TypeAlias = Union[int, float]

def hypotenuse(a: num, b: num) -> float:
    """Calculate the hypotenuse of a right triangle given sides a and b."""
    return sqrt(a**2 + b**2)

def logarithm(x: num, base: Union[num, str] = 10) -> float:
    """Calculate the logarithm of x to the given base.

    `base` may be a number (e.g. 10, 2), or the string 'e' to indicate natural log.
    """
    if isinstance(base, str):
        if base == 'e':
            return log(x)
        raise ValueError("Unsupported base string. Use 'e' for natural log or provide a numeric base.")
    return log(x, base)

def exponential(x: num) -> float:
    """Calculate the exponential of x."""
    return exp(x)

def trigonometric_functions(angle_rad: num) -> dict[str, float]:
    """Calculate the sine, cosine, and tangent of an angle in radians."""
    return {
        'sin': sin(angle_rad),
        'cos': cos(angle_rad),
        'tan': tan(angle_rad)
    }

def degrees_to_radians(degrees: num) -> float:
    """Convert degrees to radians."""
    return degrees * (pi / 180)

def radians_to_degrees(radians: num) -> float:
    """Convert radians to degrees."""
    return radians * (180 / pi)

def pythagorean_theorem(a: num, b: num) -> float:
    """Calculate the length of the hypotenuse using the Pythagorean theorem."""
    return sqrt(a**2 + b**2)

def area_of_circle(radius: num) -> float:
    """Calculate the area of a circle given its radius."""
    return pi * radius**2

def circumference_of_circle(radius: num) -> float:
    """Calculate the circumference of a circle given its radius."""
    return 2 * pi * radius

def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def combinations(n: int, r: int) -> int:
    """Calculate the number of combinations of n items taken r at a time."""
    if r > n or n < 0 or r < 0:
        return 0
    return factorial(n) // (factorial(r) * factorial(n - r))

def permutations(n: int, r: int) -> int:
    """Calculate the number of permutations of n items taken r at a time."""
    if r > n or n < 0 or r < 0:
        return 0
    return factorial(n) // factorial(n - r)

def quadratic_formula(a: num, b: num, c: num) -> tuple[num, num] | None:
    """Calculate the roots of a quadratic equation ax^2 + bx + c = 0."""
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None  # No real roots
    root1 = (-b + sqrt(discriminant)) / (2*a)
    root2 = (-b - sqrt(discriminant)) / (2*a)
    return (root1, root2)

def mean(numbers: list[num]) -> float | int:
    """Calculate the mean of a list of numbers."""
    return sum(numbers) / len(numbers) if numbers else 0

def median(numbers: list[num]) -> float | int:
    """Calculate the median of a list of numbers."""
    sorted_numbers = sorted(numbers)
    n: int = len(sorted_numbers)
    if n == 0:
        return 0
    mid: int = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    else:
        return sorted_numbers[mid]
    
def mode(numbers: list[num]) -> Union[num, list[num], None]:
    """Calculate the mode of a list of numbers."""
    from collections import Counter
    if not numbers:
        return None
    count = Counter(numbers)
    max_count: int = max(count.values())
    modes = [k for k, v in count.items() if v == max_count]
    return modes if len(modes) > 1 else modes[0]

def standard_deviation(numbers: list[num]) -> float | int:
    """Calculate the standard deviation of a list of numbers."""
    n: int = len(numbers)
    if n == 0:
        return 0
    mean_value: float | int = mean(numbers)
    variance: float = sum((x - mean_value) ** 2 for x in numbers) / n
    return sqrt(variance)

def variance(numbers: list[num]) -> float | int:
    """Calculate the variance of a list of numbers."""
    n: int = len(numbers)
    if n == 0:
        return 0
    mean_value: float | int = mean(numbers)
    return sum((x - mean_value) ** 2 for x in numbers) / n

def distance_between_points(x1: num, y1: num, x2: num, y2: num) -> float:
    """Calculate the distance between two points (x1, y1) and (x2, y2)."""
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def slope_of_line(x1: num, y1: num, x2: num, y2: num) -> float:
    """Calculate the slope of the line passing through points (x1, y1) and (x2, y2)."""
    if x2 - x1 == 0:
        raise ValueError("Slope is undefined for vertical lines.")
    return (y2 - y1) / (x2 - x1)

def midpoint_of_line(x1: num, y1: num, x2: num, y2: num) -> tuple[float, float]:
    """Calculate the midpoint of the line segment between points (x1, y1) and (x2, y2)."""
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def circle_equation(x: num, y: num, h: num, k: num, r: num) -> bool:
    """Check if the point (x, y) lies on the circle with center (h, k) and radius r."""
    return (x - h)**2 + (y - k)**2 == r**2

def linear_equation(m: num, b: num, x: num) -> num:   
    """Calculate the y value of a linear equation y = mx + b for a given x."""
    return m * x + b

def geometric_mean(numbers: list[num]) -> float:
    """Calculate the geometric mean of a list of numbers."""
    product = 1
    n: int = len(numbers)
    if n == 0:
        return 0
    for num in numbers:
        product *= num
    return product ** (1/n)

def harmonic_mean(numbers: list[num]) -> float | int:
    """Calculate the harmonic mean of a list of numbers."""
    n: int = len(numbers)
    if n == 0:
        return 0
    reciprocal_sum: float = sum(1 / num for num in numbers if num != 0)
    if reciprocal_sum == 0:
        return 0
    return n / reciprocal_sum

def fibonacci(n: int) -> list[int]:
    """Generate the first n Fibonacci numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    fib_sequence: list[int] = [0, 1]
    for _ in range(2, n):
        next_fib: int = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_fib)
    return fib_sequence

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num <= 1:
        return False
    for i in range(2, int(sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_factors(num: int) -> list[int]:
    """Return the prime factors of a given number."""
    factors: list[int] = []
    # Check for number of 2s that divide num
    while num % 2 == 0:
        factors.append(2)
        num //= 2
    # num must be odd at this point, so we can skip even numbers
    for i in range(3, int(sqrt(num)) + 1, 2):
        while num % i == 0:
            factors.append(i)
            num //= i
    # This condition is to check if num is a prime number greater than 2
    if num > 2:
        factors.append(num)
    return factors

def lcm(a: int, b: int) -> int:
    """Calculate the least common multiple of two numbers."""
    def gcd(x: int, y: int) -> int:
        while y:
            x, y = y, x % y
        return x
    return abs(a * b) // gcd(a, b)

def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two numbers."""
    while b:
        a, b = b, a % b
    return abs(a)
