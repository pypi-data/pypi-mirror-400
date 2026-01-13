import pandas as pd
import numpy as np
from tqdm import tqdm
from AlloyFrame.LoadFrame import concat


class MultipleFeaturizer:
    def __init__(self, *model_in):
        self.models = model_in

    def __call__(self, compositions=None, DataFrame=None, col_id=None):
        return self.featurize(compositions, DataFrame, col_id)

    def featurize(self, compositions=None, DataFrame=None, col_id=None):
        def model_featurize(comp):
            features = model.featurize(comp[0])
            process.update(1)
            return np.array(features)

        if DataFrame is not None:
            compositions = DataFrame[col_id]
        output_frames = []
        for i, model in enumerate(self.models):
            process = tqdm(total=compositions.shape[0], desc=f"Featuring Model {i}")
            v_featurize = np.vectorize(model_featurize, signature='(n)->(k)')
            output = v_featurize(pd.DataFrame(compositions))
            output_frames.append(pd.DataFrame(output, columns=model.feature_labels()))
            process.close()

        return concat(output_frames, axis=1)
