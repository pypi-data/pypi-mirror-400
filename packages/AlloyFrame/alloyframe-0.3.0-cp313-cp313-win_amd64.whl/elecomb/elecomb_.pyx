# cython:language_level=3
# distutils: language = c++
cimport cython
# cimport numpy as npc
# import numpy as np
from libc.stdlib cimport malloc, free

cdef extern from "elecomb_i.c":
    ctypedef struct element:
        char *name
        int begin
        int end
        int step
        int precise
        int times
        int current
        int lim0
        int lim1
        float current_f

cdef struct element_p:
    char *name
    int begin
    int end
    int step
    int precise
    int times
    int current
    int lim0
    int lim1
    float current_f

cdef extern from "elecomb_i.c":
    ctypedef struct element
    void comb_input(char *file_name, element *elements_input, int size_in, int max_in)

def input(file_name, elements_input, max_in):
    cdef element_p *elements
    cdef int size = len(elements_input)
    cdef char *fname = file_name
    elements = <element_p *> malloc(size * sizeof(element_p))
    cdef int i = 0
    for i in range(size):
        elements[i] = element_p(elements_input[i][0],
                                elements_input[i][1],
                                elements_input[i][2],
                                elements_input[i][3],
                                elements_input[i][4],
                                elements_input[i][5],
                                0,
                                0,
                                100,
                                0)

        i += 1

    comb_input(fname, <element *> elements, size, max_in)
    free(elements)
