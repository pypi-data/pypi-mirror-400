from math import sqrt
def primes(a,b):
    for i in range(a,b+1):
        if i<2:
            continue
        for j in range(2,int(sqrt(i))+1):
            if i%j==0:
                break
        else:
            print(f"{i}")


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def list_primes(a, b):
    return [i for i in range(a, b + 1) if is_prime(i)]


def count_primes(a, b):
    return len(list_primes(a, b))


def nth_prime(n):
    count = 0
    num = 2
    while True:
        if is_prime(num):
            count += 1
            if count == n:
                return num
        num += 1


def next_prime(n):
    num = n + 1
    while not is_prime(num):
        num += 1
    return num
