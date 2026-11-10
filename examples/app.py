def average(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)


def main():
    scores = []
    print("Average score:", average(scores))


main()
