import torch
import torch.nn as nn

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from itertools import combinations, product
from datetime import datetime as dt

from sklearn.linear_model import Ridge as LREG

################################################################################
### Fast Graph for only just_cosines string CoS outputs
################################################################################
class justCosinesFastGraph(nn.Module):

    def __init__(self, analyzer_object: object, timed: bool=False, iterated_checkpoint_dir:str=''):
        super(justCosinesFastGraph, self).__init__()

        self.analyzer = analyzer_object
        self.analyzer.dim = None

        self.M, self.N, self.beta = [], [], None
        self.save_k = 100000
        self.ckpt_loc = iterated_checkpoint_dir
        if self.ckpt_loc:
            if not os.path.exists(iterated_checkpoint_dir):
                os.mkdir(iterated_checkpoint_dir)
        self.timed = timed

        self.id_dic = None
        self._square = False

    def __ckpt_fit(self, x: list, y: list):

        for (i, (x_, y_)) in enumerate(tqdm(list(zip(x, y)))):
            H, N = self.analyzer(x_, y_)
            self.M += [{'nx': N[0], 'ny': N[1], 'CoS': str(H.detach().cpu().tolist())}]

            if ((i+1) % self.save_k) == 0:
                pd.DataFrame(self.M).to_parquet(
                    os.path.join(self.ckpt_loc, 'ckpt-' + str(i) + '.parquet'),
                    engine='fastparquet',
                    compression='snappy'
                )

                self.M = []

        if len(self.M):
            pd.DataFrame(self.M).to_parquet(
                os.path.join(self.ckpt_loc, 'ckpt-' + str(i) + '.parquet'),
                engine='fastparquet',
                compression='snappy'
            )

    def __nockpt_fit(self, x: list, y: list):

        for (i, (x_, y_)) in enumerate(tqdm(list(zip(x,y)))):
            H, N = self.analyzer(x_, y_)
            self.M += [{'nx': N[0], 'ny': N[1], 'CoS': str(H.detach().cpu().tolist())}]

    def fit(self, x: list, y: list):
        if self.ckpt_loc:
            self.__ckpt_fit(x,y)
        else:
            self.__nockpt_fit(x,y)

    def df(self):
        return pd.DataFrame(self.M)