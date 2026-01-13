from typing import List, Dict, Any

def split_list(datas: List[Any], length_each: int) -> List[List[Any]]:
    """
    Splits a list into sublists of specified length.
    
    Takes a list and divides it into multiple sublists where each sublist
    (except possibly the last one) has the specified length.
    
    Args:
        datas (List[Any]): The input list to be split
        length_each (int): The maximum length of each sublist
    
    Returns:
        List[List[Any]]: A list containing the sublists
        
    Examples:
        >>> split_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    results: List[Any] = []
    for i in range(0, len(datas), length_each):
        results.append(datas[i:i+length_each])
    return results

def to_float(text: str) -> float | str:
    """
    Safely converts a string to float.
    
    Attempts to convert a string to float. Returns the original string
    if conversion fails.
    
    Args:
        text (str): The string to convert
    
    Returns:
        float | str: The converted float or original string if conversion fails
        
    Examples:
        >>> to_float("3.14")
        3.14
        >>> to_float("abc")
        "abc"
    """
    try:
        return float(text)
    except Exception:
        return text

def to_int(text: str) -> int | str:
    """
    Safely converts a string to integer.
    
    Attempts to convert a string to integer. Returns the original string
    if conversion fails.
    
    Args:
        text (str): The string to convert
    
    Returns:
        int | str: The converted integer or original string if conversion fails
        
    Examples:
        >>> to_int("42")
        42
        >>> to_int("4.2")
        "4.2"
    """
    try:
        return int(text)
    except Exception:
        return text

def val(text: Any) -> Any:
    """
    Returns the input value if truthy, otherwise returns None.
    
    A helper function that returns None for falsy values (empty strings,
    empty lists, etc.) and the original value for truthy values.
    
    Args:
        text (Any): The value to evaluate
    
    Returns:
        Any: The original value if truthy, None otherwise
        
    Examples:
        >>> val("text")
        "text"
        >>> val("")
        None
    """
    if text: return text
    else: return None

def vlist_dict(data_list: List[Dict], key: str) -> List[Dict]:
    """
    Removes duplicate dictionaries from a list based on a key.
    
    Takes a list of dictionaries and returns a new list without duplicates,
    where uniqueness is determined by the specified key.
    
    Args:
        data_list (List[Dict]): List of dictionaries to process
        key (str): Dictionary key to check for duplicates
    
    Returns:
        List[Dict]: List with duplicate dictionaries removed
        
    Examples:
        >>> data = [{'id': 1, 'name': 'A'}, {'id': 1, 'name': 'B'}]
        >>> vlist_dict(data, 'id')
        [{'id': 1, 'name': 'A'}]
    """
    seen = set()
    result = []
    for d in data_list:
        if d[key] not in seen:
            seen.add(d[key])
            result.append(d)
    return result

def search_key_v2(data: Dict[str, Any], key: str, required_key: str = None) -> Any:
    """
    Recursively searches for a key in nested dictionaries (enhanced version).
    
    Searches through nested dictionaries to find a specified key. Can optionally
    return a value from a sub-dictionary if the key is found.
    
    Args:
        data (Dict[str, Any]): The dictionary to search
        key (str): The key to search for
        required_key (str, optional): If provided and key is found,
            returns data[key][required_key] if exists
    
    Returns:
        Any: The found value or None if not found
        
    Examples:
        >>> data = {'a': {'b': {'c': 1}}}
        >>> search_key_v2(data, 'b')
        {'c': 1}
        >>> search_key_v2(data, 'b', 'c')
        1
    """
    if key in data:
        if isinstance(data[key], dict):
            if required_key is None:
                return data[key]
            elif required_key in data[key]:
                return data[key][required_key]
        else:
            return None

    for k, v in data.items():
        if isinstance(v, dict):
            result = search_key_v2(v, key, required_key)
            if result is not None:
                return result
    return None

def search_key(data: Dict[str, Any], key: str) -> Any:
    """
    Recursively searches for a key in nested dictionaries.
    
    Searches through nested dictionaries to find a specified key.
    Returns the first occurrence found in a depth-first search.
    
    Args:
        data (Dict[str, Any]): The dictionary to search
        key (str): The key to search for
    
    Returns:
        Any: The found value or None if not found
        
    Examples:
        >>> data = {'a': 1, 'b': {'c': 2}}
        >>> search_key(data, 'c')
        2
    """
    if not isinstance(data, dict):
        return None
    if key in data:
        return data[key]
    for value in data.values():
        if isinstance(value, dict):
            result = search_key(value, key)
            if result is not None:
                return result
    return None