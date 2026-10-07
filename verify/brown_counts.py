"""Independent check of Brown's triangulation counts against the bundle's table.

Brown (1964): the number of triangulations of a disk with m+3 labelled boundary
vertices and n unlabelled interior vertices is
    R_{n,m} = 2 (2m+3)! (4n+2m+1)! / ((m+2)! m! n! (3n+2m+3)!) .
Multiplying by n! gives the number of fully labelled triangulations.
"""
from math import factorial

TABLE = {(9, 1): 5005, (9, 2): 90090, (9, 3): 2252250,
         (10, 1): 19448, (10, 2): 388960, (11, 1): 75582}
ORBITS = {(9, 1): 291, (9, 2): 2548, (9, 3): 21018,
          (10, 1): 1004, (10, 2): 9876, (11, 1): 3471}

ok = True
for (B, I), want in sorted(TABLE.items()):
    m = B - 3
    R = 2 * factorial(2 * m + 3) * factorial(4 * I + 2 * m + 1) // \
        (factorial(m + 2) * factorial(m) * factorial(I) * factorial(3 * I + 2 * m + 3))
    labeled = R * factorial(I)
    good = (labeled == want)
    ok &= good
    print(f'(B,I)=({B},{I}): Brown={labeled:>9d}  bundle={want:>9d}  '
          f'orbits={ORBITS[(B,I)]:>6d}  {"OK" if good else "MISMATCH"}')
print('total labelled:', sum(TABLE.values()), ' total orbits:', sum(ORBITS.values()))
print('ALL OK' if ok else 'MISMATCH')
