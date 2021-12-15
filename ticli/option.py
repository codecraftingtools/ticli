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

    # Construct an __init__() signature that includes options
    def _construct_init_sig(_init, option_params):
        init_sig = inspect.signature(_init)
        init_params = list(init_sig.parameters.values())
        leading_init_params = list(init_params)
        trailing_init_params = []
        for p in reversed(init_params):
            if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.KEYWORD_ONLY,
                           inspect.Parameter.VAR_POSITIONAL ]:
                trailing_init_params.insert(0, leading_init_params.pop())
        new_init_sig = init_sig.replace(
            parameters = leading_init_params + option_params +
                         trailing_init_params)
        return new_init_sig
    
    # Construct a __call__() signature that includes options
    def _construct_call_sig(_invoke, option_params):
        invoke_sig = inspect.signature(_invoke)
        invoke_params = list(invoke_sig.parameters.values())
        leading_invoke_params = list(invoke_params)
        trailing_invoke_params = []
        for p in reversed(invoke_params):
            if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.KEYWORD_ONLY,
                           inspect.Parameter.VAR_POSITIONAL ]:
                trailing_invoke_params.insert(0, leading_invoke_params.pop())
        call_sig = invoke_sig.replace(
            parameters=leading_invoke_params + option_params + \
                       trailing_invoke_params)
        return call_sig
    
    # Piece together top-level documentation string
    def _make_doc(cls):
        methods_with_doc = [
            "_options",
            "_init",
            "_invoke",
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
        if hasattr(C, "_options"):
            _options = C._options
        else:
            print("adding _options")
            def _options(self):
                pass
        if hasattr(C, "_init"):
            _init = C._init
        else:
            print("adding _init")
            def _init(self):
                pass
        if hasattr(C, "_invoke"):
            _invoke = C._invoke
        else:
            print("adding _invoke")
            def _invoke(self):
                pass

        # Extract information about options from the method signature
        _option_names = inspect.getfullargspec(_options)[0][1:]
        _options_sig = inspect.signature(_options)
        _option_params = list(_options_sig.parameters.values())[1:]
        
        # Define an __init__() that handles options before calling _init()
        _init_sig = _construct_init_sig(_init, _option_params)
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
            self._options(**option_kw)
            return self._init(*args, **kw)
        
        # Define a __call__() that handles options before calling _invoke()
        _call_sig = _construct_call_sig(_invoke, _option_params)    
        @with_signature(_call_sig)
        def __call__(self, *args, **kw):
            option_kw = {}
            for o_name in self._option_names:
                if o_name in kw:
                    option_kw[o_name] = kw.pop(o_name)
            self._options(**option_kw)
            return self._invoke(*args, **kw)
    
        # Piece together top-level documentation string
        __doc__ = _make_doc(C)
    
    return D
