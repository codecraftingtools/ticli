# Copyright (C) 2021 NTA, Inc.

import inspect
from makefun import with_signature
from decopatch import class_decorator, DECORATED

try:
    import fire.decorators
    _fire_package_present = True
except:
    _fire_package_present = False

@class_decorator
def group(C=DECORATED):

    # Retrieve option names and types from class annotations
    option_types = C.__dict__.get('__annotations__', {})
    option_names = list(option_types.keys())

    # Remove class attributes for options with default values and capture the
    # default values
    option_values = {}
    for opt_name in option_names:
        if hasattr(C, opt_name):
            opt_value = getattr(C, opt_name)
            option_values[opt_name] = opt_value
            delattr(C, opt_name)

    # Construct a function signature that accepts the options as arguments
    def ref_fun(self):
        pass
    ref_sig = inspect.signature(ref_fun)
    option_params = []
    for n in option_names:
        p = inspect.Parameter(
            name=n,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=option_values.get(n,inspect.Parameter.empty),
            annotation=option_types[n])
        option_params.append(p)
    self_param = list(ref_sig.parameters.values())[0]
    option_params_with_self = [self_param] + option_params
    options_sig = ref_sig.replace(parameters=option_params_with_self)

    # Construct an __init__() signature that includes options
    def _construct_init_sig(__post_init__):
        post_init_sig = inspect.signature(__post_init__)
        post_init_params = list(post_init_sig.parameters.values())
        leading_init_params = list(post_init_params)
        trailing_init_params = []
        for p in reversed(post_init_params):
            if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.KEYWORD_ONLY,
                           inspect.Parameter.VAR_POSITIONAL ]:
                trailing_init_params.insert(0, leading_init_params.pop())
        init_sig = post_init_sig.replace(
            parameters = leading_init_params + option_params +
                         trailing_init_params)
        return init_sig
    
    # Construct a __call__() signature that includes options
    def _construct_call_sig(__post_call__):
        post_call_sig = inspect.signature(__post_call__)
        post_call_params = list(post_call_sig.parameters.values())
        leading_call_params = list(post_call_params)
        trailing_call_params = []
        for p in reversed(post_call_params):
            if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.KEYWORD_ONLY,
                           inspect.Parameter.VAR_POSITIONAL ]:
                trailing_call_params.insert(0, leading_call_params.pop())
        call_sig = post_call_sig.replace(
            parameters=leading_call_params + option_params + \
                       trailing_call_params)
        return call_sig
    
    # Piece together top-level documentation string
    def _make_doc(cls):
        methods_with_doc = [
            "__post_init__",
            "__post_call__",
        ]
        docs = [cls.__doc__]
        for m_name in methods_with_doc:
            doc = ""
            if hasattr(cls, m_name):
                m = getattr(cls, m_name)
                if hasattr(m, "__doc__"):
                    doc = m.__doc__
            docs.append(doc)
        return "".join(docs)
        
    class D(C):
        # Provide default implementations for required methods, if necessary
        if hasattr(C, "__post_init__"):
            __post_init__ = C.__post_init__
        else:
            def __post_init__(self):
                pass
        if hasattr(C, "__post_call__"):
            __post_call__ = C.__post_call__
        else:
            def __post_call__(self):
                pass

        # Capture option names for use in __init__ and __call__
        _option_names = option_names
        
        # Define an __init__() that handles any supplied options before
        # calling __post_init__()
        _init_sig = _construct_init_sig(__post_init__)
        @with_signature(_init_sig)
        def __init__(self, *args, **kw):
            self._option_data = {}
            if _fire_package_present:
                fire.decorators._SetMetadata(
                    self, fire.decorators.FIRE_DEFAULTS_DICT, self._option_data)
            option_kw = {}
            for o_name in self._option_names:
                if o_name in kw:
                    option_kw[o_name] = kw.pop(o_name)
            self._set_option_attrs_from_args(**option_kw)
            return self.__post_init__(*args, **kw)
        
        # Define a __call__() that handles any supplied options before
        # calling __post_call__()
        _call_sig = _construct_call_sig(__post_call__)    
        @with_signature(_call_sig)
        def __call__(self, *args, **kw):
            option_kw = {}
            for o_name in self._option_names:
                if o_name in kw:
                    option_kw[o_name] = kw.pop(o_name)
            self._set_option_attrs_from_args(**option_kw)
            return self.__post_call__(*args, **kw)
        
        @with_signature(options_sig)
        def _set_option_attrs_from_args(self, **kw):
            pass
    
        # Piece together top-level documentation string
        __doc__ = _make_doc(C)
    
    return D
