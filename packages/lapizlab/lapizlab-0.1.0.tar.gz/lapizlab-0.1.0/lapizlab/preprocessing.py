#Import requires
import numpy as np
import pandas as pd

#Tabular datasets preprocessors
class TabularPreProcessor:
    def set_df(self, df):
        self.df = df
    def drop_missings(self, thr=0, axis=0):
        if thr > 0:
            self.df.dropna(thresh=thr, axis=axis, inplace=True)
        else:
            self.df.dropna(axis=axis, inplace=True)
    def return_df(self):
        return self.df

    