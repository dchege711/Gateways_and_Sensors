'''
Stores various LED patterns.

@ Original Author   : Chege Gitau

'''

#_______________________________________________________________________________

# Set up helper variables for the colors
ledColors = {
    'black'   : (  0,   0,   0),
    'red'     : (255,   0,   0),
    'green'   : (  0, 255,   0),
    'blue'    : (  0,   0, 255),
    'orange'  : (255, 165,   0),
    'magenta' : (255,   0, 255)
}

O = ledColors['black']

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

def threeDots(color, sOrG):
    X = ledColors[color]

    if sOrG == 'S':
        S = X
        G = O
    elif sOrG == 'G':
        S = O
        G = X
    else:
        S = ledColors['red']
        G = ledColors['red']

    figure = [
        X, X, O, X, X, O, X, X,
        X, X, O, X, X, O, X, X
        O, O, O, O, O, O, O, O,
        O, O, X, X, X, X, O, O,
        O, O, X, O, O, O, O, O,
        O, O, X, S, X, X, G, O,
        O, O, G, O, O, X, O, O,
        O, O, X, X, X, X, O, O
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

def arrowSend(colorArrow, colorDot):
    X = ledColors[colorArrow]
    Y = ledColors[colorDot]
    figure = [
        Y, O, O, X, X, O, O, Y,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        X, X, X, X, X, X, X, X,
        O, X, X, X, X, X, X, O,
        O, O, X, X, X, X, O, O,
        Y, O, O, X, X, O, O, Y
    ]
    return figure

#_______________________________________________________________________________

def arrowReceive(colorArrow, colorDot):
    X = ledColors[colorArrow]
    Y = ledColors[colorDot]
    figure = [
        Y, O, O, X, X, O, O, Y,
        O, O, X, X, X, X, O, O,
        O, X, X, X, X, X, X, O,
        X, X, X, X, X, X, X, X,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        O, O, O, X, X, O, O, O,
        Y, O, O, X, X, O, O, Y
    ]
    return figure

#_______________________________________________________________________________

# def arrow(colorArrow):
#     X = ledColors[colorArrow]
#     figure = [
#         O, O, O, X, X, O, O, O,
#         O, O, O, X, X, O, O, O,
#         O, O, O, X, X, O, O, O,
#         O, O, O, X, X, O, O, O,
#         X, X, X, X, X, X, X, X,
#         O, X, X, X, X, X, X, O,
#         O, O, X, X, X, X, O, O,
#         O, O, O, X, X, O, O, O
#     ]
#     return figure

#_______________________________________________________________________________
