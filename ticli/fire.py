# Copyright (C) 2021 NTA, Inc.

"""
Wrapper for the Python Fire package.
"""

try:
    from fire import decorators
    from fire import Fire
    
# Try to make due without fire package being installed
except:
    def dummy(*args, **kw):
        pass

    class Dummy:
        pass
    
    Fire = dummy
    decorators = Dummy
    decorators._SetMetadata = dummy
    decorators.FIRE_DEFAULTS_DICT = "FIRE_DEFAULTS_DICT"
    decorators.FIRE_STAND_IN = "FIRE_STAND_IN"

_Fire = Fire
def Fire(*args, **kw):
    # Work-around to keep fire from using "less" to show help output
    import os
    os.environ["PAGER"] = "cat"
    
    # Provide exception handling for validation errors
    import ticli.validation as v
    try:
        _Fire(*args, **kw)
    except v.ValidationError as exc:
        v.print_validation_error(exc)
