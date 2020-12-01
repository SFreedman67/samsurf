from sage.all import *

from collections import deque
from itertools import product
from enum import Enum

from bowman.triangulation import Triangulation, Triangle

Angles = Enum('Angles', 'acute right obtuse')
Sides = Enum('Sides', 'equilateral isosceles scalene')


def get_angles_from_parameters(a, b, c):
    if not (0 < a <= b <= c):
        raise ValueError("Parameters must be non-zero and non-decreasing")
    elif gcd(gcd(a, b), c) != 1:
        raise ValueError("Parameters must be coprime")
    d = a + b + c
    return QQ(a / d) * pi, QQ(b / d) * pi, QQ(c / d) * pi


def get_triangle_from_parameters(a, b, c):
    return get_triangle_from_angles(*get_angles_from_parameters(a, b, c))


def get_triangle_from_angles(alpha, beta, gamma):
    a, b, c = get_side_lengths_from_angles(alpha, beta, gamma)

    x = (a ** 2 - b ** 2 + c ** 2) / (2 * a)
    y = sqrt(c ** 2 - x ** 2)

    return Triangle(sage.all.vector([a, 0]),
                    sage.all.vector([x - a, y]),
                    sage.all.vector([-x, -y]))


def get_side_lengths_from_angles(alpha, beta, gamma):
    sines = [sin(alpha), sin(beta), sin(gamma)]
    _, (a, b, c), phi = number_field_elements_from_algebraics(sines,
                                                              minimal=True)
    return phi(a), phi(b), phi(c)


def matrix_reflection(v):
    v_perp = sage.all.matrix([[0, -1], [1, 0]]) * v
    # COB from E (Standard basis) to B := (v, v_perp)
    change_basis = sage.all.matrix([v, v_perp]).transpose()
    return change_basis * sage.all.matrix([[1, 0], [0, -1]]) * change_basis ** (-1)


def build_unfolding(t0):
    tris_to_visit = deque([(t0, 0)])
    group_elements = [sage.all.identity_matrix(2)]

    triangles = [t0]
    gluings = {}

    while tris_to_visit:
        tri_curr, tri_lab = tris_to_visit.pop()
        tri_elt = group_elements[tri_lab]
        for edge_lab in [x for x in range(3) if (tri_lab, x) not in gluings]:
            h = matrix_reflection(tri_curr[edge_lab])
            tri_reflection = tri_curr.reflect(edge_lab)
            reflection_elt = h * tri_elt

            if reflection_elt in group_elements:
                tri_prev_lab = group_elements.index(reflection_elt)
                tri_prev = triangles[tri_prev_lab]
                for idx, edge_prev in enumerate(tri_prev):
                    if edge_prev == -tri_curr[edge_lab]:
                        edge_lab_prev = idx
                gluings[(tri_lab, edge_lab)] = (tri_prev_lab, edge_lab_prev)

            else:
                reflection_lab = len(triangles)
                triangles.append(tri_reflection)
                group_elements.append(reflection_elt)
                gluings[(tri_lab, edge_lab)] = (reflection_lab, edge_lab)
                tris_to_visit.appendleft((tri_reflection, reflection_lab))

        gluings.update({val: key for key, val in gluings.items()})

    return Triangulation(triangles, gluings)


def get_triangle_type_angles(angles):
    if all(QQ(x / pi) < QQ(1 / 2) for x in angles):
        return Angles.acute
    elif any(QQ(x / pi) == QQ(1 / 2) for x in angles):
        return Angles.right
    else:
        return Angles.obtuse


def get_triangle_type_sides(angles):
    alpha, beta, gamma = angles
    if alpha == beta == gamma:
        return Sides.equilateral
    elif alpha == beta or beta == gamma:
        return Sides.isosceles
    else:
        return Sides.scalene


if __name__ == "__main__":
    X = build_unfolding(get_triangle_from_parameters(1, 1, 3))
    while X.idr.is_trivial:
        X = X.change_delaunay_triangulation()

    print(X.generators_veech)
