# Being built...
# Slightly better correcting
# Rather than just finding letter similarities, it looks for substring similarities
def advancedGuessing(list_of_people, name):
    confidence = {prof : 0 for prof in list_of_people}

    # Find common substrings
    for prof in list_of_people:
        name_iterator = iter(name)
        last_position = 0
        on_a_roll = False
        # Iterate until the iterator has no next() value
        while 1:
            # Find any substrings in name that're in prof as well
            try:
                on_a_roll = False
                letter = next(name_iterator)
                while letter in prof:
                    confidence[prof] += on_a_roll
                    on_a_roll = True
                    letter += next(name_iterator)
            except:
                break
        # Greater size difference, less confident
        confidence[prof] -= abs(len(name) - len(prof)) * 0.1

    # Initial confidence rating is done
    # Now, enhance confidence level based on size, letters given (not in substring), etc.

    return max(confidence,key=confidence.get)
