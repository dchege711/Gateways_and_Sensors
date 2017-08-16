'''
Stores various LED patterns.

@ Original Author   : Chege Gitau

'''

#_______________________________________________________________________________

# Set up helper variables for the colors
black   = (  0,   0,   0)
red     = (255,   0,   0)
green   = (  0, 255,   0)
blue    = (  0,   0, 255)
orange  = (255, 165,   0)
magenta = (255,   0, 255)

O = black

X = green
diamond = [
    O, O, O, X, X, O, O, O,
    O, O, X, O, O, X, O, O,
    O, X, O, O, O, O, X, O,
    X, O, O, O, O, O, O, X,
    X, O, O, O, O, O, O, X,
    O, X, O, O, O, O, X, O,
    O, O, X, O, O, X, O, O,
    O, O, O, X, X, O, O, O
]

X = red
xCross = [
    X, O, O, O, O, O, O, X,
    O, X, O, O, O, O, X, O,
    O, O, X, O, O, X, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, X, O, O, X, O, O,
    O, X, O, O, O, O, X, O,
    X, O, O, O, O, O, O, X
]

X = blue
arrow = [
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    X, O, O, X, X, O, O, X,
    O, X, O, X, X, O, X, O,
    O, O, X, X, X, X, O, O,
    O, O, O, X, X, O, O, O
]

X = orange
orangeArrow = [
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    X, O, O, X, X, O, O, X,
    O, X, O, X, X, O, X, O,
    O, O, X, X, X, X, O, O,
    O, O, O, X, X, O, O, O
]
