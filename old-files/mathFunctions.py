import math

# give examples of these
def surfaceAreaOfCuboid(width, height, depth):
    return width*height*depth

def factorial(n):
    if (n==0 or n==1):
        return 1
    else:
        return n * factorial(n-1)

# test on these
def fib(n):
    if (n == 0 or n == 1):
        return 1
    else:
        return fib(n-1)+fib(n-2)


def sumTo(n):
    if (n==0):
        return 0;
    else:
        return n+sumTo(n-1)

def square(n):
    return n*n


def sumOfSquaresTo(n):
    if (n==0):
        return 0;
    else:
        return square(n) + sumOfSquaresTo(n-1)


def pythag(a,b):
    return math.sqrt(square(a)+square(b))


def areaOfCircle(r):
    return math.pi * square(r)


def volumeOfCylinder(radius, height):
    return math.pi * square(radius)*height


def triangle(n):
    sum = 0
    for count in range(0,n):
        sum += count
    return sum

# we have assumed here that the discriminant is positive - ie it has real solutions
def quadraticFormulaPositve(a,b,c):
    discriminant = square(b)-4*a*c
    return (-b + math.sqrt(discriminant))/(2*a)




# give them the mathamatical formula and ask them to give function for:
    # volume cone
    # volume pyramid
    # surface area of a cuboid
    # surface area of