class pandas:
      from __future__ import annotations

   
   
   # start delvewheel patch
   def _delvewheel_patch_1_5_1():
       import ctypes
       

       import os
       

       import platform
       

       import sys
       

       libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pandas.libs'))
       is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
       if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
           if os.path.isdir(libs_dir):
               os.add_dll_directory(libs_dir)
       else:
           load_order_filepath = os.path.join(libs_dir, '.load-order-pandas-2.1.3')
           if os.path.isfile(load_order_filepath):
               with open(os.path.join(libs_dir, '.load-order-pandas-2.1.3')) as file:
                   load_order = file.read().split()
               for lib in load_order:
                   lib_path = os.path.join(os.path.join(libs_dir, lib))
                   if os.path.isfile(lib_path) and not ctypes.windll.kernel32.LoadLibraryExW(ctypes.c_wchar_p(lib_path), None, 0x00000008):
                       raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError()))
   
   
   _delvewheel_patch_1_5_1()
   del _delvewheel_patch_1_5_1
   # end delvewheel patch
   
   __docformat__ = "restructuredtext"
   
   # Let users know if they're missing any of our hard dependencies
   _hard_dependencies = ("numpy", "pytz", "dateutil")
   _missing_dependencies = []
   
   for _dependency in _hard_dependencies:
       try:
           __import__(_dependency)
       except ImportError as _e:  # pragma: no cover
           _missing_dependencies.append(f"{_dependency}: {_e}")
   
   if _missing_dependencies:  # pragma: no cover
       raise ImportError(
           "Unable to import required dependencies:\n" + "\n".join(_missing_dependencies)
       )
   del _hard_dependencies, _dependency, _missing_dependencies
   
   try:
       # numpy compat
       

           is_numpy_dev as _is_numpy_dev,  # pyright: ignore[reportUnusedImport] # noqa: F401,E501
       )
   except ImportError as _err:  # pragma: no cover
       _module = _err.name
       raise ImportError(
           f"C extension: {_module} not built. If you want to import "
           "pandas from the source directory, you may need to run "
           "'python setup.py build_ext' to build the C extensions first."
       ) from _err
   
   

       get_option,
       set_option,
       reset_option,
       describe_option,
       option_context,
       options,
   )
   
   # let init-time option registration happen
   class pandas:
      class core:
         class config_init:
            """
            This module is imported from the pandas package __init__.py file
            in order to ensure that the core.config options registered here will
            be available as soon as the user loads the package. if register_option
            is invoked inside specific modules, they will not be registered until that
            module is imported, which may or may not be a problem.
            
            If you need to make sure options are available even before a certain
            module is imported, register them here rather than in the module.
            
            """
            from __future__ import annotations
            
            import os
            

            
            class pandas:
               class _config:
                  class config:
                     """
                     The config module holds package-wide configurables and provides
                     a uniform API for working with them.
                     
                     Overview
                     ========
                     
                     This module supports the following requirements:
                     - options are referenced using keys in dot.notation, e.g. "x.y.option - z".
                     - keys are case-insensitive.
                     - functions should accept partial/regex keys, when unambiguous.
                     - options can be registered by modules at import time.
                     - options can be registered at init-time (via core.config_init)
                     - options have a default value, and (optionally) a description and
                       validation function associated with them.
                     - options can be deprecated, in which case referencing them
                       should produce a warning.
                     - deprecated options can optionally be rerouted to a replacement
                       so that accessing a deprecated option reroutes to a differently
                       named option.
                     - options can be reset to their default value.
                     - all option can be reset to their default value at once.
                     - all options in a certain sub - namespace can be reset at once.
                     - the user can set / get / reset or ask for the description of an option.
                     - a developer can register and mark an option as deprecated.
                     - you can register a callback to be invoked when the option value
                       is set or reset. Changing the stored value is considered misuse, but
                       is not verboten.
                     
                     Implementation
                     ==============
                     
                     - Data is stored using nested dictionaries, and should be accessed
                       through the provided API.
                     
                     - "Registered options" and "Deprecated options" have metadata associated
                       with them, which are stored in auxiliary dictionaries keyed on the
                       fully-qualified key, e.g. "x.y.z.option".
                     
                     - the config_init module is imported by the package's __init__.py file.
                       placing any register_option() calls there will ensure those options
                       are available as soon as pandas is loaded. If you use register_option
                       in a module, it will only be available after that module is imported,
                       which you should be aware of.
                     
                     - `config_prefix` is a context_manager (for use with the `with` keyword)
                       which can save developers some typing, see the docstring.
                     
                     """
                     
                     from __future__ import annotations
                     
                     

                         ContextDecorator,
                         contextmanager,
                     )
                     import re
                     

                     

                         TYPE_CHECKING,
                         Any,
                         Callable,
                         Generic,
                         NamedTuple,
                         cast,
                     )
                     import warnings
                     

                     
                     

                         F,
                         T,
                     )
                     

                     
                     if TYPE_CHECKING:
                         

                             Generator,
                             Iterable,
                         )
                     
                     
                     class DeprecatedOption(NamedTuple):
                         key: str
                         msg: str | None
                         rkey: str | None
                         removal_ver: str | None
                     
                     
                     class RegisteredOption(NamedTuple):
                         key: str
                         defval: object
                         doc: str
                         validator: Callable[[object], Any] | None
                         cb: Callable[[str], Any] | None
                     
                     
                     # holds deprecated option metadata
                     _deprecated_options: dict[str, DeprecatedOption] = {}
                     
                     # holds registered option metadata
                     _registered_options: dict[str, RegisteredOption] = {}
                     
                     # holds the current values for registered options
                     _global_config: dict[str, Any] = {}
                     
                     # keys which have a special meaning
                     _reserved_keys: list[str] = ["all"]
                     
                     
                     class OptionError(AttributeError, KeyError):
                         """
                         Exception raised for pandas.options.
                     
                         Backwards compatible with KeyError checks.
                     
                         Examples
                         --------
                         >>> pd.options.context
                         Traceback (most recent call last):
                         OptionError: No such option
                         """
                     
                     
                     #
                     # User API
                     
                     
                     def _get_single_key(pat: str, silent: bool) -> str:
                         keys = _select_options(pat)
                         if len(keys) == 0:
                             if not silent:
                                 _warn_if_deprecated(pat)
                             raise OptionError(f"No such keys(s): {repr(pat)}")
                         if len(keys) > 1:
                             raise OptionError("Pattern matched multiple keys")
                         key = keys[0]
                     
                         if not silent:
                             _warn_if_deprecated(key)
                     
                         key = _translate_key(key)
                     
                         return key
                     
                     
                     def _get_option(pat: str, silent: bool = False) -> Any:
                         key = _get_single_key(pat, silent)
                     
                         # walk the nested dict
                         root, k = _get_root(key)
                         return root[k]
                     
                     
                     def _set_option(*args, **kwargs) -> None:
                         # must at least 1 arg deal with constraints later
                         nargs = len(args)
                         if not nargs or nargs % 2 != 0:
                             raise ValueError("Must provide an even number of non-keyword arguments")
                     
                         # default to false
                         silent = kwargs.pop("silent", False)
                     
                         if kwargs:
                             kwarg = next(iter(kwargs.keys()))
                             raise TypeError(f'_set_option() got an unexpected keyword argument "{kwarg}"')
                     
                         for k, v in zip(args[::2], args[1::2]):
                             key = _get_single_key(k, silent)
                     
                             o = _get_registered_option(key)
                             if o and o.validator:
                                 o.validator(v)
                     
                             # walk the nested dict
                             root, k_root = _get_root(key)
                             root[k_root] = v
                     
                             if o.cb:
                                 if silent:
                                     with warnings.catch_warnings(record=True):
                                         o.cb(key)
                                 else:
                                     o.cb(key)
                     
                     
                     def _describe_option(pat: str = "", _print_desc: bool = True) -> str | None:
                         keys = _select_options(pat)
                         if len(keys) == 0:
                             raise OptionError("No such keys(s)")
                     
                         s = "\n".join([_build_option_description(k) for k in keys])
                     
                         if _print_desc:
                             print(s)
                             return None
                         return s
                     
                     
                     def _reset_option(pat: str, silent: bool = False) -> None:
                         keys = _select_options(pat)
                     
                         if len(keys) == 0:
                             raise OptionError("No such keys(s)")
                     
                         if len(keys) > 1 and len(pat) < 4 and pat != "all":
                             raise ValueError(
                                 "You must specify at least 4 characters when "
                                 "resetting multiple keys, use the special keyword "
                                 '"all" to reset all the options to their default value'
                             )
                     
                         for k in keys:
                             _set_option(k, _registered_options[k].defval, silent=silent)
                     
                     
                     def get_default_val(pat: str):
                         key = _get_single_key(pat, silent=True)
                         return _get_registered_option(key).defval
                     
                     
                     class DictWrapper:
                         """provide attribute-style access to a nested dict"""
                     
                         def __init__(self, d: dict[str, Any], prefix: str = "") -> None:
                             object.__setattr__(self, "d", d)
                             object.__setattr__(self, "prefix", prefix)
                     
                         def __setattr__(self, key: str, val: Any) -> None:
                             prefix = object.__getattribute__(self, "prefix")
                             if prefix:
                                 prefix += "."
                             prefix += key
                             # you can't set new keys
                             # can you can't overwrite subtrees
                             if key in self.d and not isinstance(self.d[key], dict):
                                 _set_option(prefix, val)
                             else:
                                 raise OptionError("You can only set the value of existing options")
                     
                         def __getattr__(self, key: str):
                             prefix = object.__getattribute__(self, "prefix")
                             if prefix:
                                 prefix += "."
                             prefix += key
                             try:
                                 v = object.__getattribute__(self, "d")[key]
                             except KeyError as err:
                                 raise OptionError("No such option") from err
                             if isinstance(v, dict):
                                 return DictWrapper(v, prefix)
                             else:
                                 return _get_option(prefix)
                     
                         def __dir__(self) -> Iterable[str]:
                             return list(self.d.keys())
                     
                     
                     # For user convenience,  we'd like to have the available options described
                     # in the docstring. For dev convenience we'd like to generate the docstrings
                     # dynamically instead of maintaining them by hand. To this, we use the
                     # class below which wraps functions inside a callable, and converts
                     # __doc__ into a property function. The doctsrings below are templates
                     # using the py2.6+ advanced formatting syntax to plug in a concise list
                     # of options, and option descriptions.
                     
                     
                     class CallableDynamicDoc(Generic[T]):
                         def __init__(self, func: Callable[..., T], doc_tmpl: str) -> None:
                             self.__doc_tmpl__ = doc_tmpl
                             self.__func__ = func
                     
                         def __call__(self, *args, **kwds) -> T:
                             return self.__func__(*args, **kwds)
                     
                         # error: Signature of "__doc__" incompatible with supertype "object"
                         @property
                         def __doc__(self) -> str:  # type: ignore[override]
                             opts_desc = _describe_option("all", _print_desc=False)
                             opts_list = pp_options_list(list(_registered_options.keys()))
                             return self.__doc_tmpl__.format(opts_desc=opts_desc, opts_list=opts_list)
                     
                     
                     _get_option_tmpl = """
                     get_option(pat)
                     
                     Retrieves the value of the specified option.
                     
                     Available options:
                     
                     {opts_list}
                     
                     Parameters
                     ----------
                     pat : str
                         Regexp which should match a single option.
                         Note: partial matches are supported for convenience, but unless you use the
                         full option name (e.g. x.y.z.option_name), your code may break in future
                         versions if new options with similar names are introduced.
                     
                     Returns
                     -------
                     result : the value of the option
                     
                     Raises
                     ------
                     OptionError : if no such option exists
                     
                     Notes
                     -----
                     Please reference the :ref:`User Guide <options>` for more information.
                     
                     The available options with its descriptions:
                     
                     {opts_desc}
                     
                     Examples
                     --------
                     >>> pd.get_option('display.max_columns')  # doctest: +SKIP
                     4
                     """
                     
                     _set_option_tmpl = """
                     set_option(pat, value)
                     
                     Sets the value of the specified option.
                     
                     Available options:
                     
                     {opts_list}
                     
                     Parameters
                     ----------
                     pat : str
                         Regexp which should match a single option.
                         Note: partial matches are supported for convenience, but unless you use the
                         full option name (e.g. x.y.z.option_name), your code may break in future
                         versions if new options with similar names are introduced.
                     value : object
                         New value of option.
                     
                     Returns
                     -------
                     None
                     
                     Raises
                     ------
                     OptionError if no such option exists
                     
                     Notes
                     -----
                     Please reference the :ref:`User Guide <options>` for more information.
                     
                     The available options with its descriptions:
                     
                     {opts_desc}
                     
                     Examples
                     --------
                     >>> pd.set_option('display.max_columns', 4)
                     >>> df = pd.DataFrame([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
                     >>> df
                        0  1  ...  3   4
                     0  1  2  ...  4   5
                     1  6  7  ...  9  10
                     [2 rows x 5 columns]
                     >>> pd.reset_option('display.max_columns')
                     """
                     
                     _describe_option_tmpl = """
                     describe_option(pat, _print_desc=False)
                     
                     Prints the description for one or more registered options.
                     
                     Call with no arguments to get a listing for all registered options.
                     
                     Available options:
                     
                     {opts_list}
                     
                     Parameters
                     ----------
                     pat : str
                         Regexp pattern. All matching keys will have their description displayed.
                     _print_desc : bool, default True
                         If True (default) the description(s) will be printed to stdout.
                         Otherwise, the description(s) will be returned as a unicode string
                         (for testing).
                     
                     Returns
                     -------
                     None by default, the description(s) as a unicode string if _print_desc
                     is False
                     
                     Notes
                     -----
                     Please reference the :ref:`User Guide <options>` for more information.
                     
                     The available options with its descriptions:
                     
                     {opts_desc}
                     
                     Examples
                     --------
                     >>> pd.describe_option('display.max_columns')  # doctest: +SKIP
                     display.max_columns : int
                         If max_cols is exceeded, switch to truncate view...
                     """
                     
                     _reset_option_tmpl = """
                     reset_option(pat)
                     
                     Reset one or more options to their default value.
                     
                     Pass "all" as argument to reset all options.
                     
                     Available options:
                     
                     {opts_list}
                     
                     Parameters
                     ----------
                     pat : str/regex
                         If specified only options matching `prefix*` will be reset.
                         Note: partial matches are supported for convenience, but unless you
                         use the full option name (e.g. x.y.z.option_name), your code may break
                         in future versions if new options with similar names are introduced.
                     
                     Returns
                     -------
                     None
                     
                     Notes
                     -----
                     Please reference the :ref:`User Guide <options>` for more information.
                     
                     The available options with its descriptions:
                     
                     {opts_desc}
                     
                     Examples
                     --------
                     >>> pd.reset_option('display.max_columns')  # doctest: +SKIP
                     """
                     
                     # bind the functions with their docstrings into a Callable
                     # and use that as the functions exposed in pd.api
                     get_option = CallableDynamicDoc(_get_option, _get_option_tmpl)
                     set_option = CallableDynamicDoc(_set_option, _set_option_tmpl)
                     reset_option = CallableDynamicDoc(_reset_option, _reset_option_tmpl)
                     describe_option = CallableDynamicDoc(_describe_option, _describe_option_tmpl)
                     options = DictWrapper(_global_config)
                     
                     #
                     # Functions for use by pandas developers, in addition to User - api
                     
                     
                     class option_context(ContextDecorator):
                         """
                         Context manager to temporarily set options in the `with` statement context.
                     
                         You need to invoke as ``option_context(pat, val, [(pat, val), ...])``.
                     
                         Examples
                         --------
                         >>> from pandas import option_context
                         >>> with option_context('display.max_rows', 10, 'display.max_columns', 5):
                         ...     pass
                         """
                     
                         def __init__(self, *args) -> None:
                             if len(args) % 2 != 0 or len(args) < 2:
                                 raise ValueError(
                                     "Need to invoke as option_context(pat, val, [(pat, val), ...])."
                                 )
                     
                             self.ops = list(zip(args[::2], args[1::2]))
                     
                         def __enter__(self) -> None:
                             self.undo = [(pat, _get_option(pat)) for pat, val in self.ops]
                     
                             for pat, val in self.ops:
                                 _set_option(pat, val, silent=True)
                     
                         def __exit__(self, *args) -> None:
                             if self.undo:
                                 for pat, val in self.undo:
                                     _set_option(pat, val, silent=True)
                     
                     
                     def register_option(
                         key: str,
                         defval: object,
                         doc: str = "",
                         validator: Callable[[object], Any] | None = None,
                         cb: Callable[[str], Any] | None = None,
                     ) -> None:
                         """
                         Register an option in the package-wide pandas config object
                     
                         Parameters
                         ----------
                         key : str
                             Fully-qualified key, e.g. "x.y.option - z".
                         defval : object
                             Default value of the option.
                         doc : str
                             Description of the option.
                         validator : Callable, optional
                             Function of a single argument, should raise `ValueError` if
                             called with a value which is not a legal value for the option.
                         cb
                             a function of a single argument "key", which is called
                             immediately after an option value is set/reset. key is
                             the full name of the option.
                     
                         Raises
                         ------
                         ValueError if `validator` is specified and `defval` is not a valid value.
                     
                         """
                         import keyword
                         

                         import tokenize
                         

                     
                         key = key.lower()
                     
                         if key in _registered_options:
                             raise OptionError(f"Option '{key}' has already been registered")
                         if key in _reserved_keys:
                             raise OptionError(f"Option '{key}' is a reserved key")
                     
                         # the default value should be legal
                         if validator:
                             validator(defval)
                     
                         # walk the nested dict, creating dicts as needed along the path
                         path = key.split(".")
                     
                         for k in path:
                             if not re.match("^" + tokenize.Name + "$", k):
                                 raise ValueError(f"{k} is not a valid identifier")
                             if keyword.iskeyword(k):
                                 raise ValueError(f"{k} is a python keyword")
                     
                         cursor = _global_config
                         msg = "Path prefix to option '{option}' is already an option"
                     
                         for i, p in enumerate(path[:-1]):
                             if not isinstance(cursor, dict):
                                 raise OptionError(msg.format(option=".".join(path[:i])))
                             if p not in cursor:
                                 cursor[p] = {}
                             cursor = cursor[p]
                     
                         if not isinstance(cursor, dict):
                             raise OptionError(msg.format(option=".".join(path[:-1])))
                     
                         cursor[path[-1]] = defval  # initialize
                     
                         # save the option metadata
                         _registered_options[key] = RegisteredOption(
                             key=key, defval=defval, doc=doc, validator=validator, cb=cb
                         )
                     
                     
                     def deprecate_option(
                         key: str,
                         msg: str | None = None,
                         rkey: str | None = None,
                         removal_ver: str | None = None,
                     ) -> None:
                         """
                         Mark option `key` as deprecated, if code attempts to access this option,
                         a warning will be produced, using `msg` if given, or a default message
                         if not.
                         if `rkey` is given, any access to the key will be re-routed to `rkey`.
                     
                         Neither the existence of `key` nor that if `rkey` is checked. If they
                         do not exist, any subsequence access will fail as usual, after the
                         deprecation warning is given.
                     
                         Parameters
                         ----------
                         key : str
                             Name of the option to be deprecated.
                             must be a fully-qualified option name (e.g "x.y.z.rkey").
                         msg : str, optional
                             Warning message to output when the key is referenced.
                             if no message is given a default message will be emitted.
                         rkey : str, optional
                             Name of an option to reroute access to.
                             If specified, any referenced `key` will be
                             re-routed to `rkey` including set/get/reset.
                             rkey must be a fully-qualified option name (e.g "x.y.z.rkey").
                             used by the default message if no `msg` is specified.
                         removal_ver : str, optional
                             Specifies the version in which this option will
                             be removed. used by the default message if no `msg` is specified.
                     
                         Raises
                         ------
                         OptionError
                             If the specified key has already been deprecated.
                         """
                         key = key.lower()
                     
                         if key in _deprecated_options:
                             raise OptionError(f"Option '{key}' has already been defined as deprecated.")
                     
                         _deprecated_options[key] = DeprecatedOption(key, msg, rkey, removal_ver)
                     
                     
                     #
                     # functions internal to the module
                     
                     
                     def _select_options(pat: str) -> list[str]:
                         """
                         returns a list of keys matching `pat`
                     
                         if pat=="all", returns all registered options
                         """
                         # short-circuit for exact key
                         if pat in _registered_options:
                             return [pat]
                     
                         # else look through all of them
                         keys = sorted(_registered_options.keys())
                         if pat == "all":  # reserved key
                             return keys
                     
                         return [k for k in keys if re.search(pat, k, re.I)]
                     
                     
                     def _get_root(key: str) -> tuple[dict[str, Any], str]:
                         path = key.split(".")
                         cursor = _global_config
                         for p in path[:-1]:
                             cursor = cursor[p]
                         return cursor, path[-1]
                     
                     
                     def _is_deprecated(key: str) -> bool:
                         """Returns True if the given option has been deprecated"""
                         key = key.lower()
                         return key in _deprecated_options
                     
                     
                     def _get_deprecated_option(key: str):
                         """
                         Retrieves the metadata for a deprecated option, if `key` is deprecated.
                     
                         Returns
                         -------
                         DeprecatedOption (namedtuple) if key is deprecated, None otherwise
                         """
                         try:
                             d = _deprecated_options[key]
                         except KeyError:
                             return None
                         else:
                             return d
                     
                     
                     def _get_registered_option(key: str):
                         """
                         Retrieves the option metadata if `key` is a registered option.
                     
                         Returns
                         -------
                         RegisteredOption (namedtuple) if key is deprecated, None otherwise
                         """
                         return _registered_options.get(key)
                     
                     
                     def _translate_key(key: str) -> str:
                         """
                         if key id deprecated and a replacement key defined, will return the
                         replacement key, otherwise returns `key` as - is
                         """
                         d = _get_deprecated_option(key)
                         if d:
                             return d.rkey or key
                         else:
                             return key
                     
                     
                     def _warn_if_deprecated(key: str) -> bool:
                         """
                         Checks if `key` is a deprecated option and if so, prints a warning.
                     
                         Returns
                         -------
                         bool - True if `key` is deprecated, False otherwise.
                         """
                         d = _get_deprecated_option(key)
                         if d:
                             if d.msg:
                                 warnings.warn(
                                     d.msg,
                                     FutureWarning,
                                     stacklevel=find_stack_level(),
                                 )
                             else:
                                 msg = f"'{key}' is deprecated"
                                 if d.removal_ver:
                                     msg += f" and will be removed in {d.removal_ver}"
                                 if d.rkey:
                                     msg += f", please use '{d.rkey}' instead."
                                 else:
                                     msg += ", please refrain from using it."
                     
                                 warnings.warn(msg, FutureWarning, stacklevel=find_stack_level())
                             return True
                         return False
                     
                     
                     def _build_option_description(k: str) -> str:
                         """Builds a formatted description of a registered option and prints it"""
                         o = _get_registered_option(k)
                         d = _get_deprecated_option(k)
                     
                         s = f"{k} "
                     
                         if o.doc:
                             s += "\n".join(o.doc.strip().split("\n"))
                         else:
                             s += "No description available."
                     
                         if o:
                             s += f"\n    [default: {o.defval}] [currently: {_get_option(k, True)}]"
                     
                         if d:
                             rkey = d.rkey or ""
                             s += "\n    (Deprecated"
                             s += f", use `{rkey}` instead."
                             s += ")"
                     
                         return s
                     
                     
                     def pp_options_list(keys: Iterable[str], width: int = 80, _print: bool = False):
                         """Builds a concise listing of available options, grouped by prefix"""
                         

                         

                     
                         def pp(name: str, ks: Iterable[str]) -> list[str]:
                             pfx = "- " + name + ".[" if name else ""
                             ls = wrap(
                                 ", ".join(ks),
                                 width,
                                 initial_indent=pfx,
                                 subsequent_indent="  ",
                                 break_long_words=False,
                             )
                             if ls and ls[-1] and name:
                                 ls[-1] = ls[-1] + "]"
                             return ls
                     
                         ls: list[str] = []
                         singles = [x for x in sorted(keys) if x.find(".") < 0]
                         if singles:
                             ls += pp("", singles)
                         keys = [x for x in keys if x.find(".") >= 0]
                     
                         for k, g in groupby(sorted(keys), lambda x: x[: x.rfind(".")]):
                             ks = [x[len(k) + 1 :] for x in list(g)]
                             ls += pp(k, ks)
                         s = "\n".join(ls)
                         if _print:
                             print(s)
                         else:
                             return s
                     
                     
                     #
                     # helpers
                     
                     
                     @contextmanager
                     def config_prefix(prefix: str) -> Generator[None, None, None]:
                         """
                         contextmanager for multiple invocations of API with a common prefix
                     
                         supported API functions: (register / get / set )__option
                     
                         Warning: This is not thread - safe, and won't work properly if you import
                         the API functions into your module using the "from x import y" construct.
                     
                         Example
                         -------
                         import pandas._config.config as cf
                         with cf.config_prefix("display.font"):
                             cf.register_option("color", "red")
                             cf.register_option("size", " 5 pt")
                             cf.set_option(size, " 6 pt")
                             cf.get_option(size)
                             ...
                     
                             etc'
                     
                         will register options "display.font.color", "display.font.size", set the
                         value of "display.font.size"... and so on.
                         """
                         # Note: reset_option relies on set_option, and on key directly
                         # it does not fit in to this monkey-patching scheme
                     
                         global register_option, get_option, set_option
                     
                         def wrap(func: F) -> F:
                             def inner(key: str, *args, **kwds):
                                 pkey = f"{prefix}.{key}"
                                 return func(pkey, *args, **kwds)
                     
                             return cast(F, inner)
                     
                         _register_option = register_option
                         _get_option = get_option
                         _set_option = set_option
                         set_option = wrap(set_option)
                         get_option = wrap(get_option)
                         register_option = wrap(register_option)
                         try:
                             yield
                         finally:
                             set_option = _set_option
                             get_option = _get_option
                             register_option = _register_option
                     
                     
                     # These factories and methods are handy for use as the validator
                     # arg in register_option
                     
                     
                     def is_type_factory(_type: type[Any]) -> Callable[[Any], None]:
                         """
                     
                         Parameters
                         ----------
                         `_type` - a type to be compared against (e.g. type(x) == `_type`)
                     
                         Returns
                         -------
                         validator - a function of a single argument x , which raises
                                     ValueError if type(x) is not equal to `_type`
                     
                         """
                     
                         def inner(x) -> None:
                             if type(x) != _type:
                                 raise ValueError(f"Value must have type '{_type}'")
                     
                         return inner
                     
                     
                     def is_instance_factory(_type) -> Callable[[Any], None]:
                         """
                     
                         Parameters
                         ----------
                         `_type` - the type to be checked against
                     
                         Returns
                         -------
                         validator - a function of a single argument x , which raises
                                     ValueError if x is not an instance of `_type`
                     
                         """
                         if isinstance(_type, (tuple, list)):
                             _type = tuple(_type)
                             type_repr = "|".join(map(str, _type))
                         else:
                             type_repr = f"'{_type}'"
                     
                         def inner(x) -> None:
                             if not isinstance(x, _type):
                                 raise ValueError(f"Value must be an instance of {type_repr}")
                     
                         return inner
                     
                     
                     def is_one_of_factory(legal_values) -> Callable[[Any], None]:
                         callables = [c for c in legal_values if callable(c)]
                         legal_values = [c for c in legal_values if not callable(c)]
                     
                         def inner(x) -> None:
                             if x not in legal_values:
                                 if not any(c(x) for c in callables):
                                     uvals = [str(lval) for lval in legal_values]
                                     pp_values = "|".join(uvals)
                                     msg = f"Value must be one of {pp_values}"
                                     if len(callables):
                                         msg += " or a callable"
                                     raise ValueError(msg)
                     
                         return inner
                     
                     
                     def is_nonnegative_int(value: object) -> None:
                         """
                         Verify that value is None or a positive int.
                     
                         Parameters
                         ----------
                         value : None or int
                                 The `value` to be checked.
                     
                         Raises
                         ------
                         ValueError
                             When the value is not None or is a negative integer
                         """
                         if value is None:
                             return
                     
                         elif isinstance(value, int):
                             if value >= 0:
                                 return
                     
                         msg = "Value must be a nonnegative integer or None"
                         raise ValueError(msg)
                     
                     
                     # common type validators, for convenience
                     # usage: register_option(... , validator = is_int)
                     is_int = is_type_factory(int)
                     is_bool = is_type_factory(bool)
                     is_float = is_type_factory(float)
                     is_str = is_type_factory(str)
                     is_text = is_instance_factory((str, bytes))
                     
                     
                     def is_callable(obj) -> bool:
                         """
                     
                         Parameters
                         ----------
                         `obj` - the object to be checked
                     
                         Returns
                         -------
                         validator - returns True if object is callable
                             raises ValueError otherwise.
                     
                         """
                         if not callable(obj):
                             raise ValueError("Value must be a callable")
                         return True
                     
                  
               
            cf = pandas._config.config
            

            

                is_bool,
                is_callable,
                is_instance_factory,
                is_int,
                is_nonnegative_int,
                is_one_of_factory,
                is_str,
                is_text,
            )
            
            # compute
            
            use_bottleneck_doc = """
            : bool
                Use the bottleneck library to accelerate if it is installed,
                the default is True
                Valid values: False,True
            """
            
            
            def use_bottleneck_cb(key) -> None:
                

            
                nanops.set_use_bottleneck(cf.get_option(key))
            
            
            use_numexpr_doc = """
            : bool
                Use the numexpr library to accelerate computation if it is installed,
                the default is True
                Valid values: False,True
            """
            
            
            def use_numexpr_cb(key) -> None:
                

            
                expressions.set_use_numexpr(cf.get_option(key))
            
            
            use_numba_doc = """
            : bool
                Use the numba engine option for select operations if it is installed,
                the default is False
                Valid values: False,True
            """
            
            
            def use_numba_cb(key) -> None:
                

            
                numba_.set_use_numba(cf.get_option(key))
            
            
            with cf.config_prefix("compute"):
                cf.register_option(
                    "use_bottleneck",
                    True,
                    use_bottleneck_doc,
                    validator=is_bool,
                    cb=use_bottleneck_cb,
                )
                cf.register_option(
                    "use_numexpr", True, use_numexpr_doc, validator=is_bool, cb=use_numexpr_cb
                )
                cf.register_option(
                    "use_numba", False, use_numba_doc, validator=is_bool, cb=use_numba_cb
                )
            #
            # options from the "display" namespace
            
            pc_precision_doc = """
            : int
                Floating point output precision in terms of number of places after the
                decimal, for regular formatting as well as scientific notation. Similar
                to ``precision`` in :meth:`numpy.set_printoptions`.
            """
            
            pc_colspace_doc = """
            : int
                Default space for DataFrame columns.
            """
            
            pc_max_rows_doc = """
            : int
                If max_rows is exceeded, switch to truncate view. Depending on
                `large_repr`, objects are either centrally truncated or printed as
                a summary view. 'None' value means unlimited.
            
                In case python/IPython is running in a terminal and `large_repr`
                equals 'truncate' this can be set to 0 and pandas will auto-detect
                the height of the terminal and print a truncated object which fits
                the screen height. The IPython notebook, IPython qtconsole, or
                IDLE do not run in a terminal and hence it is not possible to do
                correct auto-detection.
            """
            
            pc_min_rows_doc = """
            : int
                The numbers of rows to show in a truncated view (when `max_rows` is
                exceeded). Ignored when `max_rows` is set to None or 0. When set to
                None, follows the value of `max_rows`.
            """
            
            pc_max_cols_doc = """
            : int
                If max_cols is exceeded, switch to truncate view. Depending on
                `large_repr`, objects are either centrally truncated or printed as
                a summary view. 'None' value means unlimited.
            
                In case python/IPython is running in a terminal and `large_repr`
                equals 'truncate' this can be set to 0 or None and pandas will auto-detect
                the width of the terminal and print a truncated object which fits
                the screen width. The IPython notebook, IPython qtconsole, or IDLE
                do not run in a terminal and hence it is not possible to do
                correct auto-detection and defaults to 20.
            """
            
            pc_max_categories_doc = """
            : int
                This sets the maximum number of categories pandas should output when
                printing out a `Categorical` or a Series of dtype "category".
            """
            
            pc_max_info_cols_doc = """
            : int
                max_info_columns is used in DataFrame.info method to decide if
                per column information will be printed.
            """
            
            pc_nb_repr_h_doc = """
            : boolean
                When True, IPython notebook will use html representation for
                pandas objects (if it is available).
            """
            
            pc_pprint_nest_depth = """
            : int
                Controls the number of nested levels to process when pretty-printing
            """
            
            pc_multi_sparse_doc = """
            : boolean
                "sparsify" MultiIndex display (don't display repeated
                elements in outer levels within groups)
            """
            
            float_format_doc = """
            : callable
                The callable should accept a floating point number and return
                a string with the desired format of the number. This is used
                in some places like SeriesFormatter.
                See formats.format.EngFormatter for an example.
            """
            
            max_colwidth_doc = """
            : int or None
                The maximum width in characters of a column in the repr of
                a pandas data structure. When the column overflows, a "..."
                placeholder is embedded in the output. A 'None' value means unlimited.
            """
            
            colheader_justify_doc = """
            : 'left'/'right'
                Controls the justification of column headers. used by DataFrameFormatter.
            """
            
            pc_expand_repr_doc = """
            : boolean
                Whether to print out the full DataFrame repr for wide DataFrames across
                multiple lines, `max_columns` is still respected, but the output will
                wrap-around across multiple "pages" if its width exceeds `display.width`.
            """
            
            pc_show_dimensions_doc = """
            : boolean or 'truncate'
                Whether to print out dimensions at the end of DataFrame repr.
                If 'truncate' is specified, only print out the dimensions if the
                frame is truncated (e.g. not display all rows and/or columns)
            """
            
            pc_east_asian_width_doc = """
            : boolean
                Whether to use the Unicode East Asian Width to calculate the display text
                width.
                Enabling this may affect to the performance (default: False)
            """
            
            pc_ambiguous_as_wide_doc = """
            : boolean
                Whether to handle Unicode characters belong to Ambiguous as Wide (width=2)
                (default: False)
            """
            
            pc_table_schema_doc = """
            : boolean
                Whether to publish a Table Schema representation for frontends
                that support it.
                (default: False)
            """
            
            pc_html_border_doc = """
            : int
                A ``border=value`` attribute is inserted in the ``<table>`` tag
                for the DataFrame HTML repr.
            """
            
            pc_html_use_mathjax_doc = """\
            : boolean
                When True, Jupyter notebook will process table contents using MathJax,
                rendering mathematical expressions enclosed by the dollar symbol.
                (default: True)
            """
            
            pc_max_dir_items = """\
            : int
                The number of items that will be added to `dir(...)`. 'None' value means
                unlimited. Because dir is cached, changing this option will not immediately
                affect already existing dataframes until a column is deleted or added.
            
                This is for instance used to suggest columns from a dataframe to tab
                completion.
            """
            
            pc_width_doc = """
            : int
                Width of the display in characters. In case python/IPython is running in
                a terminal this can be set to None and pandas will correctly auto-detect
                the width.
                Note that the IPython notebook, IPython qtconsole, or IDLE do not run in a
                terminal and hence it is not possible to correctly detect the width.
            """
            
            pc_chop_threshold_doc = """
            : float or None
                if set to a float value, all float values smaller than the given threshold
                will be displayed as exactly 0 by repr and friends.
            """
            
            pc_max_seq_items = """
            : int or None
                When pretty-printing a long sequence, no more then `max_seq_items`
                will be printed. If items are omitted, they will be denoted by the
                addition of "..." to the resulting string.
            
                If set to None, the number of items to be printed is unlimited.
            """
            
            pc_max_info_rows_doc = """
            : int or None
                df.info() will usually show null-counts for each column.
                For large frames this can be quite slow. max_info_rows and max_info_cols
                limit this null check only to frames with smaller dimensions than
                specified.
            """
            
            pc_large_repr_doc = """
            : 'truncate'/'info'
                For DataFrames exceeding max_rows/max_cols, the repr (and HTML repr) can
                show a truncated table, or switch to the view from
                df.info() (the behaviour in earlier versions of pandas).
            """
            
            pc_memory_usage_doc = """
            : bool, string or None
                This specifies if the memory usage of a DataFrame should be displayed when
                df.info() is called. Valid values True,False,'deep'
            """
            
            
            def table_schema_cb(key) -> None:
                

            
                enable_data_resource_formatter(cf.get_option(key))
            
            
            def is_terminal() -> bool:
                """
                Detect if Python is running in a terminal.
            
                Returns True if Python is running in a terminal or False if not.
                """
                try:
                    # error: Name 'get_ipython' is not defined
                    ip = get_ipython()  # type: ignore[name-defined]
                except NameError:  # assume standard Python interpreter in a terminal
                    return True
                else:
                    if hasattr(ip, "kernel"):  # IPython as a Jupyter kernel
                        return False
                    else:  # IPython in a terminal
                        return True
            
            
            with cf.config_prefix("display"):
                cf.register_option("precision", 6, pc_precision_doc, validator=is_nonnegative_int)
                cf.register_option(
                    "float_format",
                    None,
                    float_format_doc,
                    validator=is_one_of_factory([None, is_callable]),
                )
                cf.register_option(
                    "max_info_rows",
                    1690785,
                    pc_max_info_rows_doc,
                    validator=is_instance_factory((int, type(None))),
                )
                cf.register_option("max_rows", 60, pc_max_rows_doc, validator=is_nonnegative_int)
                cf.register_option(
                    "min_rows",
                    10,
                    pc_min_rows_doc,
                    validator=is_instance_factory([type(None), int]),
                )
                cf.register_option("max_categories", 8, pc_max_categories_doc, validator=is_int)
            
                cf.register_option(
                    "max_colwidth",
                    50,
                    max_colwidth_doc,
                    validator=is_nonnegative_int,
                )
                if is_terminal():
                    max_cols = 0  # automatically determine optimal number of columns
                else:
                    max_cols = 20  # cannot determine optimal number of columns
                cf.register_option(
                    "max_columns", max_cols, pc_max_cols_doc, validator=is_nonnegative_int
                )
                cf.register_option(
                    "large_repr",
                    "truncate",
                    pc_large_repr_doc,
                    validator=is_one_of_factory(["truncate", "info"]),
                )
                cf.register_option("max_info_columns", 100, pc_max_info_cols_doc, validator=is_int)
                cf.register_option(
                    "colheader_justify", "right", colheader_justify_doc, validator=is_text
                )
                cf.register_option("notebook_repr_html", True, pc_nb_repr_h_doc, validator=is_bool)
                cf.register_option("pprint_nest_depth", 3, pc_pprint_nest_depth, validator=is_int)
                cf.register_option("multi_sparse", True, pc_multi_sparse_doc, validator=is_bool)
                cf.register_option("expand_frame_repr", True, pc_expand_repr_doc)
                cf.register_option(
                    "show_dimensions",
                    "truncate",
                    pc_show_dimensions_doc,
                    validator=is_one_of_factory([True, False, "truncate"]),
                )
                cf.register_option("chop_threshold", None, pc_chop_threshold_doc)
                cf.register_option("max_seq_items", 100, pc_max_seq_items)
                cf.register_option(
                    "width", 80, pc_width_doc, validator=is_instance_factory([type(None), int])
                )
                cf.register_option(
                    "memory_usage",
                    True,
                    pc_memory_usage_doc,
                    validator=is_one_of_factory([None, True, False, "deep"]),
                )
                cf.register_option(
                    "unicode.east_asian_width", False, pc_east_asian_width_doc, validator=is_bool
                )
                cf.register_option(
                    "unicode.ambiguous_as_wide", False, pc_east_asian_width_doc, validator=is_bool
                )
                cf.register_option(
                    "html.table_schema",
                    False,
                    pc_table_schema_doc,
                    validator=is_bool,
                    cb=table_schema_cb,
                )
                cf.register_option("html.border", 1, pc_html_border_doc, validator=is_int)
                cf.register_option(
                    "html.use_mathjax", True, pc_html_use_mathjax_doc, validator=is_bool
                )
                cf.register_option(
                    "max_dir_items", 100, pc_max_dir_items, validator=is_nonnegative_int
                )
            
            tc_sim_interactive_doc = """
            : boolean
                Whether to simulate interactive mode for purposes of testing
            """
            
            with cf.config_prefix("mode"):
                cf.register_option("sim_interactive", False, tc_sim_interactive_doc)
            
            use_inf_as_na_doc = """
            : boolean
                True means treat None, NaN, INF, -INF as NA (old way),
                False means None and NaN are null, but INF, -INF are not NA
                (new way).
            
                This option is deprecated in pandas 2.1.0 and will be removed in 3.0.
            """
            
            # We don't want to start importing everything at the global context level
            # or we'll hit circular deps.
            
            
            def use_inf_as_na_cb(key) -> None:
                

            
                _use_inf_as_na(key)
            
            
            with cf.config_prefix("mode"):
                cf.register_option("use_inf_as_na", False, use_inf_as_na_doc, cb=use_inf_as_na_cb)
            
            cf.deprecate_option(
                # GH#51684
                "mode.use_inf_as_na",
                "use_inf_as_na option is deprecated and will be removed in a future "
                "version. Convert inf values to NaN before operating instead.",
            )
            
            data_manager_doc = """
            : string
                Internal data manager type; can be "block" or "array". Defaults to "block",
                unless overridden by the 'PANDAS_DATA_MANAGER' environment variable (needs
                to be set before pandas is imported).
            """
            
            
            with cf.config_prefix("mode"):
                cf.register_option(
                    "data_manager",
                    # Get the default from an environment variable, if set, otherwise defaults
                    # to "block". This environment variable can be set for testing.
                    os.environ.get("PANDAS_DATA_MANAGER", "block"),
                    data_manager_doc,
                    validator=is_one_of_factory(["block", "array"]),
                )
            
            
            # TODO better name?
            copy_on_write_doc = """
            : bool
                Use new copy-view behaviour using Copy-on-Write. Defaults to False,
                unless overridden by the 'PANDAS_COPY_ON_WRITE' environment variable
                (if set to "1" for True, needs to be set before pandas is imported).
            """
            
            
            with cf.config_prefix("mode"):
                cf.register_option(
                    "copy_on_write",
                    # Get the default from an environment variable, if set, otherwise defaults
                    # to False. This environment variable can be set for testing.
                    os.environ.get("PANDAS_COPY_ON_WRITE", "0") == "1",
                    copy_on_write_doc,
                    validator=is_bool,
                )
            
            
            # user warnings
            chained_assignment = """
            : string
                Raise an exception, warn, or no action if trying to use chained assignment,
                The default is warn
            """
            
            with cf.config_prefix("mode"):
                cf.register_option(
                    "chained_assignment",
                    "warn",
                    chained_assignment,
                    validator=is_one_of_factory([None, "warn", "raise"]),
                )
            
            
            string_storage_doc = """
            : string
                The default storage for StringDtype. This option is ignored if
                ``future.infer_string`` is set to True.
            """
            
            with cf.config_prefix("mode"):
                cf.register_option(
                    "string_storage",
                    "python",
                    string_storage_doc,
                    validator=is_one_of_factory(["python", "pyarrow", "pyarrow_numpy"]),
                )
            
            
            # Set up the io.excel specific reader configuration.
            reader_engine_doc = """
            : string
                The default Excel reader engine for '{ext}' files. Available options:
                auto, {others}.
            """
            
            _xls_options = ["xlrd"]
            _xlsm_options = ["xlrd", "openpyxl"]
            _xlsx_options = ["xlrd", "openpyxl"]
            _ods_options = ["odf"]
            _xlsb_options = ["pyxlsb"]
            
            
            with cf.config_prefix("io.excel.xls"):
                cf.register_option(
                    "reader",
                    "auto",
                    reader_engine_doc.format(ext="xls", others=", ".join(_xls_options)),
                    validator=is_one_of_factory(_xls_options + ["auto"]),
                )
            
            with cf.config_prefix("io.excel.xlsm"):
                cf.register_option(
                    "reader",
                    "auto",
                    reader_engine_doc.format(ext="xlsm", others=", ".join(_xlsm_options)),
                    validator=is_one_of_factory(_xlsm_options + ["auto"]),
                )
            
            
            with cf.config_prefix("io.excel.xlsx"):
                cf.register_option(
                    "reader",
                    "auto",
                    reader_engine_doc.format(ext="xlsx", others=", ".join(_xlsx_options)),
                    validator=is_one_of_factory(_xlsx_options + ["auto"]),
                )
            
            
            with cf.config_prefix("io.excel.ods"):
                cf.register_option(
                    "reader",
                    "auto",
                    reader_engine_doc.format(ext="ods", others=", ".join(_ods_options)),
                    validator=is_one_of_factory(_ods_options + ["auto"]),
                )
            
            with cf.config_prefix("io.excel.xlsb"):
                cf.register_option(
                    "reader",
                    "auto",
                    reader_engine_doc.format(ext="xlsb", others=", ".join(_xlsb_options)),
                    validator=is_one_of_factory(_xlsb_options + ["auto"]),
                )
            
            # Set up the io.excel specific writer configuration.
            writer_engine_doc = """
            : string
                The default Excel writer engine for '{ext}' files. Available options:
                auto, {others}.
            """
            
            _xlsm_options = ["openpyxl"]
            _xlsx_options = ["openpyxl", "xlsxwriter"]
            _ods_options = ["odf"]
            
            
            with cf.config_prefix("io.excel.xlsm"):
                cf.register_option(
                    "writer",
                    "auto",
                    writer_engine_doc.format(ext="xlsm", others=", ".join(_xlsm_options)),
                    validator=str,
                )
            
            
            with cf.config_prefix("io.excel.xlsx"):
                cf.register_option(
                    "writer",
                    "auto",
                    writer_engine_doc.format(ext="xlsx", others=", ".join(_xlsx_options)),
                    validator=str,
                )
            
            
            with cf.config_prefix("io.excel.ods"):
                cf.register_option(
                    "writer",
                    "auto",
                    writer_engine_doc.format(ext="ods", others=", ".join(_ods_options)),
                    validator=str,
                )
            
            
            # Set up the io.parquet specific configuration.
            parquet_engine_doc = """
            : string
                The default parquet reader/writer engine. Available options:
                'auto', 'pyarrow', 'fastparquet', the default is 'auto'
            """
            
            with cf.config_prefix("io.parquet"):
                cf.register_option(
                    "engine",
                    "auto",
                    parquet_engine_doc,
                    validator=is_one_of_factory(["auto", "pyarrow", "fastparquet"]),
                )
            
            
            # Set up the io.sql specific configuration.
            sql_engine_doc = """
            : string
                The default sql reader/writer engine. Available options:
                'auto', 'sqlalchemy', the default is 'auto'
            """
            
            with cf.config_prefix("io.sql"):
                cf.register_option(
                    "engine",
                    "auto",
                    sql_engine_doc,
                    validator=is_one_of_factory(["auto", "sqlalchemy"]),
                )
            
            # --------
            # Plotting
            # ---------
            
            plotting_backend_doc = """
            : str
                The plotting backend to use. The default value is "matplotlib", the
                backend provided with pandas. Other backends can be specified by
                providing the name of the module that implements the backend.
            """
            
            
            def register_plotting_backend_cb(key) -> None:
                if key == "matplotlib":
                    # We defer matplotlib validation, since it's the default
                    return
                

            
                _get_plot_backend(key)
            
            
            with cf.config_prefix("plotting"):
                cf.register_option(
                    "backend",
                    defval="matplotlib",
                    doc=plotting_backend_doc,
                    validator=register_plotting_backend_cb,
                )
            
            
            register_converter_doc = """
            : bool or 'auto'.
                Whether to register converters with matplotlib's units registry for
                dates, times, datetimes, and Periods. Toggling to False will remove
                the converters, restoring any converters that pandas overwrote.
            """
            
            
            def register_converter_cb(key) -> None:
                

                    deregister_matplotlib_converters,
                    register_matplotlib_converters,
                )
            
                if cf.get_option(key):
                    register_matplotlib_converters()
                else:
                    deregister_matplotlib_converters()
            
            
            with cf.config_prefix("plotting.matplotlib"):
                cf.register_option(
                    "register_converters",
                    "auto",
                    register_converter_doc,
                    validator=is_one_of_factory(["auto", True, False]),
                    cb=register_converter_cb,
                )
            
            # ------
            # Styler
            # ------
            
            styler_sparse_index_doc = """
            : bool
                Whether to sparsify the display of a hierarchical index. Setting to False will
                display each explicit level element in a hierarchical key for each row.
            """
            
            styler_sparse_columns_doc = """
            : bool
                Whether to sparsify the display of hierarchical columns. Setting to False will
                display each explicit level element in a hierarchical key for each column.
            """
            
            styler_render_repr = """
            : str
                Determine which output to use in Jupyter Notebook in {"html", "latex"}.
            """
            
            styler_max_elements = """
            : int
                The maximum number of data-cell (<td>) elements that will be rendered before
                trimming will occur over columns, rows or both if needed.
            """
            
            styler_max_rows = """
            : int, optional
                The maximum number of rows that will be rendered. May still be reduced to
                satisfy ``max_elements``, which takes precedence.
            """
            
            styler_max_columns = """
            : int, optional
                The maximum number of columns that will be rendered. May still be reduced to
                satisfy ``max_elements``, which takes precedence.
            """
            
            styler_precision = """
            : int
                The precision for floats and complex numbers.
            """
            
            styler_decimal = """
            : str
                The character representation for the decimal separator for floats and complex.
            """
            
            styler_thousands = """
            : str, optional
                The character representation for thousands separator for floats, int and complex.
            """
            
            styler_na_rep = """
            : str, optional
                The string representation for values identified as missing.
            """
            
            styler_escape = """
            : str, optional
                Whether to escape certain characters according to the given context; html or latex.
            """
            
            styler_formatter = """
            : str, callable, dict, optional
                A formatter object to be used as default within ``Styler.format``.
            """
            
            styler_multirow_align = """
            : {"c", "t", "b"}
                The specifier for vertical alignment of sparsified LaTeX multirows.
            """
            
            styler_multicol_align = r"""
            : {"r", "c", "l", "naive-l", "naive-r"}
                The specifier for horizontal alignment of sparsified LaTeX multicolumns. Pipe
                decorators can also be added to non-naive values to draw vertical
                rules, e.g. "\|r" will draw a rule on the left side of right aligned merged cells.
            """
            
            styler_hrules = """
            : bool
                Whether to add horizontal rules on top and bottom and below the headers.
            """
            
            styler_environment = """
            : str
                The environment to replace ``\\begin{table}``. If "longtable" is used results
                in a specific longtable environment format.
            """
            
            styler_encoding = """
            : str
                The encoding used for output HTML and LaTeX files.
            """
            
            styler_mathjax = """
            : bool
                If False will render special CSS classes to table attributes that indicate Mathjax
                will not be used in Jupyter Notebook.
            """
            
            with cf.config_prefix("styler"):
                cf.register_option("sparse.index", True, styler_sparse_index_doc, validator=is_bool)
            
                cf.register_option(
                    "sparse.columns", True, styler_sparse_columns_doc, validator=is_bool
                )
            
                cf.register_option(
                    "render.repr",
                    "html",
                    styler_render_repr,
                    validator=is_one_of_factory(["html", "latex"]),
                )
            
                cf.register_option(
                    "render.max_elements",
                    2**18,
                    styler_max_elements,
                    validator=is_nonnegative_int,
                )
            
                cf.register_option(
                    "render.max_rows",
                    None,
                    styler_max_rows,
                    validator=is_nonnegative_int,
                )
            
                cf.register_option(
                    "render.max_columns",
                    None,
                    styler_max_columns,
                    validator=is_nonnegative_int,
                )
            
                cf.register_option("render.encoding", "utf-8", styler_encoding, validator=is_str)
            
                cf.register_option("format.decimal", ".", styler_decimal, validator=is_str)
            
                cf.register_option(
                    "format.precision", 6, styler_precision, validator=is_nonnegative_int
                )
            
                cf.register_option(
                    "format.thousands",
                    None,
                    styler_thousands,
                    validator=is_instance_factory([type(None), str]),
                )
            
                cf.register_option(
                    "format.na_rep",
                    None,
                    styler_na_rep,
                    validator=is_instance_factory([type(None), str]),
                )
            
                cf.register_option(
                    "format.escape",
                    None,
                    styler_escape,
                    validator=is_one_of_factory([None, "html", "latex", "latex-math"]),
                )
            
                cf.register_option(
                    "format.formatter",
                    None,
                    styler_formatter,
                    validator=is_instance_factory([type(None), dict, Callable, str]),
                )
            
                cf.register_option("html.mathjax", True, styler_mathjax, validator=is_bool)
            
                cf.register_option(
                    "latex.multirow_align",
                    "c",
                    styler_multirow_align,
                    validator=is_one_of_factory(["c", "t", "b", "naive"]),
                )
            
                val_mca = ["r", "|r|", "|r", "r|", "c", "|c|", "|c", "c|", "l", "|l|", "|l", "l|"]
                val_mca += ["naive-l", "naive-r"]
                cf.register_option(
                    "latex.multicol_align",
                    "r",
                    styler_multicol_align,
                    validator=is_one_of_factory(val_mca),
                )
            
                cf.register_option("latex.hrules", False, styler_hrules, validator=is_bool)
            
                cf.register_option(
                    "latex.environment",
                    None,
                    styler_environment,
                    validator=is_instance_factory([type(None), str]),
                )
            
            
            with cf.config_prefix("future"):
                cf.register_option(
                    "infer_string",
                    False,
                    "Whether to infer sequence of str objects as pyarrow string "
                    "dtype, which will be the default in pandas 3.0 "
                    "(at which point this option will be deprecated).",
                    validator=is_one_of_factory([True, False]),
                )
            
         
      
   

   
   

       # dtype
       ArrowDtype,
       Int8Dtype,
       Int16Dtype,
       Int32Dtype,
       Int64Dtype,
       UInt8Dtype,
       UInt16Dtype,
       UInt32Dtype,
       UInt64Dtype,
       Float32Dtype,
       Float64Dtype,
       CategoricalDtype,
       PeriodDtype,
       IntervalDtype,
       DatetimeTZDtype,
       StringDtype,
       BooleanDtype,
       # missing
       NA,
       isna,
       isnull,
       notna,
       notnull,
       # indexes
       Index,
       CategoricalIndex,
       RangeIndex,
       MultiIndex,
       IntervalIndex,
       TimedeltaIndex,
       DatetimeIndex,
       PeriodIndex,
       IndexSlice,
       # tseries
       NaT,
       Period,
       period_range,
       Timedelta,
       timedelta_range,
       Timestamp,
       date_range,
       bdate_range,
       Interval,
       interval_range,
       DateOffset,
       # conversion
       to_numeric,
       to_datetime,
       to_timedelta,
       # misc
       Flags,
       Grouper,
       factorize,
       unique,
       value_counts,
       NamedAgg,
       array,
       Categorical,
       set_eng_float_format,
       Series,
       DataFrame,
   )
   
   

   
   

   

   
   

   
   

       concat,
       lreshape,
       melt,
       wide_to_long,
       merge,
       merge_asof,
       merge_ordered,
       crosstab,
       pivot,
       pivot_table,
       get_dummies,
       from_dummies,
       cut,
       qcut,
   )
   
   

   

   

   
   

       # excel
       ExcelFile,
       ExcelWriter,
       read_excel,
       # parsers
       read_csv,
       read_fwf,
       read_table,
       # pickle
       read_pickle,
       to_pickle,
       # pytables
       HDFStore,
       read_hdf,
       # sql
       read_sql,
       read_sql_query,
       read_sql_table,
       # misc
       read_clipboard,
       read_parquet,
       read_orc,
       read_feather,
       read_gbq,
       read_html,
       read_xml,
       read_json,
       read_stata,
       read_sas,
       read_spss,
   )
   
   

   
   

   
   # use the closest tagged version if possible
   _built_with_meson = False
   try:
       

           __version__,
           __git_version__,
       )
   
       _built_with_meson = True
   except ImportError:
       

   
       v = get_versions()
       __version__ = v.get("closest-tag", v["version"])
       __git_version__ = v.get("full-revisionid")
       del get_versions, v
   
   
   # module level doc-string
   __doc__ = """
   pandas - a powerful data analysis and manipulation library for Python
   =====================================================================
   
   **pandas** is a Python package providing fast, flexible, and expressive data
   structures designed to make working with "relational" or "labeled" data both
   easy and intuitive. It aims to be the fundamental high-level building block for
   doing practical, **real world** data analysis in Python. Additionally, it has
   the broader goal of becoming **the most powerful and flexible open source data
   analysis / manipulation tool available in any language**. It is already well on
   its way toward this goal.
   
   Main Features
   -------------
   Here are just a few of the things that pandas does well:
   
     - Easy handling of missing data in floating point as well as non-floating
       point data.
     - Size mutability: columns can be inserted and deleted from DataFrame and
       higher dimensional objects
     - Automatic and explicit data alignment: objects can be explicitly aligned
       to a set of labels, or the user can simply ignore the labels and let
       `Series`, `DataFrame`, etc. automatically align the data for you in
       computations.
     - Powerful, flexible group by functionality to perform split-apply-combine
       operations on data sets, for both aggregating and transforming data.
     - Make it easy to convert ragged, differently-indexed data in other Python
       and NumPy data structures into DataFrame objects.
     - Intelligent label-based slicing, fancy indexing, and subsetting of large
       data sets.
     - Intuitive merging and joining data sets.
     - Flexible reshaping and pivoting of data sets.
     - Hierarchical labeling of axes (possible to have multiple labels per tick).
     - Robust IO tools for loading data from flat files (CSV and delimited),
       Excel files, databases, and saving/loading data from the ultrafast HDF5
       format.
     - Time series-specific functionality: date range generation and frequency
       conversion, moving window statistics, date shifting and lagging.
   """
   
   # Use __all__ to let type checkers know what is part of the public API.
   # Pandas is not (yet) a py.typed library: the public API is determined
   # based on the documentation.
   __all__ = [
       "ArrowDtype",
       "BooleanDtype",
       "Categorical",
       "CategoricalDtype",
       "CategoricalIndex",
       "DataFrame",
       "DateOffset",
       "DatetimeIndex",
       "DatetimeTZDtype",
       "ExcelFile",
       "ExcelWriter",
       "Flags",
       "Float32Dtype",
       "Float64Dtype",
       "Grouper",
       "HDFStore",
       "Index",
       "IndexSlice",
       "Int16Dtype",
       "Int32Dtype",
       "Int64Dtype",
       "Int8Dtype",
       "Interval",
       "IntervalDtype",
       "IntervalIndex",
       "MultiIndex",
       "NA",
       "NaT",
       "NamedAgg",
       "Period",
       "PeriodDtype",
       "PeriodIndex",
       "RangeIndex",
       "Series",
       "SparseDtype",
       "StringDtype",
       "Timedelta",
       "TimedeltaIndex",
       "Timestamp",
       "UInt16Dtype",
       "UInt32Dtype",
       "UInt64Dtype",
       "UInt8Dtype",
       "api",
       "array",
       "arrays",
       "bdate_range",
       "concat",
       "crosstab",
       "cut",
       "date_range",
       "describe_option",
       "errors",
       "eval",
       "factorize",
       "get_dummies",
       "from_dummies",
       "get_option",
       "infer_freq",
       "interval_range",
       "io",
       "isna",
       "isnull",
       "json_normalize",
       "lreshape",
       "melt",
       "merge",
       "merge_asof",
       "merge_ordered",
       "notna",
       "notnull",
       "offsets",
       "option_context",
       "options",
       "period_range",
       "pivot",
       "pivot_table",
       "plotting",
       "qcut",
       "read_clipboard",
       "read_csv",
       "read_excel",
       "read_feather",
       "read_fwf",
       "read_gbq",
       "read_hdf",
       "read_html",
       "read_json",
       "read_orc",
       "read_parquet",
       "read_pickle",
       "read_sas",
       "read_spss",
       "read_sql",
       "read_sql_query",
       "read_sql_table",
       "read_stata",
       "read_table",
       "read_xml",
       "reset_option",
       "set_eng_float_format",
       "set_option",
       "show_versions",
       "test",
       "testing",
       "timedelta_range",
       "to_datetime",
       "to_numeric",
       "to_pickle",
       "to_timedelta",
       "tseries",
       "unique",
       "value_counts",
       "wide_to_long",
   ]
   
pd = pandas



df = pd.DataFrame({'A': [1, 2, 3]})
print(df)
