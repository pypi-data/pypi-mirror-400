def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def hcf(a, b):
    return gcd(a, b)

def lcm(a, b):
    return abs(a * b) // gcd(a, b)


def prime_factors(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def factors(n):
    return [i for i in range(1, n + 1) if n % i == 0]


def is_perfect(n):
    return sum(factors(n)) - n == n


def is_armstrong(n):
    s = str(n)
    power = len(s)
    total = sum(int(d) ** power for d in s)
    return total == n
