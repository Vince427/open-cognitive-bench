def average(nums):
    # empty input must return 0, not divide by zero
    if not nums:
        return 0
    return sum(nums) / len(nums)
