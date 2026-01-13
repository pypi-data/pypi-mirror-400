from .entropy import just_cosines
from .end_to_end_analysis import analyzer
from .wv_model import wv
from .fastGraph import justCosinesFastGraph as FGA
import torch.nn as nn

class processor(nn.Module):

    def __init__(self, wv_model: str='roberta-base', wv_layers: list=[7,-1], device:str='cpu', checkpoint_location: str=None):
        super(processor, self).__init__()
        self.wv = wv(model=wv_model,layers=wv_layers,device=device)

        self.sim = just_cosines(device=device)

        self.GRAPH = FGA(
            analyzer(
                wv=self.wv,
                sim_model=self.sim,
                device=device
            ),
            iterated_checkpoint_dir=checkpoint_location
        )

    def fit(self,x, y):
        self.GRAPH.fit(x,y)

    def df(self):
        return self.GRAPH.df()