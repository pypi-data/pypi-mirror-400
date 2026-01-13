from elecomb import elecomb_
import copy
import os


def elecomb(element_data, filename=None, precise=None):
    """
    Parament element_data is the shape as [[element1, start, end, step],[element2, start, end, step], ...].
    Such as [["Al", 10, 50, 1], ["Mg", 10, 80, 0.1], ["Fe", 10, 50, 0.12]].
    Parament precise indicates the decimal places.
    Such as precise = [0, 1, 2] for element_data = [["Al", 10, 50, 1], ["Mg", 10, 80, 0.1], ["Fe", 10, 50, 0.15]]
    """
    element_input = copy.deepcopy(element_data)
    if filename is None:
        filename = ""
        for i, item in enumerate(element_input):
            filename += item[0]
        filename += ".csv"
    if path := os.path.split(filename)[0]:
        if not os.path.exists(path):
            raise ValueError(f"{path} not exists")
    filename = filename.encode("utf-8")
    for i, item in enumerate(element_input):
        element_input[i][0] = element_input[i][0].encode("utf-8")
    max_input = 100
    if precise is None:
        for i, item in enumerate(element_input):
            j = 0
            while True:
                if element_input[i][3] * 10 ** j > 0.9:
                    element_input[i].append(j)
                    break
                j += 1
            max_i = 100 * 10 ** element_input[i][4]
            max_input = max(max_input, max_i)
    else:
        if isinstance(precise, list):
            if len(precise) == len(element_input):
                for i, _ in enumerate(element_input):
                    element_input[i].append(precise[i])
                    max_i = 100 * 10 ** element_input[i][4]
                    max_input = max(max_input, max_i)
            else:
                raise ValueError("len(precise) is not equal to len(element_data)")
        else:
            raise TypeError(f"precise must be a list, not a {type(precise)}.")
    for i, item in enumerate(element_input):
        element_input[i].append(int(max_input / 100))
        element_input[i][3] = int(element_input[i][3] * element_input[i][-1])
        element_input[i][1] *= element_input[i][-1]
        element_input[i][2] *= element_input[i][-1]
    elecomb_.input(file_name=filename, elements_input=element_input, max_in=max_input)
