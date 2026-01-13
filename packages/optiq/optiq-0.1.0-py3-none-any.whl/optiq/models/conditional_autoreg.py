import torch
from torch import nn


class ConditionalAutoregressiveModel(nn.Module):
    """
    Simple GRU-based autoregressive predictor conditioned on a class label.

    Inputs:
        history: (B, T, J, 3) sequence of past positions
        class_ids: (B,) integer class labels
    Output:
        next_positions: (B, J, 3)
    """

    def __init__(
        self,
        joints: int,
        num_classes: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.joints = joints
        self.embed = nn.Embedding(num_classes, hidden_size)
        self.input_proj = nn.Linear(joints * 3 + hidden_size, hidden_size)
        self.gru = nn.GRU(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Linear(hidden_size, joints * 3)

    def forward(self, history: torch.Tensor, class_ids: torch.Tensor) -> torch.Tensor:
        """
        history: (B, T, J, 3)
        class_ids: (B,)
        """
        b, t, j, _ = history.shape
        assert j == self.joints, "Mismatch between input joints and model joints"

        x = history.reshape(b, t, j * 3)
        class_emb = self.embed(class_ids)  # (B, H)
        class_expanded = class_emb.unsqueeze(1).expand(-1, t, -1)

        feats = torch.cat([x, class_expanded], dim=-1)
        feats = self.input_proj(feats)
        out, _ = self.gru(feats)
        last_state = out[:, -1]
        pred = self.head(last_state)
        return pred.view(b, j, 3)

    @torch.no_grad()
    def generate(
        self,
        seed: torch.Tensor,
        class_id: int,
        steps: int,
        device: torch.device,
    ) -> torch.Tensor:
        """
        Autoregressively roll out predictions.

        Args:
            seed: (T, J, 3) initial window
            class_id: integer class
            steps: number of future frames to generate
            device: torch device

        Returns:
            Tensor of shape (steps, J, 3)
        """
        self.eval()
        window = seed.clone().to(device=device, dtype=torch.float32)
        outputs = []
        cls = torch.tensor([class_id], device=device, dtype=torch.long)
        for _ in range(steps):
            pred = self.forward(window.unsqueeze(0), cls)[0]  # (J,3)
            outputs.append(pred.cpu())
            window = torch.cat([window[1:], pred.unsqueeze(0)], dim=0)
        return torch.stack(outputs, dim=0)
