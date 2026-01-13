import torch
import numpy as np
import torch.nn as nn

class entropy(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(entropy, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]).cuda(), validate_args=False)

        else:
            self.cos = nn.CosineSimilarity(dim=-1)
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]), validate_args=False)


    def __stream_cos(self, ex, ey):

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

    def forward(self, ex, ey):
        N = [len(ex), len(ey)]
        dim = np.argmax(N)

        try:
            C = self.cos(ex.unsqueeze(1), ey).max(dim=dim).values

        except Exception:
            if dim == 0:
                C = self.__stream_cos_one_sided(ex,ey).max(dim=0).values
            else:
                C = self.__stream_cos_one_sided(ey, ex).max(dim=0).values

        x, y = 1-(C[:N[0]]), 1-(C[:N[1]])
        x, y = self.N.log_prob(x), self.N.log_prob(y)

        return (-torch.exp(x) * x).sum(), (-torch.exp(y) * y).sum()


class entropy_cdf(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(entropy_cdf, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]).cuda(), validate_args=False)

        else:
            self.cos = nn.CosineSimilarity(dim=-1)
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]), validate_args=False)

    def __stream_cos(self, ex, ey):

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

    def forward(self, ex, ey):
        N = [len(ex), len(ey)]
        dim = np.argmax(N)

        try:
            C = self.cos(ex.unsqueeze(1), ey).max(dim=dim).values

        except Exception:
            if dim == 0:
                C = self.__stream_cos_one_sided(ex, ey).max(dim=0).values
            else:
                C = self.__stream_cos_one_sided(ey, ex).max(dim=0).values

        x, y = 1 - (C[:N[0]]), 1 - (C[:N[1]])
        x, y = 1 - self.N.cdf(x), 1 - self.N.cdf(y)

        return (-torch.log(x) * x).sum(), (-torch.log(y) * y).sum()

#################################################################################

class I(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(I, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]).cuda(), validate_args=False)

        else:
            self.cos = nn.CosineSimilarity(dim=-1)
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]), validate_args=False)

    def __stream_cos(self, ex, ey):

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

    def forward(self, ex, ey):
        N = [len(ex), len(ey)]
        dim = np.argmax(N)

        try:
            C = self.cos(ex.unsqueeze(1), ey).max(dim=dim).values

        except Exception:
            if dim == 0:
                C = self.__stream_cos_one_sided(ex, ey).max(dim=0).values
            else:
                C = self.__stream_cos_one_sided(ey, ex).max(dim=0).values

        x, y = 1 - (C[:N[0]]), 1 - (C[:N[1]])
        x, y = self.N.log_prob(x), self.N.log_prob(y)

        return (-x).sum(), (-y).sum()


class I_cdf(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(I_cdf, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]).cuda(), validate_args=False)

        else:
            self.cos = nn.CosineSimilarity(dim=-1)
            self.N = torch.distributions.HalfNormal(scale=torch.FloatTensor([sigma]), validate_args=False)

    def __stream_cos(self, ex, ey):

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

    def forward(self, ex, ey):
        N = [len(ex), len(ey)]
        dim = np.argmax(N)

        try:
            C = self.cos(ex.unsqueeze(1), ey).max(dim=dim).values

        except Exception:
            if dim == 0:
                C = self.__stream_cos_one_sided(ex, ey).max(dim=0).values
            else:
                C = self.__stream_cos_one_sided(ey, ex).max(dim=0).values

        x, y = 1 - (C[:N[0]]), 1 - (C[:N[1]])
        x, y = 1 - self.N.cdf(x), 1 - self.N.cdf(y)

        return (-torch.log(x)).sum(), (-torch.log(y)).sum()