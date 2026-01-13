from . import DRAWINGS

def print_drawing(name_of_drawing):
    try:
        print(DRAWINGS[name_of_drawing])
    except KeyError:
        raise KeyError('Error: A drawing with that name was not found! You may need to update the library!')
    
def return_drawing(name_of_drawing):
    try:
        return DRAWINGS[name_of_drawing]
    except KeyError:
        raise KeyError('Error: A drawing with that name was not found! You may need to update the library!')