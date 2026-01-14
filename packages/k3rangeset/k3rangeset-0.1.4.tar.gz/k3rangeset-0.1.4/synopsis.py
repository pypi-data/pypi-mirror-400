import k3rangeset

a = k3rangeset.RangeSet([[1, 5], [10, 20]])
a.has(1)  # True
a.has(8)  # False
a.add([5, 7])  # [[1, 7], [10, 20]]

inp = [
    [
        0,
        1,
        [
            ["a", "b", "ab"],
            ["b", "d", "bd"],
        ],
    ],
    [
        1,
        2,
        [
            ["a", "c", "ac"],
            ["c", "d", "cd"],
        ],
    ],
]

r = k3rangeset.RangeDict(inp, dimension=2)
print(r.get(0.5, "a"))  # 'ab'
print(r.get(1.5, "a"))  # 'ac'
