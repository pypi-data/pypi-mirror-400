from k3math import Polynomial

xs = [1, 2, 3, 4]
ys = [6, 5, 7, 10]

# Fit polynomial curve with 4 points, at degree 0, 1, 2, 3:
for deg in (0, 1, 2, 3):
    poly = Polynomial.fit(xs, ys, degree=deg)
    print("y =", poly)

    # Evaluate y(5) with polynomial
    y5 = Polynomial.evaluate(poly, 5)
    print("y(5) =", y5)

    # Plot the curve and points
    lines = Polynomial.plot(
        [(poly, ".")], (-1, 6), width=30, height=10, points=list(zip(xs + [5], ys + [y5], ["X", "X", "X", "X", "*"]))
    )
    for line in lines:
        print(line)

# y = 7
# y(5) = 7.0
#                     X
#
#
#
# ...............X.........*....
#      X
#           X
# y = 3.5 + 1.4x
# y(5) = 10.5
#                              .
#                          *...
#                     X....
#                .....
#           .....X
#      X....X
# .....
# y = 8.5 - 3.6x + x²
# y(5) = 15.5
#                              .
#                             .
#                           ..
#                         .*
#                      ...
# ..               ...X
#   ...X....X....X.
# y = 12 - 9.166667x + 3.5x² - 0.333333x³
# y(5) = 12.0
#
# .                     ...*....
#  .                  X.
#   .               ..
#    .            ..
#     .         .X
#      X....X...
