import torch
import numpy as np
import torch.nn as nn

class just_cosines(nn.Module):

    def __init__(self, sigma=1, device='cpu'):
        super(just_cosines, self).__init__()

        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()

        else:
            self.cos = nn.CosineSimilarity(dim=-1)

    def __stream_cos_one_sided(self, ex, ey):

        spans = int(len(ex) / self.stream_n)

        starts = [i * self.stream_n for i in range(spans)] + [spans * self.stream_n]
        ends = [(i + 1) * self.stream_n for i in range(spans)] + [len(ex)]
        steps = list(zip(starts, ends))

        cosM = self.cos(ex[steps[0][0]:steps[0][1]].unsqueeze(1), ey).max(dim=-1).values.view(-1)
        for start, end in steps[1:]:
            if start != len(ex):
                cosM = torch.cat([
                    cosM,
                    self.cos(ex[start:end].unsqueeze(1), ey).max(dim=-1).values.view(-1)
                ], dim=-1)

        return cosM

    def one_sided(self, ex, ey):
        dim = np.argmax([len(ex), len(ey)])

        try:
            C = self.cos(ex.unsqueeze(1), ey).max(dim=dim).values

        except Exception:
            if dim == 0:
                C = self.__stream_cos_one_sided(ex,ey)
            else:
                C = self.__stream_cos_one_sided(ey,ex)

        return C

    def forward(self, ex, ey):
        return self.one_sided(ex, ey)
