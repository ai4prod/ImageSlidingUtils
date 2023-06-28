
#ifndef IMAGESLIDING_EXPORT_H
#define IMAGESLIDING_EXPORT_H

#ifdef IMAGESLIDING_STATIC_DEFINE
#  define IMAGESLIDING_EXPORT
#  define IMAGESLIDING_NO_EXPORT
#else
#  ifndef IMAGESLIDING_EXPORT
#    ifdef imagesliding_EXPORTS
        /* We are building this library */
#      define IMAGESLIDING_EXPORT __declspec(dllexport)
#    else
        /* We are using this library */
#      define IMAGESLIDING_EXPORT __declspec(dllimport)
#    endif
#  endif

#  ifndef IMAGESLIDING_NO_EXPORT
#    define IMAGESLIDING_NO_EXPORT 
#  endif
#endif

#ifndef IMAGESLIDING_DEPRECATED
#  define IMAGESLIDING_DEPRECATED __declspec(deprecated)
#endif

#ifndef IMAGESLIDING_DEPRECATED_EXPORT
#  define IMAGESLIDING_DEPRECATED_EXPORT IMAGESLIDING_EXPORT IMAGESLIDING_DEPRECATED
#endif

#ifndef IMAGESLIDING_DEPRECATED_NO_EXPORT
#  define IMAGESLIDING_DEPRECATED_NO_EXPORT IMAGESLIDING_NO_EXPORT IMAGESLIDING_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef IMAGESLIDING_NO_DEPRECATED
#    define IMAGESLIDING_NO_DEPRECATED
#  endif
#endif

#endif /* IMAGESLIDING_EXPORT_H */
