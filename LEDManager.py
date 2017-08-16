'''
Stores various LED patterns.

@ Original Author   : Chege Gitau

'''

#_______________________________________________________________________________

# Set up helper variables for the colors
ledColors = {
    'black'   : (  0,   0,   0)
    'red'     : (255,   0,   0)
    'green'   : (  0, 255,   0)
    'blue'    : (  0,   0, 255)
    'orange'  : (255, 165,   0)
    'magenta' : (255,   0, 255)
}

#_______________________________________________________________________________

def pluses(color):
    X = ledColors[color]
    figure = [
        O, X, O, O, O, O, X, O,
        X, X, X, O, O, X, X, X,
        O, X, O, O, O, O, X, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, X, O, O, O, O, X, O,
        X, X, X, O, O, X, X, X,
        O, X, O, O, O, O, X, O
    ]
    return figure

#_______________________________________________________________________________

def threeDots(color):
    X = ledColors[color]
    figure = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        X, X, O, X, X, O, X, X,
        X, X, O, X, X, O, X, X,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O
    ]
    return figure

#_______________________________________________________________________________

def diamond(color):
    X = ledColors[color]
    figure = [
        O, O, O, X, X, O, O, O,
        O, O, X, O, O, X, O, O,
        O, X, O, O, O, O, X, O,
        X, O, O, O, O, O, O, X,
        X, O, O, O, O, O, O, X,
        O, X, O, O, O, O, X, O,
        O, O, X, O, O, X, O, O,
        O, O, O, X, X, O, O, O
    ]
    return figure

#_______________________________________________________________________________

def xCross(color):
    X = ledColors[color]
    figure = [
        X, O, O, O, O, O, O, X,
        O, X, O, O, O, O, X, O,
        O, O, X, O, O, X, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, X, O, O, X, O, O,
        O, X, O, O, O, O, X, O,
        X, O, O, O, O, O, O, X
    ]
    return figure

#_______________________________________________________________________________

def arrow(color):
    X = ledColors[color]
    figure = [
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        X, X, X, X, X, X, X, X,
        O, X, X, X, X, X, X, O,
        O, O, X, X, X, X, O, O,
        O, O, O, X, X, O, O, O
    ]
    return figure

#_______________________________________________________________________________
