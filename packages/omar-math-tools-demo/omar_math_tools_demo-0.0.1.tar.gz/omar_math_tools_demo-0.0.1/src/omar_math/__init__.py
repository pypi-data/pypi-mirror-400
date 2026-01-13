def is_prime(n):
    """Check if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def get_factorial(n):
    """Calculate factorial of a number."""
    if n < 0:
        return None
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def greet_omar():
    """A special greeting from Omar's package."""
    return "Welcome to Omar's Math Tools! Let's calculate."
