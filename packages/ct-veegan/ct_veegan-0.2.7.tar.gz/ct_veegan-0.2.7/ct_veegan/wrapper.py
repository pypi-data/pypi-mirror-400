# ct_veegan/wrapper.py
import torch
import torch.nn as nn
import os
import requests
import numpy as np
from imblearn.combine import SMOTEENN
from .models import LSTMGenerator, LSTMReconstructor

GITHUB_MODEL_URL = "https://github.com/Benylaode/ct_veegans/releases/download/v0.1.1/ct_veegan_siap.pt"

class CTVeeGANWrapper:
    def __init__(
        self,
        device=None,
        checkpoint_path=None,
        latent_dim=128,
        latent_step_dim=32,
        seq_len=105,
        token_dim=400,
        num_classes=2,
        embed_dim=32,
        hidden_dim=256
    ):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.latent_dim = latent_dim
        self.latent_step_dim = latent_step_dim
        self.seq_len = seq_len
        self.token_dim = token_dim
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim

        if checkpoint_path is None:
            checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "ct_veegan_siap.pt")
        self.checkpoint_path = checkpoint_path

        self._ensure_checkpoint()

        # Load Generator & Reconstructor
        self.model = self._load_model()
        self.reconstructor = self._load_reconstructor()

    def _ensure_checkpoint(self):
        """Download checkpoint jika tidak ada."""
        if os.path.exists(self.checkpoint_path):
            return

        print("⏳ Checkpoint tidak ditemukan. Mengunduh dari GitHub...")
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

        try:
            response = requests.get(GITHUB_MODEL_URL, stream=True)
            if response.status_code == 200:
                with open(self.checkpoint_path, "wb") as f:
                    for c in response.iter_content(1024):
                        f.write(c)
                print("✅ Checkpoint berhasil diunduh!")
            else:
                print(f"⚠ Gagal mengunduh checkpoint. Status: {response.status_code}")
        except Exception as e:
            print(f"⚠ Error saat download: {e}")

    def _load_model(self):
        model = LSTMGenerator(
            latent_dim=self.latent_dim,
            latent_step_dim=self.latent_step_dim,
            num_classes=self.num_classes,
            embed_dim=self.embed_dim,
            seq_len=self.seq_len,
            token_dim=self.token_dim,
            hidden_dim=self.hidden_dim,
        ).to(self.device)

        if os.path.exists(self.checkpoint_path):
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            # Load G_state_dict
            if "G_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["G_state_dict"], strict=False)
        
        model.eval()
        return model

    def _load_reconstructor(self):
        rec = LSTMReconstructor(self.seq_len, self.token_dim, self.latent_dim, self.hidden_dim).to(self.device)
        
        if os.path.exists(self.checkpoint_path):
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            if "F_state_dict" in checkpoint:
                # Load F_state_dict
                rec.load_state_dict(checkpoint["F_state_dict"], strict=False)
        
        rec.eval()
        return rec
    
    # ---------------------------------------------------------
    # FITUR UTAMA: BALANCE (Tanpa input reconstructor manual)
    # ---------------------------------------------------------
    def balance(self, X_train, y_train, minor_class, noise_scale=0.05, pad_value=0.0):
        device = torch.device(self.device)
        
        # Gunakan reconstructor milik class
        reconstructor = self.reconstructor 

        X = torch.tensor(X_train, dtype=torch.float32, device=device)
        y = torch.tensor(y_train, dtype=torch.long, device=device)
        
        unique, counts = torch.unique(y, return_counts=True)
        class_counts = dict(zip(unique.cpu().numpy(), counts.cpu().numpy()))
        
        # Handle jika minor_class tidak ada di data
        if minor_class not in class_counts:
            minor_count = 0
            max_count = max(class_counts.values()) if class_counts else 0
        else:
            minor_count = int(class_counts[minor_class])
            max_count = max(class_counts.values())
            
        need = max_count - minor_count
        
        if need <= 0:
            mask = (X != pad_value).any(-1).cpu().numpy()
            return X.cpu().numpy(), y.cpu().numpy(), mask
        
        seq_len, token_dim = X.shape[1], X.shape[2]
        
        # 1. Flatten & SMOTE
        X_flat = X.mean(dim=1).cpu().numpy()
        y_np = y.cpu().numpy()
        
        # Gunakan 'auto' atau 'not majority' agar aman
        try:
            sm = SMOTEENN(sampling_strategy='auto', random_state=42)
            X_res, y_res = sm.fit_resample(X_flat, y_np)
        except ValueError:
            # Fallback jika sampel terlalu sedikit untuk SMOTEENN
            print("⚠ Data terlalu sedikit untuk SMOTEENN, melewati tahap ini.")
            mask = (X != pad_value).any(-1).cpu().numpy()
            return X.cpu().numpy(), y.cpu().numpy(), mask

        # 2. Filter hasil SMOTE (ambil kelas minor saja)
        minor_mask = (y_res == minor_class)
        X_minor = X_res[minor_mask]
        
        # Jika SMOTE gagal menambah data
        if len(X_minor) == 0:
             mask = (X != pad_value).any(-1).cpu().numpy()
             return X.cpu().numpy(), y.cpu().numpy(), mask

        X_minor_seq = np.repeat(X_minor[:, None, :], seq_len, axis=1)
        X_minor_seq_t = torch.tensor(X_minor_seq, dtype=torch.float32, device=device)
        
        # 3. Reconstruction (Flat -> Latent Z)
        X_rec = X_minor_seq_t.reshape(X_minor_seq_t.size(0), -1)
        
        # Handle dimensi linear layer
        expected_dim = next((m.in_features for m in reconstructor.modules() if isinstance(m, nn.Linear)), X_rec.shape[1])
        if X_rec.shape[1] < expected_dim:
            padding = torch.zeros((X_rec.size(0), expected_dim - X_rec.shape[1]), device=device)
            X_rec = torch.cat([X_rec, padding], dim=1)
        else:
            X_rec = X_rec[:, :expected_dim]
        
        with torch.no_grad():
            z_pool = reconstructor(X_rec)
        
        # 4. Sampling Latent Z
        if z_pool.shape[0] >= need:
            idx = torch.randperm(z_pool.shape[0], device=device)[:need]
            z = z_pool[idx]
        else:
            # Jika hasil SMOTE lebih sedikit dari yang dibutuhkan, lakukan resampling
            idx = torch.randint(0, z_pool.shape[0], (need,), device=device)
            z = z_pool[idx]

        # Tambah noise agar variatif
        z = z + noise_scale * torch.randn_like(z)
        
        # 5. Generate Data Baru (Latent Z -> Sequence)
        z_step = torch.randn((need, seq_len, self.latent_step_dim), device=device)
        labels = torch.full((need,), minor_class, dtype=torch.long, device=device)
        
        with torch.no_grad():
            X_fake = self.model(z, z_step, labels)
        
        if X_fake.ndim == 2 and X_fake.shape[1] == seq_len * token_dim:
            X_fake = X_fake.reshape(need, seq_len, token_dim)
        
        # 6. Post-processing (Padding mask dari data asli)
        if minor_count > 0:
            # Ambil pola padding dari salah satu sampel asli kelas minor
            # Pastikan indeks valid
            indices = (y == minor_class).nonzero(as_tuple=True)[0]
            if len(indices) > 0:
                X_minor_orig = X[indices[0]]
                padmask = (X_minor_orig == pad_value).all(dim=1)
                if padmask.any():
                    X_fake[:, padmask, :] = pad_value
        
        # 7. Gabungkan Data Asli + Sintetis
        X_final = torch.cat([X, X_fake], dim=0).cpu().numpy()
        y_fake = np.full((need,), minor_class, dtype=y_train.dtype)
        y_final = np.concatenate([y_train, y_fake], axis=0)
        mask_final = (X_final != pad_value).any(axis=(1, 2)).astype(float)
        
        return X_final, y_final, mask_final