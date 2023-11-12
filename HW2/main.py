def plugboard(to_convert, list_of_letter_pairs):
    """Convert a given string using sets of two letters. Each letter converts to its neighbor."""
    converted = ''
    for ch in to_convert:
        # create a list of all sets that contain the current letter
        corresponding_set = [letters_set for letters_set in list_of_letter_pairs if ch in letters_set]

        # if the list is empty or the current character
        # isn't a letter, then the character will not be changed
        if not corresponding_set or not ch.isalpha():
            converted += ch
        else:
            # get difference between the set {'ch', 'other_letter'} and {ch} to find 'other_letter'
            # (next() and iter() are used to extract the single member of the set)
            converted += next(iter(corresponding_set[0] - {ch}))
    return converted


def rotor(to_convert, dict_letters):
    converted = ''
    for ch in to_convert:
        if not ch.isalpha():  # only convert letters
            converted += ch
            continue
        converted += dict_letters[ch]
    return converted


def enigma_encrypt(plugboard_position=[], rotor_position={}):
    def decorator(func):
        def inner(to_encrypt):
            after_plugboard = plugboard(to_encrypt, plugboard_position)
            after_rotor = rotor(after_plugboard, rotor_position)
            func(after_rotor)
        return inner
    return decorator


def enigma_decrypt(plugboard_position=[], rotor_position={}):
    def decorator(func):
        def inner(to_decrypt):
            rotor_reversed = {v: k for k, v in rotor_position.items()}
            after_rotor = rotor(to_decrypt, rotor_reversed)
            after_plugboard = plugboard(after_rotor, plugboard_position)
            func(after_plugboard)
        return inner
    return decorator
