
#ifndef URX_UTILS_EXPORT_H
#define URX_UTILS_EXPORT_H

#ifdef URX_UTILS_STATIC_DEFINE
#  define URX_UTILS_EXPORT
#  define URX_UTILS_NO_EXPORT
#else
#  ifndef URX_UTILS_EXPORT
#    ifdef UrxUtils_EXPORTS
        /* We are building this library */
#      define URX_UTILS_EXPORT 
#    else
        /* We are using this library */
#      define URX_UTILS_EXPORT 
#    endif
#  endif

#  ifndef URX_UTILS_NO_EXPORT
#    define URX_UTILS_NO_EXPORT 
#  endif
#endif

#ifndef URX_UTILS_DEPRECATED
#  define URX_UTILS_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef URX_UTILS_DEPRECATED_EXPORT
#  define URX_UTILS_DEPRECATED_EXPORT URX_UTILS_EXPORT URX_UTILS_DEPRECATED
#endif

#ifndef URX_UTILS_DEPRECATED_NO_EXPORT
#  define URX_UTILS_DEPRECATED_NO_EXPORT URX_UTILS_NO_EXPORT URX_UTILS_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef URX_UTILS_NO_DEPRECATED
#    define URX_UTILS_NO_DEPRECATED
#  endif
#endif

#endif /* URX_UTILS_EXPORT_H */
