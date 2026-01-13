import torch
import torch.nn as nn

class SyncNet(nn.Module):
    """
    SyncNet: Audio-Visual Synchronization Network.
    Simplified implementation.
    """
    def __init__(self):
        super(SyncNet, self).__init__()

        # Audio Encoder (takes MFCCs)
        # Input: (B, 1, 13, 20)
        self.audio_encoder = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(1, 1), stride=(1, 1)),

            nn.Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(1, 2), stride=(1, 2)),

            nn.Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(1, 2), stride=(1, 2)),

            nn.Conv2d(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(1, 2), stride=(1, 2)), # (13, 20) -> (13, 20) -> (13, 10) -> (13, 5) -> (13, 2)
        )
        self.audio_fc = nn.Linear(512 * 13 * 2, 1024) # Corrected size

        # Video Encoder (takes 5 frames of mouth crop, stacked channel-wise)
        # Input: (B, 15, 112, 112). 15 channels = 5 frames * 3 colors.
        self.face_encoder = nn.Sequential(
            nn.Conv2d(15, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)), # 112 -> 56

            nn.Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)), # 56 -> 28

            nn.Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)), # 28 -> 14

            nn.Conv2d(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)), # 14 -> 7
        )
        self.face_fc = nn.Linear(512 * 7 * 7, 1024) # 512 * 49

    def forward(self, audio, video):
        # Audio: (B, 1, 13, 20)
        # Video: (B, 15, 112, 112)

        a = self.audio_encoder(audio)
        v = self.face_encoder(video)

        # Flatten
        a = a.view(a.size(0), -1)
        v = v.view(v.size(0), -1)

        a = self.audio_fc(a)
        v = self.face_fc(v)

        # L2 Normalize
        a = nn.functional.normalize(a, p=2, dim=1)
        v = nn.functional.normalize(v, p=2, dim=1)

        return a, v
