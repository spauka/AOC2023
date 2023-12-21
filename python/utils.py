import re
from pathlib import Path
import numpy as np
from types import GeneratorType
from collections.abc import Iterable
from itertools import chain, product
from functools import partial

NUM = re.compile("([\d]+)")
NEG = re.compile("(-?[\d]+)")
DEC = re.compile("(-?[\d]+(?:.[\d]+))")

def read_numbers(inp: str, allow_negative=False, allow_decimal=False):
    if not allow_negative and not allow_decimal:
        inps = NUM.findall(inp)
    elif allow_negative and not allow_decimal:
        inps = NEG.findall(inp)
    else:
        inps = DEC.findall(inp)
    return [int(inp) for inp in inps]

class Coord(tuple):
    def __new__(cls, *args):
        if isinstance(args[0], Coord):
            return args[0]
        if isinstance(args[0], tuple) and len(args) == 1:
            return super(Coord, cls).__new__(cls, args[0])
        if isinstance(args[0], (Iterable, GeneratorType)) and len(args) == 1:
            return super(Coord, cls).__new__(cls, args[0])

        return super(Coord, cls).__new__(cls, args)

    def __add__(self, o):
        if not isinstance(o, (tuple, Coord)) or len(self) != len(o):
            raise TypeError(f"Must be a tuple of size {len(self)}")
        return Coord(x+y for x, y in zip(self, o))
    def __mul__(self, o):
        if isinstance(o, int):
            return Coord(x*o for x in self)
        if not isinstance(o, (tuple, Coord)) or len(self) != len(o):
            raise TypeError(f"Must be a tuple of size {len(self)}")
        return Coord(x*y for x, y in zip(self, o))

    def __sub__(self, o):
        if not isinstance(o, (tuple, Coord)) or len(self) != len(o):
            raise TypeError(f"Must be a tuple of size {len(self)}")
        return Coord(x-y for x, y in zip(self, o))

    def __mod__(self, o):
        if not isinstance(o, (tuple, Coord)) or len(self) != len(o):
            raise TypeError(f"Must be a tuple of size {len(self)}")
        return Coord(x%y for x, y in zip(self, o))

    def dist(self, o):
        if not isinstance(o, (tuple, Coord)) or len(self) != len(o):
            raise TypeError(f"Must be a tuple of size {len(self)}")
        return sum(abs(c1-c2) for c1, c2 in zip(self, o))

    def mag(self):
        return sum(abs(c) for c in self)
    def mag_l2(self):
        return np.sqrt(sum(c**2 for c in self))

    def __repr__(self):
        return f"Coord{super().__repr__()}"

class Range:
    def __init__(self, start, stop):
        if stop < start:
            raise ValueError(f"{stop} must be <= {start}")
        self.start = start
        self.stop = stop

    def __repr__(self):
        return f"Range({self.start}, {self.stop})"
    def __len__(self):
        return self.stop - self.start + 1

    def __add__(self, o: "Range"):
        olap = self.overlaps(o)
        if not olap:
            raise RuntimeError("Cannot combine non-overlapping ranges {self} and {o}")
        if olap == -1:
            nr = Range(self.start, o.stop)
            return nr
        else:
            nr = Range(o.start, self.stop)
            return nr

    def contains(self, o: "Range"):
        if (self.start <= o.start and
            self.stop >= o.stop):
            return True
        return False
    def iscontained(self, o: "Range"):
        return o.contains(self)

    def overlaps(self, o: "Range"):
        if self.start <= o.start <= self.stop <= o.stop:
            return -1
        elif o.start <= self.start <= o.stop <= self.stop:
            return 1
        else:
            return 0

class Neighbours:
    STRT = {
        'N': Coord(0, 1),
        'E': Coord(1, 0),
        'S': Coord(0, -1),
        'W': Coord(-1, 0)
    }
    NDIRS = {
        'U': Coord(0, 1),
        'R': Coord(1, 0),
        'D': Coord(0, -1),
        'L': Coord(-1, 0),
    }
    DIAG = {
        'NE': STRT['N'] + STRT['E'],
        'SE': STRT['S'] + STRT['E'],
        'SW': STRT['S'] + STRT['W'],
        'NW': STRT['N'] + STRT['W'],
    }
    DIRS = STRT | NDIRS | DIAG

    def __init__(self, parent, incl_diag=False):
        self._parent = parent
        self.incl_diag = incl_diag

    def __getitem__(self, coord):
        if not isinstance(coord, (Coord, tuple)) or len(coord) != 2:
            raise TypeError(f"index must be a tuple or Coord of length 2. Got: {coord}")
        return BoundNeighbours(self._parent, self.incl_diag, coord)

    def __setitem__(self, coord, val):
        neighbours = self[coord]
        for d in neighbours.valid_dirs:
            setattr(neighbours, d, val)

    def __repr__(self):
        return f"Neighbours(incl_diag={self.incl_diag})"


class BoundNeighbours(Neighbours):
    def __init__(self, parent, incl_diag=False, coord=None):
        super().__init__(parent, incl_diag)
        self.coord = Coord(coord)

        self._valid_dirs = []
        self._valid_coords = []
        for name, dir in self.STRT.items():
            if self.validate_coord(self.coord + dir):
                setattr(self, name, property(partial(self.get_at_offset, dir), partial(self.set_at_offset, dir)))
                self._valid_dirs.append(name)
                self._valid_coords.append(self.coord + dir)
        if self.incl_diag:
            for name, dir in self.DIAG.items():
                if self.validate_coord(self.coord + dir):
                    setattr(self, name, property(partial(self.get_at_offset, dir), partial(self.set_at_offset, dir)))
                    self._valid_dirs.append(name)
                    self._valid_coords.append(self.coord + dir)
        self._valid_dirs = tuple(self._valid_dirs)
        self._valid_coords = tuple(self._valid_coords)

    def __iter__(self):
        if self.incl_diag:
            dirs = chain(*zip(self.STRT.values(), self.DIAG.values()))
        else:
            dirs = self.STRT.values()
        for dir in dirs:
            if self.validate_coord(self.coord + dir):
                yield self.get_at_offset(dir)

    def __getitem__(self, direction):
        if direction not in self.DIRS:
            raise ValueError(f"Unable to resolve direction {direction}. Valid directions are: {', '.join(self.DIRS.keys())}")
        return self.get_at_offset(self.DIRS[direction])

    @property
    def valid_dirs(self):
        return self._valid_dirs
    @property
    def coords(self):
        return self._valid_coords

    def validate_coord(self, coord):
        if any(p<0 for p in coord) or any(p>=l for p, l in zip(coord, self._parent.shape)):
            return False
        return True

    def get_at_offset(self, offset):
        pos = self.coord + offset
        if not self.validate_coord(pos):
            raise IndexError("Coordinate {pos} out of bounds")
        return self._parent.grid[pos]

    def set_at_offset(self, offset, val):
        pos = self.coord + offset
        if not self.validate_coord(pos):
            raise IndexError("Coordinate {pos} out of bounds")
        self._parent.grid[pos] = val

    def __repr__(self):
        return f"Neighbours[{self.coord}] = {list(iter(self))}"

    def __iadd__(self, val):
        for d in self.valid_dirs:
            self._parent.grid[self.coord + self.DIRS[d]] += val
    def __isub__(self, val):
        for d in self.valid_dirs:
            self._parent.grid[self.coord + self.DIRS[d]] -= val

class Grid:
    def __init__(self, xdim, ydim, dtype=int, incl_diag=False):
        self.dtype = dtype
        self.grid = np.zeros((xdim, ydim), dtype=dtype)
        self.incl_diag = incl_diag

    @property
    def neighbours(self):
        return Neighbours(self, self.incl_diag)
    @property
    def n(self):
        return self.neighbours

    @property
    def size(self):
        return self.grid.size
    @property
    def shape(self):
        return self.grid.shape

    def iter_coord(self):
        return map(Coord, product(*(range(x) for x in self.shape)))

    def copy(self):
        new_grid = self.__class__(*self.shape, self.dtype, self.incl_diag)
        new_grid.grid[:] = self.grid
        return new_grid

    def __getitem__(self, coord):
        if isinstance(coord, int):
            return self.grid[:, coord]
        elif isinstance(coord, complex):
            return self.grid[coord.real, coord.imag]
        return self.grid[coord]

    def __setitem__(self, coord, vals):
        if isinstance(coord, int):
            self.grid[:, coord] = vals
        elif isinstance(coord, complex):
            self.grid[coord.real, coord.imag] = vals
        self.grid[coord] = vals

    def __contains__(self, coord):
        if any(p < 0 or p >= l for p, l in zip(coord, self.shape)):
            return False
        return True

    def __repr__(self):
        return repr(self.grid[:,::-1].T)

    def print_grid(self, conv_num=False, sep=""):
        if conv_num:
            for y in range(self.shape[1]):
                print(sep.join(str(b) for b in self[:,-y-1]))
        else:
            for y in range(self.shape[1]):
                print(sep.join(b.decode("ascii") for b in self[:,-y-1]))

    @property
    def tl(self):
        return Coord(0, self.shape[1]-1)
    @property
    def tr(self):
        return Coord(self.shape[0]-1, self.shape[1]-1)
    @property
    def bl(self):
        return Coord(0, 0)
    @property
    def br(self):
        return Coord(self.shape[0]-1, 0)

    @classmethod
    def load_dense_file(cls, file: str | Path, incl_diag=False, dtype=int, conv_char=False):
        lines = []
        with open(file) as f:
            for line in f:
                if not line:
                    continue
                lines.append(list(c for c in line.strip()))

        shape = (len(lines[0]), len(lines))
        grid = Grid(*shape, incl_diag=incl_diag, dtype=dtype)
        for i, line in enumerate(reversed(lines)):
            grid[:, i] = line if not conv_char else [ord(c) for c in line]
        return grid

class InfiniteGrid():
    def __init__(self, def_val=0, incl_diag=False):
        self.grid = {}
        self.incl_diag = incl_diag
        self._def_val = def_val
        self._bl = Coord(0, 0)
        self._tr = Coord(0, 0)

    @property
    def neighbours(self):
        return Neighbours(self, self.incl_diag)
    @property
    def n(self):
        return self.neighbours

    @property
    def size(self):
        shape = self.shape
        return shape[0] * shape[1]
    @property
    def shape(self):
        return self._tr - self._bl + Coord(1, 1)

    def iter_coord(self):
        return product(*(range(cmin, cmax+1) for cmin, cmax in zip(self._bl, self._tr)))

    def copy(self):
        newinst = InfiniteGrid(self._def_val, self.incl_diag)
        newinst.grid = self.grid.copy()
        newinst._bl = self.bl
        newinst._tr = self.tr
        return newinst

    def __valiter(self, coord):
        if isinstance(coord, (int, np.integer)):
            raise IndexError("Can't index a single row in an InfiniteGrid")
        if len(coord) != 2:
            raise IndexError("Index must have dimension two")
        if not (intt := all(isinstance(x, (int, np.integer)) for x in coord)) and not all(isinstance(x, slice) for x in coord):
            print(intt, [np.issubdtype(x, np.integer) for x in coord], coord)
            raise IndexError("Can index by exact position or by slice, not both")
        return intt

    def __getitem__(self, coord):
        intt = self.__valiter(coord)
        if intt:
            return self.grid.get(coord, self._def_val)
        x, y = np.mgrid[coord]
        outarr = np.zeros_like(x)
        for coord in zip(x.flat, y.flat):
            ocoord = Coord(coord) - (x[0][0], y[0][0])
            outarr[ocoord] = self.grid.get(coord, self._def_val)
        return outarr[:,::-1].T

    def __setitem__(self, coord, vals):
        intt = self.__valiter(coord)
        if intt:
            self._bl = Coord(min(_bl, _c) for _bl, _c in zip(self._bl, coord))
            self._tr = Coord(max(_bl, _c) for _bl, _c in zip(self._tr, coord))
            self.grid[coord] = vals
            return
        x, y = np.mgrid[coord]
        if isinstance(vals, type(self._def_val)):
            vals = np.zeros_like(x, dtype=type(self._def_val)) + vals
        vals = np.asarray(vals)
        if vals.shape != x.shape:
            raise ValueError(f"Expected array of shape {x.shape}, got {vals.shape}.")
        for xc, yc, val in zip(x.flat, y.flat, vals.flat):
            self.grid[(xc, yc)] = val

    def __repr__(self):
        indices = tuple(slice(start, end+1) for start, end in zip(self._bl, self._tr))
        return repr(self[indices])

    def asarray(self):
        indices = tuple(slice(start, end+1) for start, end in zip(self._bl, self._tr))
        return self[indices]

    @property
    def tl(self):
        return Coord(self._bl[0], self._tr[1])
    @property
    def tr(self):
        return self._tr
    @property
    def bl(self):
        return self._bl
    @property
    def br(self):
        return Coord(self._tr[0], self._bl[1])
