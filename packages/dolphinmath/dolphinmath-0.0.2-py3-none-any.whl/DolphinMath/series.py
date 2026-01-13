def ap_nth(a, d, n):
    return a + (n - 1) * d


def ap_sum(a, d, n):
    return n / 2 * (2 * a + (n - 1) * d)


def gp_nth(a, r, n):
    return a * (r ** (n - 1))


def gp_sum(a, r, n):
    if r == 1:
        return a * n
    return a * (r**n - 1) / (r - 1)
