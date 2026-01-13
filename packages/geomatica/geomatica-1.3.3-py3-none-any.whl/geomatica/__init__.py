from typing import Callable as _Callable, Iterator as _Iterator, Union as _Union, overload as _overload
from abc import ABC as _ABC, abstractmethod as _absd
from types import UnionType as _UnionType
from dataclasses import dataclass as _dataclass
from warnings import filterwarnings as _filterwarnings
__version__ = '1.3.3'
__author__ = 'slycedf'
__email__ = 'svntythsnd@gmail.com'
__license__ = 'MIT'
__description__ = 'Geometric Algebra in Python'
__url__ = 'https://github.com/svntythsnd/geomatica'
_filterwarnings("ignore", category=SyntaxWarning)
class IMultivector(_ABC):
 """
    An ABC representing any Multivector, with type hints and relevant
    docstrings for all user-facing methods.
    """
 __slots__ = ()
 @property
 @_absd
 def algebra(self) -> 'GA':
  """A reference to the Multivector's parent GA.""" 
 @_absd
 def __add__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  pass
 @_absd
 def __radd__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  pass
 @_absd
 def __sub__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  pass
 @_absd
 def __rsub__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  pass
 @_absd
 def __neg__(self) -> 'IMultivector':
  pass
 @_absd
 def __invert__(self) -> 'IMultivector':
  """Return the adjugate of the Multivector.""" 
 @_absd
 def __mul__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  """Return the geometric product of two Multivectors.""" 
 @_absd
 def __rmul__(self, other: int | float) -> 'IMultivector':
  """Return the geometric product of two Multivectors.""" 
 @_absd
 def __pow__(self, other: int | float) -> 'IMultivector':
  pass
 @_absd
 def __rpow__(self, other: int | float) -> 'IMultivector':
  """Exponentiate the Multivector by applying e^(M ln b).""" 
 @_absd
 def __abs__(self) -> float:
  """Return the determinant of the Multivector.""" 
 @_absd
 def __matmul__(self, grade: int) -> 'IMultivector':
  """Extract a specific grade of the Multivector.""" 
 @_absd
 def __truediv__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  pass
 @_absd
 def __rtruediv__(self, other: int | float) -> 'IMultivector':
  pass
 @_absd
 def __or__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  """Return the Perwass dot product of two Multivectors.""" 
 @_absd
 def __ror__(self, other: int | float) -> 'IMultivector':
  """Return the Perwass dot product of two Multivectors.""" 
 @_absd
 def __xor__(self, other: _Union[int, float, 'IMultivector']) -> 'IMultivector':
  """Return the wedge product of two Multivectors.""" 
 @_absd
 def __rxor__(self, other: int | float) -> 'IMultivector':
  """Return the wedge product of two Multivectors.""" 
 @_absd
 def __pos__(self) -> int | None:
  """Return the grade of the Multivector if it's homogenous, None otherwise.""" 
 @_absd
 def __format__(self, form: str) -> str:
  pass
 @_absd
 def __str__(self) -> str:
  pass
 @_absd
 def __float__(self) -> float:
  """Convert a scalar Multivector to a float.""" 
 @_absd
 def __int__(self) -> float:
  """Convert a scalar Multivector to an int.""" 
 @_absd
 def __eq__(self, other: _Union[int, float, 'IMultivector']) -> bool:
  pass
 @_absd
 def __call__(self, other: _Callable[[int], int|float]) -> 'IMultivector':
  """Scale each grade of the Multivector with the provided Callable.""" 
 @_absd
 def __hash__(self) -> int:
  pass
 @_absd
 def exp(self) -> 'IMultivector':
  """Compute e^M either by decomposing the Multivector into commuting blocks or, if that fails, explicit Taylor expansion.""" 
 
class NoAdjugateError(ValueError):
 """Raised when a Multivector does not admit an adjugate."""
 __slots__ = ()
class GAMismatchError(TypeError):
 """Raised when two Multivectors from different GA instances are combined."""
 __slots__ = ()
_subscripts = str.maketrans('0123456789','₀₁₂₃₄₅₆₇₈₉')
def _merge_sort_parity(arr):
 if len(arr) <= 1 : return arr, 1
 mid = len(arr) // 2
 left, p_left = _merge_sort_parity(arr[:mid])
 right, p_right = _merge_sort_parity(arr[mid:])
 merged = []
 parity = p_left * p_right
 i = j = 0
 while i < len(left) and j < len(right):
  if left[i] <= right[j]:
   merged.append(left[i])
   i += 1
   continue
  merged.append(right[j])
  j += 1
  if (len(left) - i) & 1: parity = -parity
 merged.extend(left[i:])
 merged.extend(right[j:])
 return merged, parity
@_dataclass(frozen=True, slots=True)
class _RuntimeCallableWrapper:
 callable: _Callable
 return_type: type|_UnionType
 name: str
 type_name: str
 def __call__(self, *args):
  if not isinstance(out := self.callable(*args), self.return_type):raise TypeError(f"{self.name} must be a {self.type_name}, but got {type(out).__name__} for input {', '.join(str(x) for x in args)}")
  return out
 
class GA:
 """
    A container representing a Geometric Algebra.

    Attributes:
        signature: a Callable returning the square of the nth basis vector.
        epsilon_order: integer offset for machine epsilon comparisons.
                       The effective bound for treating numbers as zero is
                       2^epsilon_order times the machine epsilon.
    """
 __slots__ = ('signature', 'epsilon_order', '__Multivector')
 signature: _Callable[[int], int|float]
 epsilon_order: int
 def __setattr__(self, name, value):
  match name:
   case 'epsilon_order' if not isinstance(value, int): raise TypeError(f"GA.{name} must be an int, but got {type(value).__name__}")
   case 'signature':
    if not isinstance(value, _Callable): raise TypeError(f"GA.{name} must be a Callable[[int], int|float], but got {type(value).__name__}")
    from inspect import signature
    if (l := len(signature(value).parameters)) != 1: raise TypeError(f"GA.{name} must be a Callable[[int], int|float], but got {l} arguments")
    value = _RuntimeCallableWrapper(value,int|float,f'GA.{name}','Callable[[int], int|float]')
    
   
  super().__setattr__(name, value)
 def __init__(ga, *, signature:_Callable[[int], int|float]= lambda x:1.0, epsilon_order:int=0):
  """
        Create a Geometric Algebra.

        Args:
            signature: a Callable returning the square of the nth basis vector.
                       Defaults to 1 for all.
            epsilon_order: integer offset for machine epsilon comparisons.
                       The effective bound for treating numbers as zero is
                       2^epsilon_order times the machine epsilon. Defaults to 0.
        """
  ga.signature = signature
  ga.epsilon_order = epsilon_order
  class Multivector(IMultivector):
   @property
   def algebra(self) -> GA : return ga
   __slots__ = ('__d', '__decomposition', '__sigma', '__abs')
   def __init__(self, keys:dict[int, float], **argv) -> None:
    from math import ldexp
    self.__d = {k:v for k, v in keys.items() if 1+abs(ldexp(v,-self.algebra.epsilon_order)) != 1}
    self.__decomposition = argv.get("decomposition", ...)
    self.__sigma = argv.get("sigma", ...)
    self.__abs = argv.get("abs", ...)
   def __add__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector':
    if isinstance(other, int | float) : return Multivector({0: self.__d.get(0, 0) + other,**{mask: value for mask, value in self.__d.items() if mask != 0}},decomposition=self.__decomposition, sigma=self.__sigma)
    if not isinstance(other, Multivector):
     if isinstance(other, IMultivector): raise GAMismatchError("Cannot combine Multivectors from different GA instances")
     return NotImplemented
    return Multivector({mask: self.__d.get(mask, 0) + other._Multivector__d.get(mask, 0) for mask in sorted(self.__d.keys() | other._Multivector__d.keys())})
   def __radd__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector' : return self+other
   def __sub__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector' : return self+(-other)
   def __rsub__(self,other: _Union[int, float, 'Multivector']) -> 'Multivector': return -self+other
   def __neg__(self) -> 'Multivector' : return Multivector({mask: -val for mask, val in self.__d.items()}, decomposition=self.__decomposition)
   def __invert__(self) -> 'Multivector':
    sigma = self.__get_sigma()
    return Multivector({k: -v if (sigma >> n)&1 else v for n, (k, v) in enumerate(self.__d.items())},decomposition=self.__decomposition)
   def __rmul__(self, other: int | float) -> 'Multivector' : return self*other
   def __pow__(self, other: int | float) -> 'Multivector':
    if not isinstance(other, int | float) : return NotImplemented
    from math import ldexp, copysign
    if len(self.__d) == 0:
     if 1+abs(ldexp(other, -self.algebra.epsilon_order)) == 1 : return self.algebra[0]
     if copysign(1, other) == 1 : return self
     raise ZeroDivisionError(f"Cannot invert {self}: determinant is zero")
    if len(self.__d) == 1 and 0 in self.__d : return self.algebra(self.__d[0]**other)
    if 1 + abs(ldexp(other % 1, -self.algebra.epsilon_order)) != 1: raise ValueError(f'Multivector exponent must be an integer, but got {other}')
    other = int(round(other))
    if other == 0 : return self.algebra[0]
    if other < 0:
     if det := abs(self): out = (~self)/det
     else: raise ZeroDivisionError(f"Cannot invert {self}: determinant is zero")
    else: out = self
    for _ in range(abs(other)-1): out *= self
    return out
   def __abs__(self) -> float:
    if self.__abs is ...: self.__abs = (self*~self)._Multivector__d.get(0, 0)
    return self.__abs
   def __get_sigma(self):
    if self.__sigma is None: raise NoAdjugateError(f'Adjugate undefined for {self}')
    if self.__sigma is not ... : return self.__sigma
    blades = list(self.__d.keys())
    if len(blades) == 0:
     self.__sigma = 0
     return 0
    if added := blades[0] != 0: blades = [0] + blades
    from collections import deque
    n = len(blades)
    epsilon = [[0]*n for _ in range(n)]
    for i in range(n):
     for j in range(n):
      t = (blades[i] & blades[j]).bit_count()
      parity = (blades[i].bit_count()*blades[j].bit_count() - t) & 1
      epsilon[i][j] = -1 if parity else +1
     
    sigma = 0
    known = 1
    queue = deque([0])
    while queue:
     i = queue.popleft()
     si = -1 if (sigma >> i) & 1 else +1
     for j in range(n):
      if i == j: continue
      required_sign = -epsilon[i][j] * si
      required_bit = 1 if required_sign == -1 else 0
      mask = 1 << j
      if not (known & mask):
       if required_bit: sigma |= mask
       else: sigma &= ~mask
       known |= mask
       queue.append(j)
       continue
      current_bit = (sigma >> j) & 1
      if current_bit != required_bit:
       if +(det := self*(Multivector({k: -v if 1 <= k.bit_count()%4 <= 2 else v for k, v in self.__d.items()}))) == 0:
        self.__sigma = sum(1 << n for n, b in enumerate(blades) if 1 <= b.bit_count()%4 <= 2)
        if added: self.__sigma >>= 1
        self.__abs = det._Multivector__d.get(0,0)
        return self.__sigma
       self.__sigma = None
       raise NoAdjugateError(f'Adjugate undefined for {self}')
      
     
    return sigma >> 1 if added else sigma
   def __rpow__(self, other: int | float) -> 'Multivector':
    if not isinstance(other, int | float) : return NotImplemented
    import math
    return (math.log(other)*self).exp()
   def __mulbases(self, mask1, mask2):
    if mask1 == 0 : return mask2, 1
    if mask2 == 0 : return mask1, 1
    if mask1 == mask2:
     init = -1 if mask1.bit_count() % 4 >= 2 else 1
     for n in range(mask1.bit_length()):
      if (mask1 >> n) & 1: init *= self.algebra.signature(n+1)
     return 0, init
    val = 1
    bases = [i for i in range(mask1.bit_length()) if (mask1 >> i) & 1] + [i for i in range(mask2.bit_length()) if (mask2 >> i) & 1]
    seen = set()
    for basis in tuple(bases):
     if basis in seen: continue
     seen.add(basis)
     diff = 0
     keep = False
     for n, factor in enumerate(reversed(tuple(bases))):
      if factor != basis: continue
      keep = not keep
      if keep:
       diff = n
       continue
       
      if n % 2 == diff % 2: val *= -1
      bases.pop(~diff)
      bases.pop(~n+1 if n>diff else ~n)
      val *= self.algebra.signature(basis+1)
      
     
    bases, parity = _merge_sort_parity(bases)
    bases = sum(1 << i for i in bases)
    return bases, val*parity
   def __or__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector':
    if isinstance(other, int | float) : return self*other
    if not isinstance(other, Multivector):
     if isinstance(other, IMultivector): raise GAMismatchError("Cannot combine Multivectors from different GA instances")
     return NotImplemented
    new = {}
    for mask1, val1 in self.__d.items():
     for mask2, val2 in other._Multivector__d.items():
      overlap = mask1&mask2
      if overlap != mask1 and overlap != mask2: continue
      mask, basisprod = self.__mulbases(mask1, mask2)
      new[mask] = new.get(mask, 0) + val1*val2*basisprod
     
    return Multivector(dict(sorted(new.items())))
   def __ror__(self, other: int | float) -> 'Multivector':
    if not isinstance(other, int | float) : return NotImplemented
    return self*other
   def __xor__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector':
    if isinstance(other, int | float) : return self*other
    if not isinstance(other, Multivector):
     if isinstance(other, IMultivector): raise GAMismatchError("Cannot combine Multivectors from different GA instances")
     return NotImplemented
    new = {}
    for mask1, val1 in self.__d.items():
     for mask2, val2 in other._Multivector__d.items():
      if (mask1&mask2) != 0: continue
      mask, basisprod = self.__mulbases(mask1, mask2)
      new[mask] = new.get(mask, 0) + val1*val2*basisprod
     
    return Multivector(dict(sorted(new.items())))
   def __rxor__(self, other: int | float) -> 'Multivector':
    if not isinstance(other, int | float) : return NotImplemented
    return self*other
   def __mul__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector':
    from math import ldexp
    if isinstance(other, int | float) : return Multivector({mask: other*val for mask, val in self.__d.items()},decomposition=self.__decomposition, sigma=self.__sigma)if 1+abs(ldexp(other, -self.algebra.epsilon_order)) != 1else Multivector({})
    elif not isinstance(other, Multivector):
     if isinstance(other, IMultivector): raise GAMismatchError("Cannot combine Multivectors from different GA instances")
     return NotImplemented
    new = {}
    for mask1, val1 in self.__d.items():
     for mask2, val2 in other._Multivector__d.items():
      mask, basisprod = self.__mulbases(mask1, mask2)
      new[mask] = new.get(mask, 0) + val1*val2*basisprod
     
    return Multivector(dict(sorted(new.items())))
   def __matmul__(self, grade: int) -> 'Multivector':
    if not isinstance(grade, int) : return NotImplemented
    return Multivector({mask: val for mask, val in self.__d.items() if mask.bit_count() == grade})
   def __decompose(self):
    if self.__decomposition is not ... : return self.__decomposition
    commutes = lambda mask1,mask2: mask1.bit_count()*mask2.bit_count()%2 == (mask1&mask2).bit_count()%2
    blocks = []
    for mask in self.__d.keys():
     noncom = 0
     noncomindex = None
     for n, block in enumerate(blocks):
      comtrack = None
      for item in block:
       if comtrack is None:
        comtrack = commutes(mask, item)
        continue
       if comtrack is not commutes(mask, item):
        if +(self*self) == 0:
         self.__decomposition = NotImplemented
         return NotImplemented
        self.__decomposition = None
        return None
       
      if comtrack is False:
       noncomindex = n
       noncom+=1
      
     if noncom == 0: blocks.append([mask])
     elif noncom == 1: blocks[noncomindex].append(mask)
     else:
      self.__decomposition = None
      return None
     
    self.__decomposition = blocks
    return blocks
   def exp(self) -> 'Multivector':
    d = self.__decompose()
    if d is None:
     from math import ldexp
     current = self
     cumulus = self.algebra[0] + current
     n = 2
     while True:
      current *= self
      current /= n
      if 1+abs(ldexp(sum(s*s for s in current.__d.values()),-self.algebra.epsilon_order)) == 1: break
      cumulus += current
      n+=1
     return cumulus
    import math
    if d is NotImplemented:
     if (s := (self|self).__d.get(0,0)) != 0: value = math.sqrt(abs(s))
     return self.algebra[0]*math.cosh(value) + self*math.sinh(value)/value if s > 0else self.algebra[0] + self if s == 0else self.algebra[0]*math.cos(value) + self*math.sin(value)/value
    prod = 1.0
    for block in d:
     if block == [0]:
      prod *= math.exp(self.__d[0])
      continue
     total = 0
     for mask in block:
      norm = -1 if mask.bit_count() % 4 >= 2 else 1
      for i in range(mask.bit_length()):
       if (mask >> i) & 1: norm *= self.algebra.signature(i+1)
       
      total += norm * self.__d[mask]**2
     if total != 0: value = math.sqrt(abs(total))
     prod *= Multivector({0: math.cosh(value), **{mask:math.sinh(value)*self.__d[mask]/value for mask in block}})if total > 0else Multivector({0: 1, **{mask: self.__d[mask] for mask in block}})if total == 0else Multivector({0: math.cos(value), **{mask:math.sin(value)*self.__d[mask]/value for mask in block}})
    return prod if isinstance(prod, Multivector) else Multivector({0: prod})
   def __pos__(self) -> int | None:
    grade = None
    for mask in self.__d.keys():
     if grade is None: grade = mask.bit_count()
     elif mask.bit_count() != grade : return None
    return grade
   def __truediv__(self, other: _Union[int, float, 'Multivector']) -> 'Multivector':
    if isinstance(other, int | float) : return Multivector({mask: value/other for mask, value in self.__d.items()},decomposition=self.__decomposition, sigma=self.__sigma)
    if not isinstance(other, Multivector):
     if isinstance(other, IMultivector): raise GAMismatchError("Cannot combine Multivectors from different GA instances")
     return NotImplemented
    return self*(other**(-1))
   def __rtruediv__(self, other: int | float) -> 'Multivector':
    if not isinstance(other, int | float) : return NotImplemented
    return other*(self**(-1))
   def __format__(self, form: str) -> str:
    if form == '': form = 'g'
    return '<'+(''.join(('+' if value > 0 else '')+format(value, form)+''.join('e' + str(i+1).translate(_subscripts) for i in range(mask.bit_length()) if (mask >> i) & 1)for mask, value in self.__d.items()).removeprefix('+')if self.__d else format(0.0,form))+'>'
   def __str__(self) -> str : return f'{self}'
   def __float__(self) -> float:
    if (l := len(self.__d)) == 0 : return 0.0
    elif l == 1 and 0 in self.__d : return self.__d[0]
    raise ValueError(f"Cannot convert to float: Multivector is not a scalar")
   def __int__(self) -> int:
    if (l := len(self.__d)) == 0 : return 0
    elif l == 1 and 0 in self.__d : return int(self.__d[0])
    raise ValueError(f"Cannot convert to int: Multivector is not a scalar")
   def __eq__(self, other: _Union[int, float, 'IMultivector']) -> bool:
    from math import ldexp
    if isinstance(other, int | float):
     if 1+abs(ldexp(other,-self.algebra.epsilon_order)) == 1 : return len(self.__d) == 0
     return len(self.__d) == 1 and 0 in self.__d and 1+abs(ldexp(self.__d[0]-other,-self.algebra.epsilon_order)) == 1
    if not isinstance(other, Multivector):
     if isinstance(other, IMultivector) : return False
     return NotImplemented
    return (keys := self.__d.keys()) == other._Multivector__d.keys() and all(1+abs(ldexp(self.__d[k]-other._Multivector__d[k],-self.algebra.epsilon_order)) == 1for k in keys)
   def __call__(self, factors:_Callable[[int],int|float]):
    if not isinstance(factors, _Callable): raise TypeError(f"Grade-scale factors must be a Callable[[int], int|float], but got {type(factors).__name__}")
    from inspect import signature
    if (l := len(signature(factors).parameters)) != 1: raise TypeError(f"Grade-scale factors must be a Callable[[int], int|float], but got {l} arguments")
    from math import ldexp
    accumulator = {}
    for k, v in self.__d.items():
     grade = k.bit_count()
     if not isinstance((factor := factors(grade)), int | float):raise TypeError(f"Grade-scale factors must be a Callable[[int], int|float], but got {type(factor).__name__} for index {grade}")
     if 1+abs(ldexp(V := v*factor, self.algebra.epsilon_order)) != 0: accumulator[k] = V
    return Multivector(accumulator, decomposition=self.__decomposition)
   def __hash__(self) : return hash(tuple(self.__d.items())) ^ hash(Multivector)
  ga.__Multivector = Multivector
 @_overload
 def __getitem__(self, n: int) -> IMultivector:
  pass
 @_overload
 def __getitem__(self, n: slice) -> _Iterator[IMultivector]:
  pass
 def __getitem__(self, n):
  """
        Get the nth basis vector of the GA if n > 1, the unit scalar if n = 0
        and the zero Multivector if n < 0.
        For slices, return a generator over the slice.
        """
  if isinstance(n, int) : return self.__Multivector({(1<<(n-1) if n > 0 else 0): 1.0} if n >= 0 else {})
  if not isinstance(n, slice): raise TypeError(f"GA indices must be integers or slices, not {type(n).__name__}")
  step = n.step or 1
  start = n.start or 0
  stop = n.stop
  def generator():
   idx = start
   while stop is None or idx < stop:
    yield self[idx]
    idx += step
   
  return generator()
 def __call__(self, other: int | float | IMultivector) -> IMultivector:
  """
        Convert any Multivector, float or int into a Multivector of this GA.
        """
  from math import ldexp
  if isinstance(other, int | float) : return self.__Multivector({}) if 1+abs(ldexp(other, -self.epsilon_order)) == 1 else self.__Multivector({0: float(other)})
  if not isinstance(other, IMultivector): raise TypeError(f"Cannot convert type '{type(other).__name__}' into a Multivector")
  return self.__Multivector(other._Multivector__d,decomposition=other._Multivector__decomposition,sigma=other._Multivector__sigma)
 def __str__(self) -> str : return f"GA<signature={getattr(self.signature, '__name__', repr(self.signature))}, epsilon_order={self.epsilon_order}>"

