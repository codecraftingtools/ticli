import inspect
from makefun import with_signature
from decopatch import class_decorator, DECORATED

@class_decorator
def options(C=DECORATED):

    # Provide default implementations for required classes, if necessary
    if not "_check_options" in C.__dict__:
        def _check_options(self):
            pass
        C._check_options = _check_options
        
    if not "__init__" in C.__dict__:
        def __init__(self):
            pass
        C.__init__ = __init__
        
    if not "_invoke" in C.__dict__:
        def _invoke(self):
            pass
        C._invoke = _invoke

    # This is used in __init__()
    C._option_names = inspect.getfullargspec(C._check_options)[0][1:]

    # Extract the user-defined method signatures
    options_sig = inspect.signature(C._check_options)
    option_params = list(options_sig.parameters.values())[1:]
    init_sig = inspect.signature(C.__init__)
    init_params = list(init_sig.parameters.values())
    invoke_sig = inspect.signature(C._invoke)
    invoke_params = list(invoke_sig.parameters.values())

    # Construct an __init__() signature that includes options
    leading_init_params = list(init_params)
    trailing_init_params = []
    for p in reversed(init_params):
        if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                       inspect.Parameter.KEYWORD_ONLY,
                       inspect.Parameter.VAR_POSITIONAL]:
            trailing_init_params.insert(0, leading_init_params.pop())
    new_init_sig = init_sig.replace(
        parameters=leading_init_params + option_params + trailing_init_params)

    # Define an __init__() that handles options
    @with_signature(new_init_sig)
    def __init__(self, *args, **kw):
        option_kw = {}
        for o_name in self._option_names:
            if o_name in kw:
                option_kw[o_name] = kw.pop(o_name)
        self._check_options(**option_kw)
        return self._init(*args, **kw)
    C._init = C.__init__
    C.__init__ = __init__

    # Construct a __call__() signature that includes options
    leading_invoke_params = list(invoke_params)
    trailing_invoke_params = []
    for p in reversed(invoke_params):
        if p.kind in [ inspect.Parameter.VAR_KEYWORD,
                       inspect.Parameter.KEYWORD_ONLY,
                       inspect.Parameter.VAR_POSITIONAL]:
            trailing_invoke_params.insert(0, leading_invoke_params.pop())
    call_sig = invoke_sig.replace(
        parameters=leading_invoke_params + option_params +\
                   trailing_invoke_params)
    call_params = list(call_sig.parameters.values())
        
    # Define a __call__() that handles options before calling _invoke()
    @with_signature(call_sig)
    def __call__(self, *args, **kw):
        option_kw = {}
        for o_name in self._option_names:
            if o_name in kw:
                option_kw[o_name] = kw.pop(o_name)
        self._check_options(**option_kw)
        return self._invoke(*args, **kw)
    C.__call__ = __call__

    # Piece together top-level documentation string
    C._doc_sources = [
        C,
        C._init,
        C._invoke,
        C._check_options,
    ]
    for o in C._doc_sources:
        setattr(o, "_user_doc", getattr(o, "__doc__"))
    @classmethod
    def _make_doc(C):
        docs = []
        for o in C._doc_sources:
            docs.append("" if o._user_doc is None else o._user_doc)
        C.__doc__ = "".join(docs)
    C._make_doc = _make_doc
    C._make_doc()

    return C
