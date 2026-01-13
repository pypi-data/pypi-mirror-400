import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from .models import LSTMGenerator, LSTMDiscriminator, LSTMReconstructor, JointDisc
from .utils import gradient_penalty, gradient_penalty_joint


class Trainer:
    def __init__(self,
                 lr_g=1e-4,
                 lr_d=1e-4,
                 gp_weight=10.0,
                 save_dir='checkpoints',
                 checkpoint_every=5,
                 early_stopping_patience=10):
        
        # 🔹 Auto Device (use CUDA jika tersedia)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[DEVICE] Using: {self.device}")

        # 🔹 Model Auto-load (pakai model default package)
        self.G = LSTMGenerator().to(self.device)
        self.D = LSTMDiscriminator().to(self.device)
        self.F = LSTMReconstructor().to(self.device)
        self.D_zx = JointDisc().to(self.device)

        self.gp_weight = gp_weight
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.checkpoint_every = checkpoint_every
        self.early_stopping_patience = early_stopping_patience

        # 🔹 Optimizers
        self.opt_g = optim.Adam(self.G.parameters(), lr=lr_g, betas=(0.5, 0.999))
        self.opt_d = optim.Adam(self.D.parameters(), lr=lr_d, betas=(0.5, 0.999))
        self.opt_f = optim.Adam(self.F.parameters(), lr=lr_g, betas=(0.5, 0.999))

        self.scheduler_g = None
        self.scheduler_d = None

        # ⭐ Auto–load checkpoint bawaan package
        pkg_root = os.path.dirname(os.path.abspath(__file__))
        self.default_checkpoint = os.path.join(pkg_root, "..", "checkpoints", "ct_veegan_siap.pt")
        self.load_pretrained_checkpoint(self.default_checkpoint, silent=True)

    # ============================================================
    # 🔹 AUTO LOAD CHECKPOINT
    # ============================================================
    def load_pretrained_checkpoint(self, checkpoint_path, silent=False):
        if not os.path.exists(checkpoint_path):
            if not silent:
                print(f"⚠ Checkpoint not found: {checkpoint_path}")
            return
        
        state = torch.load(checkpoint_path, map_location=self.device)
        self.G.load_state_dict(state.get("G_state_dict", {}))
        self.D.load_state_dict(state.get("D_state_dict", {}))

        if "F_state_dict" in state:
            self.F.load_state_dict(state["F_state_dict"])
        if "D_zx_state_dict" in state:
            self.D_zx.load_state_dict(state["D_zx_state_dict"])

        if not silent:
            print(f"📦 Loaded pretrained checkpoint: {checkpoint_path}")

    # ============================================================
    # 🔹 TRAINING LOOP (dipakai base pretraining & transfer)
    # ============================================================
    def _train_loop(self, dataloader, epochs=50, freeze=False, save=False):
        if freeze:
            for name, param in self.G.named_parameters():
                param.requires_grad = False
            if hasattr(self.G, "to_token"):
                for p in self.G.to_token.parameters(): p.requires_grad = True
            print("🧊 Freeze backbone enabled.")

        best_g_loss = float("inf")
        patience = 0

        for epoch in range(epochs):
            g_losses, d_losses = [], []
            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")

            for x_real, y_labels in pbar:
                x_real = x_real.to(self.device)
                y_labels = y_labels.to(self.device)
                bs = x_real.size(0)

                # Build latent input automatically
                latent_dim = self.G.fc.in_features - self.G.label_emb.embedding_dim
                z = torch.randn(bs, latent_dim, device=self.device)
                z_step_dim = self.G.step_proj.in_features - self.G.label_emb.embedding_dim
                z_step = torch.randn(bs, self.G.seq_len, z_step_dim, device=self.device)

                # 1️⃣ Train Discriminator
                self.D.zero_grad()
                x_fake = self.G(z, z_step, y_labels).detach()
                real_score, _ = self.D(x_real, y_labels)
                fake_score, _ = self.D(x_fake, y_labels)
                gp = gradient_penalty(self.D, x_real, x_fake, y_labels)
                d_loss = fake_score.mean() - real_score.mean() + self.gp_weight * gp
                d_loss.backward()
                self.opt_d.step()

                # 2️⃣ Train Generator
                self.G.zero_grad()
                gx = self.G(z, z_step, y_labels)
                g_score, _ = self.D(gx, y_labels)
                g_loss = -g_score.mean()
                g_loss.backward()
                self.opt_g.step()

                # 3️⃣ Train Reconstructor
                f_loss_item = 0.0
                if self.F:
                    self.F.zero_grad()
                    z_pred = self.F(gx.detach())
                    f_loss = nn.MSELoss()(z_pred, z)
                    f_loss.backward()
                    self.opt_f.step()
                    f_loss_item = f_loss.item()

                g_losses.append(g_loss.item())
                d_losses.append(d_loss.item())

            avg_g = sum(g_losses)/len(g_losses)
            avg_d = sum(d_losses)/len(d_losses)
            print(f"Epoch {epoch+1} → G={avg_g:.4f}, D={avg_d:.4f}")

            # Early Stop
            if avg_g < best_g_loss:
                best_g_loss = avg_g
                patience = 0
            else:
                patience += 1
                if patience >= self.early_stopping_patience:
                    print("🛑 Early stopping triggered."); break

            if save and (epoch+1) % self.checkpoint_every == 0:
                self.save_checkpoint(epoch+1, avg_g, avg_d)

    # ============================================================
    # 🔹 PUBLIC API
    # ============================================================
    def train(self, dataloader, epochs=50):
        print("🔷 TRAIN MODEL BASE")
        return self._train_loop(dataloader, epochs, freeze=False, save=True)

    def transfer_learn(self, dataloader, epochs=10, freeze=True):
        print("🟡 TRANSFER LEARNING MODE")
        return self._train_loop(dataloader, epochs, freeze=freeze, save=False)
