cdef extern from "qqmusicdes.h":
    int qq_music_triple_des_decrypt(unsigned char *, unsigned char *, int)

# Now, create a Python-callable wrapper function.
# This is the function you will import and use in Python.
def decrypt_des(bytes buff, bytes key):
    cdef unsigned char * c_buff
    cdef unsigned char * c_key

    c_buff = buff
    c_key = key

    cdef int result = qq_music_triple_des_decrypt(c_buff, c_key, len(buff))

    return result
