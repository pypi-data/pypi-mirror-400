#!/usr/bin/env python2
# coding: utf-8


int_types = (int, int)
list_like = (type([]), type(()))

compatible_types = {
    type(None): (type(None),),
    int: (
        type(None),
        int,
    ),
    float: (
        type(None),
        int,
        float,
    ),
    str: (type(None), str),
    tuple: (
        type(None),
        tuple,
    ),
    list: (
        type(None),
        list,
    ),
}


class RangeException(Exception):
    pass


class Unmergeable(RangeException):
    pass


class ValueRange(list):
    def __init__(self, left, right, val=None):
        assert_compatible(left, right)

        if cmp_boundary(left, right) > 0:
            raise ValueError(
                "left not smaller or equal right: {left}, {right}".format(left=repr(left), right=repr(right))
            )

        super(ValueRange, self).__init__([left, right, val])

    def cmp(self, b):
        # if a and b can be merged into one range, we say a == b
        #
        # Different from Range: adjacent ValueRange-s are not equal,
        # because they have their own value bound and can not be merged.

        if cmp_boundary(self[0], b[1]) >= 0:
            return 1

        if cmp_boundary(b[0], self[1]) >= 0:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0

    def intersect(self, b):
        if self.cmp(b) != 0:
            return None

        rst = [None, None] + self[2:]

        if self.cmp_left(b[0]) < 0:
            rst[0] = b[0]
        else:
            rst[0] = self[0]

        if self.cmp_right(b[1]) > 0:
            rst[1] = b[1]
        else:
            rst[1] = self[1]

        if rst[0] is not None and rst[0] == rst[1]:
            return None

        return rst

    def substract(self, b):
        if self.cmp(b) > 0:
            # keep value for ValueRange
            return [None, self.dup() + self[2:]]

        if self.cmp(b) < 0:
            # keep value for ValueRange
            return [self.dup() + self[2:], None]

        # keep value for ValueRange
        rst = [None, None]

        if self.cmp_left(b[0]) < 0:
            o = [self[0], b.prev_right()] + self[2:]
            rst[0] = self.__class__(*o)

        if b.cmp_right(self[1]) < 0:
            o = [b.next_left(), self[1]] + self[2:]
            rst[1] = self.__class__(*o)

        return rst

    def cmp_left(self, pos):
        # left is None means it is negative infinite
        return cmp_val(self[0], pos, none_cmp_finite=-1)

    def cmp_right(self, pos):
        # right is None means it is positive infinite
        return cmp_val(self[1], pos, none_cmp_finite=1)

    def is_adjacent(self, b):
        """
        Check if this range is at left of `other` and they are adjacent and can be
        merged into one range.
        :param b: is another `Range` instance.
        :return:`True` for `[1, 2] and [2, 3]`
        `False` for `[1, 2] and [3, 4]` or `[1, 2] and [1, 3]`
        """
        return cmp_boundary(b[0], self[1]) == 0

    def has(self, pos):
        """
        Return True if `val` is in this range. Otherwise `False`.
        :param pos: is the value to check.
        :return: bool
        """
        return self.cmp_left(pos) <= 0 and self.cmp_right(pos) > 0

    def length(self):
        if self[0] is None or self[1] is None:
            return float("inf")

        if isinstance(self[0], str):
            a, b = self[:2]
            max_len = max([len(a), len(b)])

            rst = 0.0
            ratio = 1.0
            for i in range(max_len):
                if i >= len(a):
                    va = 0.0
                else:
                    va = ord(a[i]) + 1.0

                if i >= len(b):
                    vb = 0.0
                else:
                    vb = ord(b[i]) + 1.0
                rst += (vb - va) / 257.0 * ratio
                ratio /= 257.0

            return rst
        else:
            return self[1] - self[0]

    def dup(self):
        return self.__class__(*self)

    def next_left(self):
        return self[1]

    def prev_right(self):
        return self[0]

    def val(self):
        return self[2]

    def set(self, v):
        self[2] = v

    def __and__(self, b):
        return self.intersect(b)

    def __rand__(self, b):
        return self.intersect(b)


class Range(ValueRange):
    """
    A continuous range.
    Range is left-close and right-open.
    E.g. a range `[1, 3]` has 2 elements `1` and `2`, but `3` is not in this range.
    """

    def __init__(self, left, right):
        """
        :param left: specifies the left close boundary, which means `left` is in in this range.
        :param right: specifies the right open boundary, which means `right` is **NOT** in this range.
        """
        assert_compatible(left, right)

        if cmp_boundary(left, right) > 0:
            raise ValueError(
                "left not smaller or equal right: {left}, {right}".format(left=repr(left), right=repr(right))
            )

        super(ValueRange, self).__init__([left, right])

    def cmp(self, b):
        """
        Compare this range with `other`.
        :param b: is another `Range` instance.
        :return: `1` if this range is on the right of `other`.
                 `-1` if this range is on the left of `other`.
                 `0` if this range overlaps with `other` or they are adjacent ranges.
        """
        # if a and b can be merged into one range, we say a == b
        #
        # Different from ValueRange: adjacent Range-s are equal,
        # because they can be merged into one.

        if cmp_boundary(self[0], b[1]) > 0:
            return 1

        if cmp_boundary(b[0], self[1]) > 0:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0


class IntIncRange(Range):
    """
    `IntIncRange` is similiar to `Range` and shares the same set of API, except it
    limits value types to int or long, and its right boundary is closed, thus unlike
    `Range`(right boundary is open), 2 is in `[1, 2]`.
    """

    def __init__(self, left, right):
        if left is not None and type(left) not in int_types:
            raise TypeError("{l} {ltyp} is not int or None".format(l=left, ltyp=type(left)))

        if right is not None and type(right) not in int_types:
            raise TypeError("{r} {rtyp} is not int or None".format(r=right, rtyp=type(right)))

        if cmp_boundary(left, right) > 0:
            raise ValueError("left not smaller or equal right: {left}, {right}".format(left=left, right=right))

        list.__init__(self, [left, right])

    def cmp(self, b):
        # if a and b can be merged into one range, we say a == b

        if None not in (self[0], b[1]) and self[0] - b[1] > 1:
            return 1

        if None not in (b[0], self[1]) and b[0] - self[1] > 1:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0

    def is_adjacent(self, b):
        return None not in (b[0], self[1]) and self[1] + 1 == b[0]

    def has(self, pos):
        return (
            cmp_val(self[0], pos, none_cmp_finite=-1) <= 0
            and cmp_val(pos, self[1], none_cmp_finite=1) <= 0
            and type(pos) in int_types
        )

    def length(self):
        if None in self:
            return float("inf")

        return self[1] - self[0] + 1

    def next_left(self):
        return self[1] + 1

    def prev_right(self):
        return self[0] - 1


class RangeDict(list):
    """
    `RangeDict` defines a mapping from ranges to values.

    Adjacent ranges such as `(0, 1), (1, 2)` can exist in `RangeDict`
    but can not exist in `RangeSet`.
    Because in `RangeDict` each range there is a value bound.

    Difference from `RangeSet`:
    Adjacent ranges such as `(0, 1), (1, 2)` can exist in `RangeDict`
    but can not exist in `RangeSet`.
    Because in `RangeDict` each range there is a value bound.
    """

    default_range_clz = ValueRange

    # dimension = 1 indicates the value is a RangeDict whose value is any type.
    # dimension = 2 indicates the value is a RangeDict thus to represent a 2D
    # range dict.
    dimension = 1

    def __init__(self, iterable=None, range_clz=None, dimension=None):
        """
        are same as `RangeSet` except the default value for `range_clz` is `ValueRange` instead of `Range`.
        :param iterable:
        :param range_clz:

        :param dimension: specifies if to convert the value in it into a nested `RangeDict`.
        It is used to create multi dimension RangeDict.
        By default it is `1`.
        """
        if iterable is None:
            iterable = []

        if dimension is not None:
            self.dimension = int(dimension)

        if self.dimension < 1:
            raise ValueError("dimension must >= 1, but: {d}".format(d=self.dimension))

        self.range_clz = range_clz or self.default_range_clz

        super(RangeDict, self).__init__([self.range_clz(*x) for x in iterable])

        for i in range(0, len(self) - 1):
            if self[i].cmp(self[i + 1]) != -1:
                raise ValueError(
                    "range[{i}] {ri} does not smaller than range[{j}] {ripp}".format(
                        i=i,
                        j=i + 1,
                        ri=self[i],
                        ripp=self[i + 1],
                    )
                )

        if self.dimension > 1:
            for rng in self:
                v = rng.val()
                if v is not None:
                    v = self.__class__(v, range_clz=self.range_clz, dimension=self.dimension - 1)
                    rng.set(v)

    def add(self, rng, val=None):
        """
        Add a mapping from range to value into `RangeDict`.
        :param rng: a two element iterable that defines a range.
        :param val: value of any data type.
        :return: Nothing
        """
        if val is not None and self.dimension > 1:
            val = self.__class__(val, range_clz=self.range_clz, dimension=self.dimension - 1)

        rng = _to_range(self.range_clz, list(rng) + [val])

        i = bisect_left(self, rng)

        while i < len(self):
            if rng.cmp(self[i]) == 0:
                left, right = substract_range(self[i], rng)
                if left is None:
                    if right is None:
                        self.pop(i)
                    else:
                        self[i] = right
                        i += 1
                else:
                    if right is None:
                        self[i] = left
                        i += 1
                    else:
                        self.pop(i)
                        self.insert(i, right)
                        self.insert(i, left)
                        i += 2
            else:
                break

        if rng[0] is None:
            self.insert(0, rng)
        else:
            for i in range(len(self)):
                if self[i].cmp_left(rng[0]) > 0:
                    self.insert(i, rng)
                    break
            else:
                self.append(rng)

        self.normalize()

    def get(self, pos, *positions):
        """
        :param pos: position in `RangeDict`
        :param positions: the nested position to get if this `RangeDict.dimension > 1`.
        :return: the value of range that `pos` is in.
        If `pos` is not in any ranges, `KeyError` is raised.
        """
        rng = [pos, None]
        i = bisect_left(self, rng)

        if i == len(self) or not self[i].has(pos):
            raise KeyError("not in range: " + repr(pos))

        v = self[i].val()

        if len(positions) > 0:
            if len(positions) + 1 <= self.dimension:
                v = v.get(*positions)
            else:
                raise TypeError("too many position to get")
        return v

    def get_min(self, is_lt=None):
        """
        Get range of the minimum value in the range dict. If minmum value has more than one range, then get
        the first one.
        :param is_lt: is a function that receives 2 arguments `a` and `b`, returns `True` if `a` is "smaller" than `b`,
        otherwise return `False`.
        Example:
        ```
        def is_lt(a, b):
            return a < b
        ```
        If `is_lt` is `None`, use `a < b` to decide 'a' is smaller than 'b'.
        :return:
        - `i`:the index of the minimum value in the range dict.

        - `rng`:a `ValueRange`, which is the range of the minimum value in the range dict.

        - `val`: the minimum value in the range dict.
        """
        if len(self) == 0:
            raise ValueError("range dict is empty")

        def default_is_lt(a, b):
            return a < b

        if is_lt is None:
            is_lt = default_is_lt

        min_val_idx = 0
        for i in range(1, len(self)):
            if is_lt(self[i].val(), self[min_val_idx].val()):
                min_val_idx = i

        min_val_rng = self[min_val_idx]

        return min_val_idx, min_val_rng, min_val_rng.val()

    def has(self, pos):
        rng = [pos, None]
        i = bisect_left(self, rng)

        if i == len(self):
            return False

        return self[i].has(pos)

    def length(self):
        rst = 0
        for rng in self:
            rst += rng.length()

        return rst

    def normalize(self):
        """
        Reduce number of elements by merging adjacent ranges those have the same value into one continuous range.
        :return: Nothing.
        """
        i = 0
        while i < len(self) - 1:
            curr = self[i]
            nxt = self[i + 1]

            if not curr.is_adjacent(nxt):
                i += 1
                continue

            # compare value if there is
            if curr[2:] == nxt[2:]:
                o = [curr[0], nxt[1]] + curr[2:]
                self[i] = self.range_clz(*o)
                self.pop(i + 1)
            else:
                i += 1
                continue

    def find_overlapped(self, rng):
        """
        Find all ranges those overlaps with `rng`.
        :param rng: a range iterable with at least 2 elements, such `list`, `tuple`, `Range` or `ValueRange`.
        :return: a instance of `self.__class__` with `Range` or `ValueRange` elements those overlaps with `rng`.
        """
        rng = list(rng)
        rst = []

        i = bisect_left(self, rng)
        while i < len(self):
            if self[i].cmp(rng) == 0:
                if self[i].intersect(rng) is not None:
                    rst.append(self.range_clz(*self[i]))
                else:
                    # adjacent ranges
                    pass
                i += 1
            else:
                break

        return self.__class__(rst)


class RangeSet(RangeDict):
    """
    A series of int `Range`.
    All ranges in it are ascending ordered, non-overlapping and non-adjacent.
    """

    default_range_clz = Range

    def add(self, rng):
        """
        It adds a new range into this range set and if possible, collapse it with
        overlapping or adjacent range.
        :param rng:  is a `Range` or a 2 element tuple or list.
        :return: nothing, but modify the range-set in place.
        """
        rng = _to_range(self.range_clz, list(rng))

        i = bisect_left(self, rng)

        while i < len(self):
            if rng.cmp(self[i]) == 0:
                rng = union_range(rng, self[i])
                self.pop(i)
            else:
                break

        self.insert(i, rng)


class IntIncRangeSet(RangeSet):
    """
    It is similiar to `RangeSet` and shares the same set of API, except the default
    class for element in it is `IntIncRange`, not `Range`.
    """

    default_range_clz = IntIncRange


def union(a, *bs):
    """
    Return a new union set `RangeSet` of all `a` and `others`.
    :param a: a `RangeSet` instance.
    :param bs: `RangeSet` instances
    :return: a new `RangeSet` instance.
    """
    u = a
    for b in bs:
        u = _union(u, b)
    return u


def _union(a, b):
    if len(a) == 0:
        return RangeSet(b, range_clz=b.range_clz)

    if len(b) == 0:
        return RangeSet(a, range_clz=b.range_clz)

    rst = []
    i, j = 1, 0

    rng = a[0]

    while i < len(a) or j < len(b):
        a_ge_b = None

        if i == len(a):
            a_ge_b = True
        elif j == len(b):
            a_ge_b = False
        else:
            a_ge_b = a[i].cmp_left(b[j][0]) >= 0

        if a_ge_b:
            nxt = b[j]
            j += 1
        else:
            nxt = a[i]
            i += 1

        if rng.cmp(nxt) == 0:
            rng = union_range(rng, nxt)
        else:
            assert rng.cmp(nxt) < 0
            rst.append(rng)
            rng = nxt

    rst.append(rng)

    return RangeSet(rst, range_clz=b.range_clz)


def substract(a, *bs):
    """
    Return a new `RangeSet` with all ranges in `others` removed from `a`.
    :param a: a `RangeSet` instance.
    :param bs: `RangeSet` instances
    :return: a new `RangeSet` instance.
    """
    s = a
    for b in bs:
        s = _substract(s, b)
    return s


def _substract(a, b):
    if len(a) == 0:
        return a.__class__([], range_clz=a.range_clz, dimension=a.dimension)

    if len(b) == 0:
        return a.__class__(a, range_clz=a.range_clz, dimension=a.dimension)

    rst = []

    for ra in a:
        sb = a.range_clz(*ra)

        j = bisect_left(b, ra)

        while j < len(b) and sb.cmp(b[j]) == 0:
            u1, u2 = substract_range(sb, b[j])

            if u1 is not None:
                rst.append(u1)

            sb = u2

            if sb is None:
                break

            j += 1

        if sb is not None:
            rst.append(sb)

    return a.__class__(rst, range_clz=a.range_clz, dimension=a.dimension)


def intersect(a, b):
    """
    Return a new intersection set `RangeSet` of all `a` and `others`.
    :param a: a `RangeSet` instance.
    :param b: `RangeSet` instances.
    :return: a new `RangeSet` instance.
    """
    return substract(a, substract(a, b))


def assert_type_valid(typ):
    if typ not in compatible_types:
        raise TypeError("{typ} is not comparable".format(typ=typ))


def _to_range(range_clz, rng):
    # rangeset is 2 element iterable, rangedict is 3 element iterable
    if len(rng) < 2:
        raise ValueError("range length is at least 2 but {l}: {rng}".format(l=len(rng), rng=rng))

    return range_clz(*rng)


def cmp_boundary(left, right):
    if left is None:
        # left is -inf
        return -1

    if right is None:
        # right is inf
        return -1

    if left < right:
        return -1
    elif left > right:
        return 1
    else:
        return 0


def cmp_val(a, b, none_cmp_finite=1):
    # compare two value. any of them can be None.
    # None means positive infinite or negative infinite, defined by none_cmp_finite

    if a is None:
        if b is None:
            return 0
        else:
            # compare(none, b)
            return none_cmp_finite
    else:
        if b is None:
            # compare(b, none) = -compare(none, b)
            return -none_cmp_finite
        else:
            if a < b:
                return -1
            elif a > b:
                return 1
            else:
                return 0


def union_range(a, b):
    if a.cmp(b) != 0:
        raise Unmergeable(a, b)

    if a[0] is None or b[0] is None:
        left = None
    else:
        left = min([a[0], b[0]])

    if a[1] is None or b[1] is None:
        right = None
    else:
        right = max([a[1], b[1]])

    return a.__class__(left, right)


def substract_range(a, b):
    return a.substract(b)


def bisect_left(a, x, lo=0, hi=None):
    # Find the left-most i so that a[i] >= x
    # Thus i is where to a.insert(i, x)

    if lo < 0:
        raise ValueError("lo must be non-negative")

    if hi is None:
        hi = len(a)

    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid].cmp(x) < 0:
            lo = mid + 1
        else:
            hi = mid
    return lo


def assert_compatible(left, right):
    if not is_compatible(left, right):
        raise TypeError(
            "{left} {ltyp} is incompatible with {right} {rtyp}".format(
                left=repr(left), ltyp=type(left), right=repr(right), rtyp=type(right)
            )
        )


def is_compatible(left, right):
    if left is None or right is None:
        return True

    if type(left) in compatible_types.get(type(right), ()):
        return True

    if type(right) in compatible_types.get(type(left), ()):
        return True

    return False
