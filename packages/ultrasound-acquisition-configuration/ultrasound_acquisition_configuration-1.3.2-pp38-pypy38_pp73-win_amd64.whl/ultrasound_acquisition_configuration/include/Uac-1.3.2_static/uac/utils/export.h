
#ifndef UAC_UTILS_EXPORT_H
#define UAC_UTILS_EXPORT_H

#ifdef UAC_UTILS_STATIC_DEFINE
#  define UAC_UTILS_EXPORT
#  define UAC_UTILS_NO_EXPORT
#else
#  ifndef UAC_UTILS_EXPORT
#    ifdef UacUtils_EXPORTS
        /* We are building this library */
#      define UAC_UTILS_EXPORT 
#    else
        /* We are using this library */
#      define UAC_UTILS_EXPORT 
#    endif
#  endif

#  ifndef UAC_UTILS_NO_EXPORT
#    define UAC_UTILS_NO_EXPORT 
#  endif
#endif

#ifndef UAC_UTILS_DEPRECATED
#  define UAC_UTILS_DEPRECATED __declspec(deprecated)
#endif

#ifndef UAC_UTILS_DEPRECATED_EXPORT
#  define UAC_UTILS_DEPRECATED_EXPORT UAC_UTILS_EXPORT UAC_UTILS_DEPRECATED
#endif

#ifndef UAC_UTILS_DEPRECATED_NO_EXPORT
#  define UAC_UTILS_DEPRECATED_NO_EXPORT UAC_UTILS_NO_EXPORT UAC_UTILS_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef UAC_UTILS_NO_DEPRECATED
#    define UAC_UTILS_NO_DEPRECATED
#  endif
#endif

#endif /* UAC_UTILS_EXPORT_H */
