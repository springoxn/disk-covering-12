import sympy as sp

r, u, v, w, c, s, z = sp.symbols('r u v w c s z')
E2 = u ** 2 - 2 * u * c + 1 - r ** 2
E3 = v ** 2 - v * (c ** 2 - s ** 2 + 2 * z * c * s) + 1 - r ** 2
E4 = w - u ** 2 + r ** 2 + r
E5 = v ** 2 - (2 * r + w) * v + w * (w + r)
F1 = c ** 2 + s ** 2 - 1


def R120(p):
    return (sp.expand(-(p[0] + z * p[1]) / 2), sp.expand((z * p[0] - p[1]) / 2))


def R240(p):
    return (sp.expand(-(p[0] - z * p[1]) / 2), sp.expand(-(z * p[0] + p[1]) / 2))


def refl60(p):
    return (sp.expand((-p[0] + z * p[1]) / 2), sp.expand((z * p[0] + p[1]) / 2))


gp = (u * c, u * s)
gm = (u * c, -u * s)
rawC = [gp, gm, R120(gp), R120(gm), R240(gp), R240(gm),
        (-v, sp.Integer(0)), R120((-v, sp.Integer(0))), R240((-v, sp.Integer(0))),
        (w, sp.Integer(0)), R120((w, sp.Integer(0))), R240((w, sp.Integer(0)))]
CS = [rawC[i] for i in [6, 5, 4, 7, 1, 0, 8, 3, 2, 9, 10, 11]]
q0 = (sp.Integer(1), sp.Integer(0))
q1 = (c ** 2 - s ** 2, 2 * c * s)
q2 = refl60(q1)
rawQ = [q0, q1, q2, R120(q0), R120(q1), R120(q2), R240(q0), R240(q1), R240(q2)]
QS = [rawQ[i] for i in [5, 6, 7, 8, 0, 1, 2, 3, 4]]


def red_simple(e):
    e = sp.expand(e)
    e = sp.expand(e.subs(s ** 2, 1 - c ** 2))
    e = sp.expand(e.subs(z ** 2, 3))
    return sp.expand(e)


def dist2(A, B):
    return sp.expand((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)


for i in range(9):
    for tag, j in (('self', i), ('next', (i + 1) % 9)):
        d = sp.expand(dist2(QS[i], CS[j]) - r ** 2)
        # try direct reduction by F1, Z3 then E2 or E3
        d1 = red_simple(d)
        # collect in u,v
        pu = sp.Poly(d1, u)
        if pu.degree() >= 2:
            d1 = sp.expand(sp.rem(pu, sp.Poly(u ** 2 - 2 * u * c + 1 - r ** 2, u), u).as_expr())
        d1 = red_simple(d1)
        pv = sp.Poly(d1, v)
        rest = None
        if pv.degree() >= 2:
            rem3 = sp.expand(sp.rem(pv, sp.Poly(E3, v), v).as_expr())
            rem5 = sp.expand(sp.rem(pv, sp.Poly(E5, v), v).as_expr())
        else:
            rem3 = rem5 = d1
        rem3 = red_simple(rem3)
        rem5 = red_simple(rem5)
        if rem3 == 0 or rem5 == 0:
            print(f'{i:2d} {tag:4s} -> {["e3 ok",""][0] if rem3==0 else ""}{" e5 ok" if rem5==0 else ""}')
        else:
            print(f'{i:2d} {tag:4s} NOT ZERO   e3-rem ops {sp.count_ops(rem3)}  e5-rem ops {sp.count_ops(rem5)}')
            print('     e3 rem =', sp.factor(rem3))
            print('     e5 rem =', sp.factor(rem5))
