
#ifndef URX_PYTHON_EXPORT_H
#define URX_PYTHON_EXPORT_H

#ifdef URX_PYTHON_STATIC_DEFINE
#  define URX_PYTHON_EXPORT
#  define URX_PYTHON_NO_EXPORT
#else
#  ifndef URX_PYTHON_EXPORT
#    ifdef UrxPython_EXPORTS
        /* We are building this library */
#      define URX_PYTHON_EXPORT 
#    else
        /* We are using this library */
#      define URX_PYTHON_EXPORT 
#    endif
#  endif

#  ifndef URX_PYTHON_NO_EXPORT
#    define URX_PYTHON_NO_EXPORT 
#  endif
#endif

#ifndef URX_PYTHON_DEPRECATED
#  define URX_PYTHON_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef URX_PYTHON_DEPRECATED_EXPORT
#  define URX_PYTHON_DEPRECATED_EXPORT URX_PYTHON_EXPORT URX_PYTHON_DEPRECATED
#endif

#ifndef URX_PYTHON_DEPRECATED_NO_EXPORT
#  define URX_PYTHON_DEPRECATED_NO_EXPORT URX_PYTHON_NO_EXPORT URX_PYTHON_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef URX_PYTHON_NO_DEPRECATED
#    define URX_PYTHON_NO_DEPRECATED
#  endif
#endif

#endif /* URX_PYTHON_EXPORT_H */
