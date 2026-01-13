from sys import argv


def permutations(lst: list, k: int) -> list[list]:
    """
    Generate all permutations of a list of elements.
    """
    if (k == 1):
        return [lst.copy()]
    ret = permutations(lst, k - 1)
    for i in range(k - 1):
        if k % 2 == 0:
            lst[i], lst[k - 1] = lst[k - 1], lst[i]
        else:
            lst[0], lst[k - 1] = lst[k - 1], lst[0]
        tmp = permutations(lst, k - 1)
        ret.extend(tmp)
    return ret


if __name__ == "__main__":
    if len(argv) < 2:
        print("please enter a list of number to permute")
        exit(1)

    lst = [elem for elem in argv[1:]]
    print(lst)
    ret = permutations(lst, len(lst))
    print("---------------------------------------")
    for line in ret:
        for elem in line:
            print(elem, end=" ")
        print()
