import torch
import torch.nn as nn
import torch.nn.functional as F

class PhysNet(nn.Module):
    """
    PhysNet: Spatio-temporal network for rPPG.
    Simplified implementation based on Yu et al. (2019).
    """
    def __init__(self, in_channels=3, temporal_len=32):
        super(PhysNet, self).__init__()

        self.encoder = nn.Sequential(
            nn.Conv3d(in_channels, 32, kernel_size=(1, 5, 5), stride=1, padding=(0, 2, 2)),
            nn.BatchNorm3d(32),
            nn.ELU(),
            nn.MaxPool3d((1, 2, 2), stride=(1, 2, 2)),

            nn.Conv3d(32, 64, kernel_size=(3, 3, 3), stride=1, padding=(1, 1, 1)),
            nn.BatchNorm3d(64),
            nn.ELU(),
            nn.Conv3d(64, 64, kernel_size=(3, 3, 3), stride=1, padding=(1, 1, 1)),
            nn.BatchNorm3d(64),
            nn.ELU(),
            nn.MaxPool3d((1, 2, 2), stride=(1, 2, 2)),

            nn.Conv3d(64, 64, kernel_size=(3, 3, 3), stride=1, padding=(1, 1, 1)),
            nn.BatchNorm3d(64),
            nn.ELU(),
            nn.Conv3d(64, 64, kernel_size=(3, 3, 3), stride=1, padding=(1, 1, 1)),
            nn.BatchNorm3d(64),
            nn.ELU(),
            nn.MaxPool3d((1, 2, 2), stride=(1, 2, 2)),
        )

        # Decoder / Regression Head to get 1D signal
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool3d((temporal_len, 1, 1)),
            nn.Flatten(),
            # Output is the rPPG signal of length `temporal_len`
            # But here we might just map it to 1 value per frame if we want BVP
        )
        # Using a simple projection to 1 channel (rPPG)
        self.regressor = nn.Linear(64, 1)

    def forward(self, x):
        # x: (B, C, T, H, W)
        B, C, T, H, W = x.shape
        x = self.encoder(x) # (B, 64, T, H/8, W/8)

        # Global Average Pooling over Spatial dimensions
        x = x.mean(dim=(-1, -2)) # (B, 64, T)

        x = x.permute(0, 2, 1) # (B, T, 64)
        x = self.regressor(x) # (B, T, 1)
        return x.squeeze(-1) # (B, T)
