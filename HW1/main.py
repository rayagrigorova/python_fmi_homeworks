def beginning(word):
    end_ind = len(word) // 3

    if len(word) % 3 == 2:  # add extra letter to 'beginning'
        end_ind += 1
    return word[:end_ind]


def middle(word):
    beg_ind = len(word) // 3
    end_ind = beg_ind + len(word) // 3

    if len(word) % 3 == 1:  # extra letter for 'middle'
        end_ind += 1
    elif len(word) % 3 == 2:  # extra letter for 'beginning', so shift 'middle' right
        end_ind += 1
        beg_ind += 1

    return word[beg_ind:end_ind]


def end(word):
    beg_ind = (len(word) // 3) * 2

    # extra letter in 'beginning' or 'middle', so shift 'end' right
    if len(word) % 3 == 1 or len(word) % 3 == 2:
        beg_ind += 1

    return word[beg_ind:]


def split_sentence(sentence):
    words = sentence.split()
    tuples = []
    for word in words:
        elem = (beginning(word), middle(word), end(word))
        tuples.append(elem)
    return tuples
