import pandas as pd
import numpy as np
import AlloyFrame as af

def weighted_mean(searching_space:pd.DataFrame,
                  elements_properties:pd.DataFrame,
                  )->pd.DataFrame:
    '''计算加权点乘'''
    return elements_properties.dot(searching_space)/searching_space.sum()

def weighted_variance(searching_space:pd.DataFrame,
                      elements_properties:pd.DataFrame,
                      mean:pd.DataFrame=None,
                      )->pd.DataFrame:
    '''计算加权方差'''
    elements_properties_square=elements_properties**2
    E_X_2=elements_properties_square.dot(searching_space)/searching_space.sum()
    if mean is None:
        mean=weighted_mean(searching_space,elements_properties)
    return E_X_2-mean**2

def weighted_harmonic(searching_space:pd.DataFrame,elements_properties:pd.DataFrame)->pd.DataFrame:
    '''计算调和平均数'''
    elements_properties_Reciprocal=1/elements_properties
    is_na_or_inf=np.isinf(elements_properties_Reciprocal)
    elements_properties_Reciprocal.replace([np.inf,-np.inf],0,inplace=True)
    property_variance_harmonic_mean=elements_properties_Reciprocal.dot(searching_space)
    property_variance_harmonic_mean
    df=pd.DataFrame(np.where(is_na_or_inf,0,1),index=elements_properties_Reciprocal.index,columns=elements_properties_Reciprocal.columns).T

    searching_space_sum=searching_space.T.dot(df).T
    return searching_space_sum / property_variance_harmonic_mean

def get_phase_energy(df_phase_energy:pd.DataFrame,searching_space:pd.DataFrame)->pd.DataFrame:
    columns=list(df_phase_energy.columns)
    columns[0]="Element"
    df_phase_energy.columns=columns
    df_phase_energy=df_phase_energy.set_index(df_phase_energy.columns[0])

    for i,e1 in enumerate(df_phase_energy.columns):
        for e2 in df_phase_energy.columns[:i]:
            df_phase_energy[e1][e2]=df_phase_energy[e2][e1]
    df_phase_energy=df_phase_energy[searching_space.index]
    df_phase_energy=df_phase_energy.T[searching_space.index]
    diagonal =df_phase_energy.values.diagonal()
    df_phase_energy_diff=df_phase_energy.sub(diagonal,axis=0)
    index=[i+"_phase_energy" for i in df_phase_energy_diff.index]
    df_phase_energy_diff.index=index
    return df_phase_energy_diff


class WeightProperty:
    def __init__(self,
                 searching_space_file:str=None,
                 elements_properties_file:str=None,
                 searching_space:pd.DataFrame=None,
                 elements_properties:pd.DataFrame=None,
                 element_fraction:pd.DataFrame=None,
                 composition_column:str=None,
                 ) -> None:
        if elements_properties is None:
            elements_properties = pd.read_csv(elements_properties_file)
        
        if element_fraction is None:
            if searching_space is None:
                searching_space=pd.read_csv(searching_space_file)
                searching_space.set_index(searching_space.columns[0])
            
            searching_space=af.add_element_fraction(searching_space[composition_column],source_column=composition_column)
            self.searching_space=searching_space[searching_space.columns[-1]].T
        else:
            self.searching_space=element_fraction.T
        self.elements_properties=(elements_properties.T)[self.searching_space.index]

    @property
    def weighted_mean(self)->pd.DataFrame:
        df = weighted_mean(searching_space=self.searching_space,elements_properties=self.elements_properties)
        df.index=([i+"_mean" for i in df.index])
        return df
    
    @property
    def weighted_variance(self)->pd.DataFrame:
        df = weighted_variance(searching_space=self.searching_space,elements_properties=self.elements_properties)
        df.index=([i+"_variance" for i in df.index])
        return df
    
    @property
    def weighted_harmonic(self)->pd.DataFrame:
        df = weighted_harmonic(searching_space=self.searching_space,elements_properties=self.elements_properties)
        df.index=([i+"_harmonic" for i in df.index])
        return df
    

class PhaseEnergy:
    def __init__(self,
                 searching_space_file:str=None,
                 phase_energy_file:str=None,
                 searching_space:pd.DataFrame=None,
                 phase_energy:pd.DataFrame=None,
                 element_fraction:pd.DataFrame=None,
                 composition_column:str=None,
                 ) -> None:
        
        if phase_energy is None:
            phase_energy=pd.read_csv(phase_energy_file)
            
        if element_fraction is None:
            if searching_space is None:
                searching_space=pd.read_csv(searching_space_file)
                searching_space.set_index(searching_space.columns[0])
            
            searching_space=af.add_element_fraction(searching_space[composition_column],source_column=composition_column)
            self.searching_space=searching_space[searching_space.columns[-1]].T
        else:
            self.searching_space=element_fraction.T

        self.phase_energy=get_phase_energy(phase_energy,self.searching_space)
    
    @property
    def phase_energy_mean(self)->pd.DataFrame:
        df=weighted_mean(searching_space=self.searching_space,elements_properties=self.phase_energy)
        df.index=([i+"phase_energy_mean" for i in df.index])
        return df
        
    
    @property
    def phase_energy_variance(self)->pd.DataFrame:
        df=weighted_variance(searching_space=self.searching_space,elements_properties=self.phase_energy)
        df.index=([i+"phase_energy_variance" for i in df.index])
        return df
        
    
    @property
    def phase_energy_harmonic(self)->pd.DataFrame:
        df=weighted_harmonic(searching_space=self.searching_space,elements_properties=self.phase_energy)
        df.index=([i+"phase_energy_harmonic" for i in df.index])
        return df
        