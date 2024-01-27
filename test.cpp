#include <ctype.h>

#ifndef _LIBCPP_CTYPE_H
#error <cctype> tried including <ctype.h> but didn't find libc++'s <ctype.h> header. \
          This usually means that your header search paths are not configured properly.  \
          The header search paths should contain the C++ Standard Library headers before \
          any C Standard Library.
#endif
#include <string.h>
int main()
{
    char str1[] = "Hello";
    char str2[] = "World";
    char str3[20];
    strcpy(str3, str1);
    strcat(str3, str2);
    return 0;
}