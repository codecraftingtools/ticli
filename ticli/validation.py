# Copyright (C) 2021 NTA, Inc.

import sys
from pydantic import create_model as _create_model

# Pull these symbols into the module namespace for use by others
from pydantic import validate_arguments, ValidationError

# Name and signature inspired by the Typeguard package
def check_type(arg_name, value, type_annotation):
    default_value = None # does not matter
    M = _create_model(
        "Temp_Model",
        **{arg_name: (type_annotation, default_value)})
    M(**{arg_name: value})

# Print ValidationError information from the pydantic package
def print_validation_error(exc, value=None, value_dict=None,
                           arg_names=None, arg_values=None):
    already_printed = []
    for error in exc.errors():
        
        # Construct the argument name from the exception data
        error_loc = str(error['loc'][0])
        for e in error['loc'][1:]:
            e = str(e)
            if e.isnumeric():
                error_loc += f" {e}"
            else:
                error_loc += f" -> {e}"
        name = str(error_loc)

        # Construct a dictionary with key=arg_name, value=supplied_arg_value
        d = {}
        
        # Add supplied keyword arguments
        if value_dict:
            d.update(value_dict)
        # Add supplied positional arguments
        if arg_names and arg_values:
            positional_pairs = zip(
                arg_names, arg_values)
            for k, v in positional_pairs:
                d[k] = v
        # Try to look up a value for the argument with the error
        value_str = ""
        if d:
            for n, v in d.items():
                if n == name:
                    value_str = str(d[name])
        # Use the caller-supplied value, if given
        if value:
            value_str = str(value)

        # Print and format the error message
        if value_str:
            value_str = f"'{value_str}' "
        m = f"{sys.argv[0]}: error: invalid value " + value_str + \
            f"supplied for argument '{error_loc}': {error['msg']}"
        if not m in already_printed:
            print(m)
            already_printed.append(m)
