import pandas as pd
import numpy as np
import tqdm
from functools import reduce

from AlloyFrame.LoadFrame import concat
from pymatgen.core.composition import Composition, Element
import re

pattern_fraction = re.compile('[0-9,.]+')
pattern_atoms = re.compile('[A-Z,a-z]+')

element_names = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K",
    "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb",
    "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs",
    "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta",
    "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa",
    "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", 'Lr'
]
element_num = len(element_names)


def add_element_fraction(df, source_column='composition'):
    process = tqdm.tqdm(total=df.shape[0], desc="Adding element fraction: ")
    for i in df[source_column]:
        test_composition = i
        break
    if isinstance(test_composition, Composition):
        element_names_e = [Element(i) for i in element_names]
        element_names_d = dict(zip(element_names_e, [i for i in range(element_num)]))

        def com2ele(comp):
            ele = np.zeros(element_num, dtype=np.float64)
            comp = comp[0]
            for atom in comp:
                ele[element_names_d[atom]] = comp[atom]
            process.update(1)
            return ele

        v_com2ele = np.vectorize(com2ele, signature='(n)->(k)')
        composition = pd.DataFrame(df[source_column])
        ele_fraction = v_com2ele(composition)
    elif isinstance(test_composition, str):
        element_names_d = dict(zip(element_names, [i for i in range(element_num)]))

        def str2ele(string):
            ele = np.zeros(element_num, dtype=np.float64)
            atoms = pattern_atoms.findall(string[0])
            fractions = pattern_fraction.findall(string[0])
            for i, atom in enumerate(atoms):
                ele[element_names_d[atom]] = fractions[i]
            process.update(1)
            return ele

        v_str2ele = np.vectorize(str2ele, signature='(n)->(k)')
        composition = pd.DataFrame(df[source_column])
        ele_fraction = v_str2ele(composition)
    else:
        raise TypeError(f"""Only support type of 'str' or 'pymatgen.core.composition.Composition'. 
        While Column {source_column} is type of {type(df[source_column][0])}""")
    output = pd.DataFrame(ele_fraction, columns=element_names)
    process.close()
    return concat([df, output], axis=1)


def element_fraction(data_frame: pd.DataFrame, source_column) -> pd.DataFrame:
    columns = {}
    print(data_frame)
    print(data_frame[source_column])
    for e in element_names:
        series = data_frame[source_column].str.extract(f"{e}(\d+(\.\d+)?)")
        series = series[0]
        series = pd.to_numeric(series, errors='coerce')
        columns[e] = series.fillna(0)
    out_df = pd.DataFrame(columns)
    return out_df


def str2composition(data_frame: pd.DataFrame, source_column, target_column):
    data_frame[target_column] = data_frame[source_column].apply(Composition)


def at2wt(data_frame: pd.DataFrame, source_column, target_column=None):
    at_fraction = element_fraction(data_frame, source_column)
    # 找到所有全为0的列
    zero_columns = at_fraction.columns[at_fraction.eq(0).all()]
    # 使用布尔索引去掉这些列
    at_fraction = at_fraction.loc[:, ~at_fraction.columns.isin(zero_columns)]
    atomic_mass = pd.Series(dict([(atom, Element(atom).atomic_mass) for atom in at_fraction.columns]))

    wt_fraction: pd.DataFrame = at_fraction * atomic_mass
    # 计算每行的总和
    row_sums = wt_fraction.sum(axis=1) / 100
    # 对每个元素进行归100化处理
    normalized100_df: pd.DataFrame = wt_fraction.div(row_sums, axis=0)
    str_df = normalized100_df.astype(str)

    out_series = reduce(lambda a, b: a + b + str_df[b], str_df.columns, "")
    data_frame[target_column] = out_series


def wt2at(data_frame: pd.DataFrame, source_column, target_column=None):
    at_fraction = element_fraction(data_frame, source_column)
    # 找到所有全为0的列
    zero_columns = at_fraction.columns[at_fraction.eq(0).all()]
    # 使用布尔索引去掉这些列
    at_fraction = at_fraction.loc[:, ~at_fraction.columns.isin(zero_columns)]
    atomic_mass = pd.Series(dict([(atom, Element(atom).atomic_mass) for atom in at_fraction.columns]))

    wt_fraction: pd.DataFrame = at_fraction.div(atomic_mass, axis=1)
    # 计算每行的总和
    row_sums = wt_fraction.sum(axis=1) / 100
    # 对每个元素进行归100化处理
    normalized100_df: pd.DataFrame = wt_fraction.div(row_sums, axis=0)
    str_df = normalized100_df.astype(str)

    out_series = reduce(lambda a, b: a + b + str_df[b], str_df.columns, "")
    data_frame[target_column] = out_series


if __name__ == "__main__":
    df = pd.DataFrame({"com": ["Al1.5Cu2Mg2", "Al2Cu3Zr2.5"]})
    print(element_fraction(df, "com"))
    print(element_fraction(df, "com")["Al"])
    at2wt(df, source_column="com", target_column="test")
    wt2at(df, source_column="test", target_column="test1")
    print(df)
