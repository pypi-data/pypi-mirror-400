import numpy
import pandas as pd
import numpy as np
import tqdm
from pymatgen.core.composition import Composition
from pymatgen.core import Element
import re
from functools import reduce
from periodictable import elements


class DataFrame(pd.DataFrame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def str2composition(self, source_column='Alloy', target_column='composition'):
        process = tqdm.tqdm(total=self.shape[0], desc="str to composition")
        if source_column not in self.columns:
            raise ValueError(f"source_column: '{source_column}' doesn't exist.")
        if target_column in self.columns:
            raise ValueError(f"target_column: '{target_column}' already exists.")
        self[target_column] = self[source_column].apply(lambda x: (Composition(x), process.update(1))[0])
        process.close()

    def wt2at(self, source_column, target_column='Alloy', precise=2):
        if source_column not in self.columns:
            raise ValueError(f"source_column: '{source_column}' doesn't exist.")
        if target_column in self.columns:
            raise ValueError(f"target_column: '{target_column}' already exists.")
        pattern_masses = re.compile('[0-9,.]+')
        pattern_atoms = re.compile('[A-Z,a-z]+')
        process = tqdm.tqdm(total=self.shape[0], desc="wt to at: ")

        def mass2atom_s(string):
            masses = np.array(pattern_masses.findall(string), dtype=np.float64)
            atoms = pattern_atoms.findall(string)
            atomic_masses = numpy.array([Element(atom).atomic_mass for atom in atoms])
            proportion = masses / atomic_masses
            proportion = 100 * proportion / proportion.sum()
            process.update(1)
            return reduce(lambda x, y: x + f'{y[0]}{y[1]:.{precise}f}', zip(atoms, proportion), '')

        self[target_column] = self[source_column].apply(mass2atom_s)
        process.close()

    def at2wt(self, source_column, target_column='Alloy', precise=2):
        if source_column not in self.columns:
            raise ValueError(f"source_column: '{source_column}' doesn't exist.")
        if target_column in self.columns:
            raise ValueError(f"target_column: '{target_column}' already exists.")
        pattern_masses = re.compile('[0-9,.]+')
        pattern_atoms = re.compile('[A-Z,a-z]+')
        process = tqdm.tqdm(total=self.shape[0], desc="at to wt: ")

        def atom2mass_s(string):
            fractions = numpy.array(pattern_masses.findall(string), dtype=np.float64)
            atoms = pattern_atoms.findall(string)
            atomic_masses = numpy.array([Element(atom).atomic_mass for atom in atoms])
            masses = fractions * atomic_masses
            masses = 100 * masses / masses.sum()
            process.update(1)
            return reduce(lambda x, y: x + f'{y[0]}{y[1]:.{precise}f}', zip(atoms, masses), '')

        self[target_column] = self[source_column].apply(atom2mass_s)
        process.close()

    def add_density(self, source_column="composition", target_column='density'):
        process = tqdm.tqdm(total=self.shape[0], desc="adding density")

        def get_density(composition):
            c = np.array([composition[i] for i in composition])
            a = np.array([i.atomic_mass for i in composition])
            rho = np.array([elements.symbol(i.name).density for i in composition])
            process.update(1)
            return (c * a).sum() / (c * a / rho).sum()

        self[target_column] = self[source_column].apply(get_density)
        process.close()

    def af_copy(self, *args, **kwargs):
        df = super().copy(*args, **kwargs)
        return DataFrame(df)

    def __getitem__(self, item):
        df = super().__getitem__(item)
        if len(df.shape) == 1:
            return df
        return DataFrame(df)

    @property
    def pd_dataframe(self):
        return super().__getitem__(slice(None, None, None))
