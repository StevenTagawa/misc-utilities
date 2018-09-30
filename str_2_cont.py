import re
import datetime

def _str_to_container(string):
    """-------------------------------------------------------------
        Method which takes a string literal representation of a list,
         tuple or dictionary and converts it back into that type.
         Converts in place any nested containers within the main
         container.  Converts any string representation of a numeric
         or boolean value, within any container, into the correct type.
        
        Arguments:
        - string -- the string to convert.
        
        Returns:  a list, or the original string if it can't be
         converted.
       -------------------------------------------------------------
    """
    # Error checking / set variables and initialize container.
    if type(string) != str:
        return string
    elif string[0] not in ["(", "[", "{"]:
        return string
    # end if
    open_char = string[0]
    if open_char == "{":
        close_char = "}"
        sep_char = ":"
        container = {}
    elif open_char == "(":
        close_char = ")"
        sep_char = ","
        container = tuple()
    else:
        close_char = "]"
        sep_char = ","
        container = []
    # end if
    if string[-1] != close_char:
        return string
    # end if
    # Empty container check.  If what was passed was a representation of
    #  an empty list/tuple/dictionary, just pass the appropriate empty
    #  container back.
    if string == "[]":
        return []
    elif string == "{}":
        return {}
    elif string == "()":
        return ()
    # Strip out container characters.
    while (string[0] == open_char) and (string[-1] == close_char):
        string = string[1:-1]
    # end while
    # Initialize pointers and flags.
    char = ""
    quote = False
    quote_char = ""
    level = 0
    start = 0
    pos = 0
    if type(container) == dict:
        d_flag = "key"
    # end if
    # Item parsing happens in an endless loop.
    while True:
        # Set start of current item.
        start = pos
        # Check to see if the first character is a quote mark.  If it
        #  is, mark the string as quoted (and advance the character
        #  pointer).
        if string[pos] in ["'", '"']:
            quote_char = string[pos]
            quote = True
            pos += 1
        # end if
        # Loop until hitting the next separator on the top level (or the
        #  end of the string).
        while (pos < len(string) and (
                (level > 0) or (quote) or (char != sep_char))):
            # Read a character.
            char = string[pos]
            # Opening and closing container characters.  The level flag
            #  shows whether the item is a nested container.
            if char in ["(", "[", "{"]:
                level += 1
            elif char in [")", "]", "}"]:
                level -= 1
            # If the character is a matching quote mark, turn off the
            #  quote flag, but only if it's not escaped.
            if (char == quote_char) and (string[pos - 1] != "\\"):
                quote = False
                quote_char = ""
            # end if
            # If we hit the separator on the top level or the end of the
            #  string, do NOT advance the character pointer.  BUT if we
            #  are parsing a quoted string, the separator can only come
            #  after the closing quote mark.
            elif (level == 0) and (not quote) and (char == sep_char):
                continue
            # end if
            pos += 1
            # end if
        # end while
        # Retrieve the complete item.
        item = string[start:pos]
            # Strip quote marks.
        if item[0] in ["'", '"'] and item[-1] == item[0]:
            item = item[1:-1]
        # end if
        # If the item is itself a container, the method calls itself to
        #  convert it.
        if item[0] in ["(", "[", "{"]:
            item = _str_to_container(item)
        # Otherwise, try to convert to a number or boolean value.
        else:
            item = _str_to_datetime(item)
            item = _str_to_num(item)
            item = _str_to_bool(item)
        # end if
        # Add the item to the container.  For a list, just append.
        if type(container) == list:
            container.append(item)
            # Tuples are immutable, so adding an item requires unpacking
            #  and repacking the entire tuple.  We use a temporary list
            #  for this.
        if type(container) == tuple:
            l = []
            for x in container:
                l.append(x)
            # end for
            l.append(item)
            container = tuple(l)
        # Dictionaries are the most complicated, because items are added
        #  in pairs.
        elif type(container) == dict:
            # Check the flag.  It if's set to "key"...
            if d_flag == "key":
                # Store the key.
                key_item = item
                # Change the separator.
                sep_char = ","
                # Flip the flag.
                d_flag = "value"
            # Else, add the key and value to the container.
            else:
                container[key_item] = item
                # Change the separator.
                sep_char = ":"
                # Flip the flag.
                d_flag = "key"
            # end if
        # Advance the pointer past the separator and the space after it.
        pos += 2
        char = ""
        # If we've reached the end of the string, we're done; break the
        #  loop.
        if pos >= len(string):
            break
    # end while
    # All done; return the container.
    return container
# end method

def _str_to_num(string):
    """-------------------------------------------------------------
        Method which takes a string literal representation of a
         number and converts it into a number type.
        
        Arguments:
        - string -- the string to convert.
        
        Returns:  a number type, if applicable; or the original
         string.
       -------------------------------------------------------------
    """
    # Error check.
    if type(string) != str:
        return string
    str_num = string
    # Strip parentheses.
    while str_num[0] == "(" and str_num[-1] == ")":
        str_num = str_num[1:-1]
    # end while
    # Complex number.
    if re.search(r"\d+(\.\d+)?[+-]{1}\d+(\.\d+)?j", str_num):
            return complex(str_num)
    # Floating point number.
    elif re.search(r"\d+\.\d*(e\d*)?", str_num):
        return float(str_num)
    # Integer.
    elif re.fullmatch(r"\d+", str_num):
        return int(str_num)
    else:
        return string
    # end if
# end method

def _str_to_bool(string):
    """-------------------------------------------------------------
        Method which takes a string literal representation of a
         boolean (True/False) and converts it to a bool type.
        
        Arguments:
        - string -- the string to convert.
        
        Returns:  a bool type, if applicable; or the original
         string.
       -------------------------------------------------------------
    """
    # Error check.
    if type(string) != str:
        return string
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        return string
    # end if
# end method
    
def _str_to_datetime(string):
    """-------------------------------------------------------------
        Method which takes a string literal representation of a
         datetime or timedelta object and converts it into the correct
         type.
        
        Arguments:
        - string -- the string to convert.
        
        Returns:  a datetime or timedelta object, if possible, or the
         original string.
       -------------------------------------------------------------
    """
    # First, try to convert to a datetime object.
    try:
        obj = datetime.datetime.fromisoformat(string)
        return obj
    # Drop through if not successful.
    except:
        pass
    # end try
    # Then try a timedelta object.
    match = re.fullmatch(
          r"(?P<days>\d+)?( days, )?(?P<hours>\d{1,2}):(?P<minutes>\d{2})" +
          r":(?P<seconds>\d{2})", string)
    if match:
        # Make sure days isn't None.
        if not match.group("days"):
            d = "0"
        else:
            d = match.group("days")
        # end if
        return datetime.timedelta(
          days=int(d),
          hours=int(match.group("hours")),
          minutes=int(match.group("minutes")),
          seconds=int(match.group("seconds")))
    else:
        return string
    # end if
# end method

s = "['28 days, 17:34:00', [], 'day\"s', 'of', 'our', 'lives', ('NBC', 45), {'running time': '45 minutes', 'channels': [13, 15, 28], 'format': 'soap'}, (5,), '2018-09-28 22:22:43.467435']"

l = _str_to_container(s)

for x in l:
    print(type(x), x)
    if type(x) == dict:
        for key in x:
            print(key, x[key], type(x[key]))
    


