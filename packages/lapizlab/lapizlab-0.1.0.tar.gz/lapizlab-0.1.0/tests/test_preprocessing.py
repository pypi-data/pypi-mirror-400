from lapizlab.preprocessing import TabularPreProcessor
import numpy as np
import pandas as pd

def test_TabularPP_1():
    df = pd.DataFrame([[12, 32423, 234234, np.NaN], 
                    [np.NaN, np.NaN, 2, 5], 
                    [np.NaN, 22, np.NaN, np.NaN]])
    pp = TabularPreProcessor()
    pp.set_df(df)
    pp.drop_missings(thr=1, axis=1)
    assert len(pp.return_df())