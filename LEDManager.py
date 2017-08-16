'''
Stores various LED patterns.

@ Original Author   : Chege Gitau

'''

#_______________________________________________________________________________

# Set up helper variables for the colors
ledColors = {
    'black'   = (  0,   0,   0)
    'red'     = (255,   0,   0)
    'green'   = (  0, 255,   0)
    'blue'    = (  0,   0, 255)
    'orange'  = (255, 165,   0)
    'magenta' = (255,   0, 255)
}

#_______________________________________________________________________________

def diamond(color):
    X = ledColors[color]
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
    return diamond

#_______________________________________________________________________________

def xCross(color):
    X = ledColors[color]
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
    return xCross

#_______________________________________________________________________________

def arrow(color):
    X = ledColors[color]
    arrow = [
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        X, X, X, X, X, X, X, X,
        O, X, X, X, X, X, X, O,
        O, O, X, X, X, X, O, O,
        O, O, O, X, X, O, O, O
    ]
    return arrow

#_______________________________________________________________________________
