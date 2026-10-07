"""Validate the mpmath PSLQ setup on a known algebraic number (sqrt2+sqrt3)."""
import mpmath as mp

mp.mp.dps = 600
q = mp.sqrt(2) + mp.sqrt(3)          # minimal polynomial x^4 - 10x^2 + 1
for deg, mc, tol in ((4, 10 ** 15, 520), (4, 10 ** 6, 520), (4, 10 ** 15, 100),
                     (37, 10 ** 15, 520)):
    x = [mp.mpf(1)] + [q ** k for k in range(1, deg + 1)]
    rel = mp.pslq(x, tol=mp.mpf(10) ** (-tol), maxcoeff=mc, maxsteps=30000)
    print(f'deg {deg} maxcoeff 1e{len(str(mc))-1} tol 1e-{tol} -> {rel}')
