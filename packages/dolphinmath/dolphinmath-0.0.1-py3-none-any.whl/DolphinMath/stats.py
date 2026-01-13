def mean(nums):
    return sum(nums) / len(nums)


def median(nums):
    nums = sorted(nums)
    n = len(nums)
    mid = n // 2

    if n % 2 == 0:
        return (nums[mid - 1] + nums[mid]) / 2
    return nums[mid]


def mode(nums):
    freq = {}
    for n in nums:
        freq[n] = freq.get(n, 0) + 1
    highest = max(freq.values())
    return [k for k, v in freq.items() if v == highest]
