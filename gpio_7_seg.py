all_seg_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

seg_to_pin = {
    'a': 15,
    'b': 16,
    'c': 17,
    'd': 18,
    'e': 19,
    'f': 20,
    'g': 21,
    'dp': 22
    }

char_to_seg_list = {
    '0': ['a', 'b', 'c', 'd', 'e', 'f'],
    '1': ['b', 'c'],
    '2': ['a', 'b', 'd', 'e', 'g'],
    '3': ['a', 'b', 'c', 'd', 'g'],
    '4': ['b', 'c', 'f', 'g'],
    '5': ['a', 'c', 'd', 'f', 'g'],
    '6': ['a', 'c', 'd', 'e', 'f', 'g'],
    '7': ['a', 'b', 'c'],
    '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    '9': ['a', 'b', 'c', 'd', 'f', 'g'],
    'a': ['a', 'b', 'c', 'e', 'f', 'g'],
    'b': ['c', 'd', 'e', 'f', 'g'],
    'c': ['a', 'd', 'e', 'f'],
    'd': ['b', 'c', 'd', 'e', 'g'],
    'e': ['a', 'd', 'e', 'f', 'g'],
    'f': ['a', 'e', 'f', 'g'],
    'g': ['a', 'c', 'd', 'e', 'f'],
    'h': ['b', 'c', 'e', 'f', 'g'],
    'i': ['c'],
    'j': ['b', 'c', 'd'],
    'k': ['b', 'd', 'e', 'f', 'g'],
    'l': ['d', 'e', 'f'],
    'm': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    'n': ['c', 'e', 'g'],
    'o': ['c', 'd', 'e', 'g'],
    'p': ['a', 'b', 'e', 'f', 'g'],
    'q': ['a', 'b', 'c', 'f', 'g'],
    'r': ['e', 'g'],
    's': ['a', 'c', 'd', 'f', 'g'],
    't': ['d', 'e', 'f', 'g'],
    'u': ['b', 'c', 'd', 'e', 'f'],
    'v': ['b', 'c', 'd', 'e'],
    'w': ['b', 'c', 'd', 'e', 'f', 'g'],
    'x': ['b', 'c', 'e', 'f', 'g'],
    'y': ['b', 'c', 'd', 'f', 'g'],
    'z': ['a', 'b', 'd', 'e', 'g']
    }
    
def show_disp(char):
    # make sure c is a string
    char = str(char)
    # check if trying to display multiple characters with this function
    if len(char) > 1:
        print('Impossible to display ' + char + ': display one character at a time.')
        return
    # check if we know how to represent the character
    if char not in char_to_seg_list:
        print('Do not know how to represent character ' + char)
        return
    # represent character on display
    for seg in all_seg_list:
        if seg in char_to_seg_list[char]:
            gpio_write(seg_to_pin[seg], 1)
        else:
            gpio_write(seg_to_pin[seg], 0)

def gpio_read(pin):
    print('TODO')
    
def gpio_write(pin, val):
    print('TODO')            
    