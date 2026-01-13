import torch
from torch import nn


class SphereMotionCNN(nn.Module):
    """
    1D CNN over joints to predict next-frame joint positions.
    Input shape: (batch, joints, 3)
    Output shape: (batch, joints, 3)
    """

    def __init__(
        self,
        hidden: int = 64,
        layers: int = 3,
        kernel_size: int = 3,
        dropout: float = 0.0,
    ):
        super().__init__()
        padding = kernel_size // 2

        convs = []
        in_ch = 3
        for i in range(layers):
            out_ch = hidden
            convs.append(
                nn.Sequential(
                    nn.Conv1d(in_ch, out_ch, kernel_size, padding=padding),
                    nn.ReLU(inplace=True),
                    nn.Dropout(dropout),
                )
            )
            in_ch = out_ch
        self.convs = nn.ModuleList(convs)
        self.head = nn.Conv1d(in_ch, 3, kernel_size, padding=padding)

    def forward(self, x):
        # x: (B, joints, 3) -> (B, 3, joints)
        x = x.transpose(1, 2)
        for block in self.convs:
            x = block(x)
        out = self.head(x)
        # back to (B, joints, 3)
        return out.transpose(1, 2)


class SphereUNet1D(nn.Module):
    """
    Lightweight 1D U-Net over joints to predict next-frame joint positions.
    Input: (B, J, 3) -> output (B, J, 3)
    """

    def __init__(self, base: int = 32, dropout: float = 0.0):
        super().__init__()
        self.enc1 = nn.Sequential(
            nn.Conv1d(3, base, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.enc2 = nn.Sequential(
            nn.Conv1d(base, base * 2, 3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.mid = nn.Sequential(
            nn.Conv1d(base * 2, base * 4, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.dec1 = nn.Sequential(
            nn.ConvTranspose1d(base * 4, base * 2, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.dec2 = nn.Sequential(
            nn.Conv1d(base * 4, base, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.head = nn.Conv1d(base, 3, 3, padding=1)

    def forward(self, x):
        # x: (B, J, 3) -> (B, 3, J)
        x = x.transpose(1, 2)
        e1 = self.enc1(x)
        e2 = self.enc2(e1)
        m = self.mid(e2)
        d1 = self.dec1(m)
        d1_cat = torch.cat([d1, e2], dim=1)
        d2 = self.dec2(d1_cat)
        out = self.head(d2 + e1[:, : d2.size(2)])
        return out.transpose(1, 2)
