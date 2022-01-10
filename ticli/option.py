# Copyright (C) 2022 Jeffrey A. Webb
# Copyright (C) 2021 NTA, Inc.

import sys
import inspect
from makefun import with_signature
from decopatch import class_decorator, DECORATED
from .validation import (
    check_type,
    print_validation_error,
    ValidationError,
    validate_arguments,
)
from . import fire

def _make_validating_version_of(member):
    g = validate_arguments(member)
    @with_signature(inspect.signature(member))
    def f(self, *args, **kw):
        return g(self, *args, **kw)
    return f

@class_decorator
def group(C=DECORATED):

    # Add validation for public methods
    for name, member in dict(C.__dict__).items():
        if not name.startswith("_") and inspect.isfunction(member):
            # Replace the unvalidated method with one that validates arguments
            setattr(C, name, _make_validating_version_of(member))
            
    # Find any option group base classes
    base_option_groups = []
    for b in C.__bases__:
        if hasattr(b, "_is_option_group") and b._is_option_group:
            base_option_groups.append(b)
        
    # Start with the previous set of options
    option_types = {}
    option_values = {}
    for b in  base_option_groups:
        option_types.update(b._option_types)
        option_values.update(b._option_values)
                             
    # Retrieve option names and types from class annotations
    new_option_types = C.__dict__.get('__annotations__', {})
    new_option_names = list(new_option_types.keys())

    # Remove class attributes for options with default values and capture the
    # default values
    new_option_values = {}
    for opt_name in new_option_names:
        if hasattr(C, opt_name):
            opt_value = getattr(C, opt_name)
            new_option_values[opt_name] = opt_value
            delattr(C, opt_name)

    # Add new items to the overall option information variables
    option_types.update(new_option_types)
    option_values.update(new_option_values)
    option_names = list(option_types.keys())
    
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
    def _construct_sig_with_inserted_options(source_sig, skip_self=True):
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
    
    
    # Piece together option docs for top-level documentation string
    def _make_options_doc(cls):
        docs = []
        class_doc = cls.__doc__
        if class_doc:
            docs.append(inspect.cleandoc(class_doc))
        # Add argument portion of base class docs
        for b in base_option_groups:
            base_class_doc = b._options_doc
            if base_class_doc:
                # Strip off class description and just keep option docs
                idx = base_class_doc.find("Args:")
                if idx >= 0:
                    # Go back to the beginning of the Args line, if needed
                    idx2 = base_class_doc.rfind("\n", 0, idx)
                    if idx2 >= 0:
                        idx=idx2
                    base_class_doc = base_class_doc[idx:]
                    docs.append(inspect.cleandoc(base_class_doc))
        return "\n".join(docs)
    
    # Piece together extra method docs for top-level documentation string
    def _make_extra_doc(cls):
        methods_with_doc = [
            "__post_init__",
            "__post_call__",
        ]
        docs = []
        for m_name in methods_with_doc:
            doc = ""
            if hasattr(cls, m_name):
                m = getattr(cls, m_name)
                if hasattr(m, "__doc__"):
                    doc = m.__doc__
            if doc:
                docs.append(inspect.cleandoc(doc))
        return "\n".join(docs)
        
    class D(C):
        # Mark class as an option class
        _is_option_group = True
        
        # Capture info about options for later use
        _option_types = option_types
        _option_values = option_values
        _option_names = option_names
        
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

        # Construct an __init__() signature for use with fire
        _post_init_sig = inspect.signature(__post_init__)
        _init_sig = _construct_sig_with_inserted_options(_post_init_sig)
        @with_signature(_init_sig)
        def _dummy_init(self):
            pass

        # Extract the __post_init__ parameter names
        _post_init_param_names = list(_post_init_sig.parameters.keys())[1:]
        
        # Define an __init__() that handles any supplied options before
        # calling __post_init__() without the option parameters.
        def __init__(self, *args, **kw):
            self._option_data = {}
            # Tell fire to use the current option values as defaults
            fire.decorators._SetMetadata(
                self, fire.decorators.FIRE_DEFAULTS_DICT,
                self._option_data)
            # Tell fire to use the desired signature for __call__
            fire.decorators._SetMetadata(
                self, fire.decorators.FIRE_STAND_IN, D._dummy_call)
            # Check if any positional arguments for __post_call__ are defined
            post_call_has_positional_args = False
            for param_name, param_val in \
                self._post_call_sig.parameters.items():
                if param_name == "self":
                    continue
                if param_val.default == inspect.Parameter.empty:
                    post_call_has_positional_args = True
            if post_call_has_positional_args:
                # Tell fire to allow positional arguments for __call__
                fire.decorators._SetMetadata(
                    self, fire.decorators.ACCEPTS_POSITIONAL_ARGS,
                    D._dummy_call)
            print(f"__init__ args: {args} kw: {kw}")
            print(f"             : option_data: {self._option_data}")
            option_kw = self._extract_option_kw(kw)
            self._set_missing_option_attrs_from_defaults()
            self._set_option_attrs_from_args(**option_kw)
            try:
                self._validate_post_init_args(*args, **kw)
            except ValidationError as exc:
                print_validation_error(
                    exc, value_dict=kw,
                    arg_names=self._post_init_param_names, arg_values=args)
                sys.exit(-1)
            return self.__post_init__(*args, **kw)

        @validate_arguments
        @with_signature(inspect.signature(__post_init__))
        def _validate_post_init_args(self, *args, **kw):
            pass
        
        # Construct a __call__() signature for use with fire
        _post_call_sig = inspect.signature(__post_call__)
        _call_sig = _construct_sig_with_inserted_options(_post_call_sig)
        @with_signature(_call_sig)
        def _dummy_call(self):
            pass
        
        # Extract the __post_call__ parameter names
        _post_call_param_names = list(_post_call_sig.parameters.keys())[1:]
                
        # Define a __call__() that handles any supplied options before
        # calling __post_call__() without the option parameters.
        def __call__(self, *args, **kw):
            print(f"__call__ args: {args} kw: {kw}")
            print(f"             : option_data: {self._option_data}")
            option_kw = self._extract_option_kw(kw)
            self._set_option_attrs_from_args(**option_kw)
            try:
                self._validate_post_call_args(*args, **kw)
            except ValidationError as exc:
                print_validation_error(
                    exc, value_dict=kw,
                    arg_names=self._post_call_param_names, arg_values=args)
                sys.exit(-1)
            return self.__post_call__(*args, **kw)
        
        @validate_arguments
        @with_signature(inspect.signature(__post_call__))
        def _validate_post_call_args(self, *args, **kw):
            pass
        
        def _extract_option_kw(self, kw):
            option_kw = {}
            for o_name in self._option_names:
                if o_name in kw:
                    option_kw[o_name] = kw.pop(o_name)
            return option_kw

        def _set_missing_option_attrs_from_defaults(self):
            print("  setting missing option attrs from defaults")
            for p in option_params:
                print(f"    {p.name}: {p.default}")
                self._option_data[p.name] = p.default
                
        def _set_option_attrs_from_args(self, **kw):
            print(f"  setting options from kw args: {kw}")
            for key, value in kw.items():
                setattr(self, key, value)

        def __getattr__(self, key):
            if key in self._option_data:
                return self._option_data[key]
            else:
                raise AttributeError
            
        def __setattr__(self, key, value):
            if key != "_option_data" and key in self._option_data:
                print(f"    setting {key} to {value}")
                try:
                    check_type(key, value, option_types[key])
                except ValidationError as exc:
                    print_validation_error(exc, value=value)
                    sys.exit(-1)
                self._option_data[key] = value
                return
            return super().__setattr__(key, value)
         
        def _restore_defaults(self):
            self._option_data.clear()
            self._set_missing_option_attrs_from_defaults()
            
        # Piece together top-level documentation string
        _options_doc = _make_options_doc(C)
        __doc__ = "\n".join([_options_doc, _make_extra_doc(C)])
        
    fire.decorators._SetMetadata(
        D, fire.decorators.FIRE_STAND_IN, D._dummy_init)
    
    return D

def restore_defaults(s):
    s._restore_defaults()
