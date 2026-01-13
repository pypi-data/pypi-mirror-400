#include <stdio.h>
#include <stdlib.h>

typedef struct
{
    char *name;
    int begin;
    int end;
    int step;
    int precise;
    int times;
    int current;
    int lim0;
    int lim1;
    double current_f;
} element;
element *elements;
int size;
FILE *f;
int max;

void self_plus(int id)
{
    elements[id].current += elements[id].step;
    elements[id].current_f = 1.0 * elements[id].current / elements[id].times;
}

void minus(int id1, int id2)
{
    elements[id1].current -= elements[id2].current;
    elements[id1].current_f = 1.0 * elements[id1].current / elements[id1].times;
}

void getlim(int id)
{
    int max_sum = 0;
    int min_sum = 0;
    for (int i = 0; i < id; i++)
    {
        max_sum += elements[i].current;
        min_sum += elements[i].current;
    }
    for (int i = id + 1; i < size; i++)
    {
        max_sum += elements[i].end;
        min_sum += elements[i].begin;
    }
    elements[id].lim0 = max - max_sum;
    elements[id].lim1 = max - min_sum;
    if (elements[id].lim0 < elements[id].begin)
    {
        elements[id].lim0 = elements[id].begin;
    }
    if (elements[id].lim1 > elements[id].end)
    {
        elements[id].lim1 = elements[id].end;
    }
}

void file_write()
{
    elements[size - 1].current = max;
    int i;
    for (i = 0; i < size - 1; i++)
    {
        elements[size - 1].current -= elements[i].current;
    }
    for (i = 0; i < size; i++)
    {
        if ((elements[i].current - elements[i].begin) % elements[i].step)
        {
            return;
        }
    }
    elements[size - 1].current_f = 1.0 * elements[size - 1].current / elements[size - 1].times;
    for (i = 0; i < size; i++)
    {
        fprintf(f, "%.*f,", elements[i].precise, elements[i].current_f);
    }
    // elements[size - 1].current_f = 1.0 * elements[size - 1].current / elements[size - 1].times;
    // fprintf(f, "%.*f,", elements[i].precise, elements[i].current_f);
    for (i = 0; i < size; i++)
    {
        fputs(elements[i].name, f);
        fprintf(f, "%.*f", elements[i].precise, elements[i].current_f);
    }
    fputc('\n', f);
}

void combination(int id)
{
    getlim(id);
    int lim0 = elements[id].lim0, lim1 = elements[id].lim1;
    if (id == size - 2)
    {
        for (elements[id].current = lim0; elements[id].current <= lim1; elements[id].current += elements[id].step)
        {
            elements[id].current_f = 1.0 * elements[id].current / elements[id].times;
            file_write();
        }
        return;
    }
    for (elements[id].current = lim0; elements[id].current <= lim1; elements[id].current += elements[id].step)
    {
        elements[id].current_f = 1.0 * elements[id].current / elements[id].times;
        combination(id + 1);
    }
}

void comb_input(char *file_name, element *elements_input, int size_in, int max_in)
{
    elements = elements_input;
    char *fname = file_name;
    size = size_in;
    max = max_in;
    f = fopen(fname, "w");
    for (int i = 0; i < size; i++)
    {
        fprintf(f, "%s,", elements[i].name);
    }
    fputs("Alloy\n", f);
    combination(0);
    fclose(f);
}