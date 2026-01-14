import cmake_build_extension

with cmake_build_extension.build_extension_env():
    from .bindings import *
