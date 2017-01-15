__version__ = '0.0.1'

class Rope(object):
    # NOTE: self.left and self.right should either both point to subnodes or
    #       both set to `None`, so checking both should not be necessary.

    def __init__(self, data=''):
        if isinstance(data, list):
            if len(data) == 0:
                self.__init__()
            elif len(data) == 1:
                self.__init__(data[0])
            else:
                # Round-up division (to match rope arithmetic associativity)
                idiv = len(data) // 2 + (len(data) % 2 > 0)

                self.left = Rope(data[:idiv])
                self.right = Rope(data[idiv:])
                self.data = ''
                self.length = self.left.length + self.right.length
        elif isinstance(data, str):
            self.left = None
            self.right = None
            self.data = data
            self.length = len(data)
        else:
            raise TypeError('Only strings are currently supported')

        # Word iteration
        self.current = self

    def __eq__(self, other):
        if (self.left and self.right) and (other.left and other.right):
            return self.left == other.left and self.right == other.right
        elif (self.left and self.right) or (other.left and other.right):
            return False
        else:
            return self.data == other.data

    def __add__(self, other):
        # TODO: Automatically collapse empty ropes
        r = Rope()
        r.left = self
        r.right = other
        r.length = self.length + other.length
        r.current = self
        return r

    def __getitem__(self, index):

        if isinstance(index, int):
            if index < 0:
                index += self.length

            if index < 0 or index >= self.length:
                raise IndexError('rope index out of range')

            if self.left and self.right:
                if index < self.left.length:
                    return self.left[index]
                else:
                    return self.right[index - self.left.length]
            else:
                return Rope(self.data[index])

        elif isinstance(index, slice):
            # Slice logic taken from CPython's `sliceobject.c'
            # It may be possible to streamline this a bit in Python

            # Step initialization
            if index.step is None:
                step = 1
            else:
                if index.step == 0:
                    raise ValueError('slice step cannot be zero')
                else:
                    step = index.step

            # Default start/stop indices
            if step < 0:
                default_start = self.length - 1
                default_stop = -1
            else:
                default_start = 0
                default_stop = self.length

            # Start index
            if index.start is None:
                start = default_start
            else:
                start = index.start
                if start < 0:
                    start += self.length
                if start < 0:
                    start = 0 if step > 0 else -1
                if start >= self.length:
                    start = self.length if step > 0 else (length - 1)

            # Stop index
            if index.stop is None:
                stop = default_stop
            else:
                stop = index.stop
                if stop < 0:
                    stop += self.length
                if stop < 0:
                    stop = 0 if step > 0 else -1
                if stop >= self.length:
                    stop = self.length if step > 0 else (length - 1)

            # Apply slice
            if self.left and self.right:
                if start < self.left.length:
                    if stop <= self.left.length:
                        return self.left[start:stop:step]
                    else:
                        return (self.left[start::step]
                                + self.right[(start + step - self.left.length) % step
                                             :(stop - self.left.length):step])
                else:
                    return self.right[(start - self.left.length)
                                      :(stop - self.left.length):step]
            else:
                if start <= 0 and stop >= self.length and step == 1:
                    return self
                else:
                    # stop = -1 for negative stride would be incorrectly
                    # converted to (self.length - 1) by the slice operation.
                    # This if-block reverts the explicit value to None.
                    if step < 0 and stop == -1:
                        stop = None
                    return Rope(self.data[start:stop:step])

        else:
            raise TypeError('rope indices must be integers or slices, not {}'
                            ''.format(type(index).__name__))

    def __repr__(self):
        # TODO: Parentheses are too conservative, need to clean this up
        if self.left and self.right:
            return '{}{} + {}{}'.format('(' if self.left else '',
                                        self.left.__repr__(),
                                        self.right.__repr__(),
                                        ')' if self.right else '')
        else:
            return "Rope('{}')".format(self.data)

    def __str__(self):
        if self.left and self.right:
            return self.left.__str__() + self.right.__str__()
        else:
            return self.data

    def __iter__(self):
        return self

    def __next__(self):
        if self.current:
            if self.left and self.right:
                try:
                    return next(self.left)
                except StopIteration:
                    self.current = self.right
                return next(self.right)
            else:
                self.current = None
                return self.data
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

    # API
    def reduce(self):
        """Search the tree and remove any redundant nodes."""
        raise NotImplementedError

    def insert(self, index, s):
        """Insert string s at index i."""
        raise NotImplementedError
