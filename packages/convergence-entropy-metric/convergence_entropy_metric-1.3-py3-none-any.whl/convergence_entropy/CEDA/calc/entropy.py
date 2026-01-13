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

        logp = self.N.log_prob(1-C)

        return (-torch.exp(logp[:N[0]]) * logp[:N[0]]).sum(), (-torch.exp(logp[:N[1]]) * logp[:N[1]]).sum()

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

        p = 1 - self.N.cdf(1 - C)

        return (-torch.log(p[:N[0]]) * p[:N[0]]).sum(), (-torch.log(p[:N[1]]) * p[:N[1]]).sum()

class entropy_kern(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(entropy_kern, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()

        else:
            self.cos = nn.CosineSimilarity(dim=-1)

    def __kern(self, CoE):
        return torch.exp(- (CoE**2) / (2*(self.sigma**2)))

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

        p = self.__kern(1 - C)

        return (-torch.log(p[:N[0]]) * p[:N[0]]).sum(), (-torch.log(p[:N[1]]) * p[:N[1]]).sum()

#################################################################################

class information(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(information, self).__init__()

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

        logp = self.N.log_prob(1-C)

        return (-logp[:N[0]]).sum(), (-logp[:N[1]]).sum()

class information_cdf(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(information_cdf, self).__init__()

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

        p = 1 - self.N.cdf(1 - C)

        return (-torch.log(p[:N[0]])).sum(), (-torch.log(p[:N[1]])).sum()

class information_kern(nn.Module):

    def __init__(self, sigma=1., dim=None, device='cpu'):
        super(information_kern, self).__init__()

        self.sigma = sigma
        # self.dev = device
        self.dim = dim
        self.stream_n = 2

        if 'cuda' in device.lower():
            self.cos = nn.CosineSimilarity(dim=-1).cuda()

        else:
            self.cos = nn.CosineSimilarity(dim=-1)

    def __kern(self, CoE):
        return torch.exp(- (CoE**2) / (2*(self.sigma**2)))

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

        p = self.__kern(1 - C)

        return (-torch.log(p[:N[0]])).sum(), (-torch.log(p[:N[1]])).sum()
