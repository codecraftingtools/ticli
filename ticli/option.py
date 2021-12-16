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
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=option_values.get(n,inspect.Parameter.empty),
            annotation=option_types[n])
        option_params.append(p)
    self_param = list(ref_sig.parameters.values())[0]
    option_params_with_self = [self_param] + option_params
    options_sig = ref_sig.replace(parameters=option_params_with_self)

    # Extract a function signature and insert kw-only options
    def _construct_sig_with_inserted_options(source_func, skip_self=True):
        source_sig = inspect.signature(source_func)
        source_params = list(source_sig.parameters.values())
        if skip_self:
            source_params = source_params[1:]
        leading_new_params = list(source_params)
        trailing_new_params = []
        for p in reversed(source_params):
            if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.KEYWORD_ONLY ]:
                trailing_new_params.insert(0, leading_new_params.pop())
        new_params = leading_new_params + option_params + \
                      trailing_new_params
        new_sig = source_sig.replace(parameters=new_params)
        return new_sig
    
    
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
        if not "__str__" in C.__dict__:
            # Otherwise help is printed on command completion in fire
            def __str__(self):
                return ""

        # Capture option names for use in __init__ and __call__
        _option_names = option_names
        
        # Define an __init__() that handles any supplied options before
        # calling __post_init__() without the option parameters.
        def __init__(self, *args, **kw):
            self._option_data = {}
            if _fire_package_present:
                # Tell fire to use the current option values as defaults
                fire.decorators._SetMetadata(
                    self, fire.decorators.FIRE_DEFAULTS_DICT,
                    self._option_data)
                # Tell fire to use the desired signature for __call__
                fire.decorators._SetMetadata(
                    self, fire.decorators.FIRE_STAND_IN, D._dummy_call)
            print(f"__init__ args: {args} kw: {kw}")
            option_kw = self._extract_option_kw(kw)
            self._set_option_attrs_from_args(**option_kw)
            return self.__post_init__(*args, **kw)

        # Construct an __init__() signature for use with fire
        _init_sig = _construct_sig_with_inserted_options(__post_init__)
        @with_signature(_init_sig)
        def _dummy_init(self):
            pass
        
        # Define a __call__() that handles any supplied options before
        # calling __post_call__() without the option parameters.
        def __call__(self, *args, **kw):
            print(f"__call__ args: {args} kw: {kw}")
            option_kw = self._extract_option_kw(kw)
            self._set_option_attrs_from_args(**option_kw)
            return self.__post_call__(*args, **kw)
        
        # Construct a __call__() signature for use with fire
        _call_sig = _construct_sig_with_inserted_options(__post_call__)
        @with_signature(_call_sig)
        def _dummy_call(self):
            pass
        
        def _extract_option_kw(self, kw):
            option_kw = {}
            for o_name in self._option_names:
                if o_name in kw:
                    option_kw[o_name] = kw.pop(o_name)
            return option_kw
        
        def _set_option_attrs_from_args(self, **kw):
            print(f"  setting options: {kw}")
            for key, value in kw.items():
                self._option_data[key] = value

        # Placeholder
        def _set_missing_option_attrs_from_defaults(self):
            pass

        def __getattr__(self, key):
            if key in self._option_data:
                return self._option_data[key]
            else:
                raise AttributeError
            
        def __setattr__(self, key, value):
            if key != "_option_data" and key in self._option_data:
                print(f"setting {key} to {value}")
                self._option_data[key] = value
                return
            return super().__setattr__(key, value)
         
        def _restore_defaults(self):
            self._option_data.clear()
            
        # Piece together top-level documentation string
        __doc__ = _make_doc(C)
        
    if _fire_package_present:
        fire.decorators._SetMetadata(
            D, fire.decorators.FIRE_STAND_IN, D._dummy_init)
    
    return D

def restore_defaults(s):
    s._restore_defaults()
