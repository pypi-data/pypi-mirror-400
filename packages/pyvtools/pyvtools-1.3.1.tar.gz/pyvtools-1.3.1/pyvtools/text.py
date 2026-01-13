from re import findall

#%% SINGLE STRING

def find_numbers(string):
    """Returns a list of numbers (int or float) found on a given string"""
    
    numbers = findall(r"[-+]?\d*\.\d+|[-+]?\d+", string)
    
    if not numbers:
        raise TypeError("There's no number in this string")
    
    for i, n in enumerate(numbers):
        if '.' in n:
            numbers[i] = float(n)
        else:
            numbers[i] = int(n) 
    
    return numbers

def change_separator(string, current_separator, new_separator):
    return new_separator.join(string.split(current_separator))

def break_into_lines(string):
    return change_separator(string, " ", "\n")

#%% LIST OF STRINGS

def filter_by_string_must(string_list, string_must, must=True, start_on=False, end_on=False):
    """Filters list of str by a str required to be always present or absent.
    
    Parameters
    ----------
    string_list : list of str
        The list of strings to filter.
    string_must : str
        The string, or list of strings, that must always be present or 
        always absent on each of the list elements.
    must=True : bool
        If true, then the string must always be present. If not, the string 
        must always be absent.
    
    Returns
    -------
    filtered_string_list: list of str
        The filtered list of strings.
    """
    
    if not isinstance(string_must, list):
        string_must = [string_must]

    if start_on and not end_on:
        check = lambda s, smust : s[:len(smust)] == smust
    elif end_on and not start_on:
        check = lambda s, smust : s[-len(smust):] == smust
    elif start_on and end_on:
        check = lambda s, smust : smust == s
    else:
        check = lambda s, smust : smust in s

    filtered_string_list = []
    for s in string_list:
        do_append = True
        for smust in string_must:
            if must and not check(s, smust):
                do_append = False
                break
            elif not must and check(s, smust):
                do_append = False
                break
        if do_append:
            filtered_string_list.append(s)
            
    return filtered_string_list