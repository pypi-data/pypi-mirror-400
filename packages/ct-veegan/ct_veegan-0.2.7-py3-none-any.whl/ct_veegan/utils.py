import os
import random
import numpy as np
from collections import defaultdict

import torch
import torch.nn as nn
import torch.autograd as autograd
import torch.nn.functional as F

from imblearn.combine import SMOTEENN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from datasets import load_dataset


# -------------------------------------------------------------------------
# GRADIENT PENALTY (FOR WGAN)
# -------------------------------------------------------------------------
def gradient_penalty(critic, real, fake, labels):
    alpha = torch.rand(real.size(0), 1, 1, device=real.device).expand_as(real)
    interpolates = (alpha * real + (1 - alpha) * fake).requires_grad_(True)
    
    with torch.backends.cudnn.flags(enabled=False):
        d_interpolates, _ = critic(interpolates, labels)
    
    fake_out = torch.ones(d_interpolates.size(), device=real.device)
    grads = autograd.grad(
        outputs=d_interpolates,
        inputs=interpolates,
        grad_outputs=fake_out,
        create_graph=True,
        retain_graph=True,
        only_inputs=True
    )[0]
    
    grads = grads.reshape(grads.size(0), -1)
    gp = ((grads.norm(2, dim=1) - 1) ** 2).mean()
    return gp


def gradient_penalty_joint(D_zx, x_real, x_fake, z_fake, z_real):
    batch_size = x_real.size(0)
    alpha_x = torch.rand(batch_size, 1, 1, device=x_real.device)
    alpha_z = torch.rand(batch_size, 1, device=z_fake.device)
    
    interpolated_x = (alpha_x * x_real + (1 - alpha_x) * x_fake).requires_grad_(True)
    interpolated_z = (alpha_z * z_real + (1 - alpha_z) * z_fake).requires_grad_(True)
    
    d_interpolates = D_zx(interpolated_z, interpolated_x)
    fake_out = torch.ones_like(d_interpolates, device=x_real.device)
    
    grad_x, grad_z = autograd.grad(
        outputs=d_interpolates,
        inputs=[interpolated_x, interpolated_z],
        grad_outputs=fake_out,
        create_graph=True,
        retain_graph=True,
        only_inputs=True
    )
    
    grad_x = grad_x.reshape(batch_size, -1)
    grad_z = grad_z.reshape(batch_size, -1)
    grad_norm = torch.sqrt(torch.sum(grad_x**2, dim=1) + torch.sum(grad_z**2, dim=1) + 1e-12)
    
    gp = ((grad_norm - 1) ** 2).mean()
    return gp


# -------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------------------------------
def pad_vector_sequences(seqs, maxlen, token_dim):
    N = len(seqs)
    out = np.zeros((N, maxlen, token_dim), dtype=np.float32)
    lengths = np.zeros(N, dtype=np.int64)
    
    for i, s in enumerate(seqs):
        L = min(len(s), maxlen)
        out[i, :L] = s[:L]
        lengths[i] = L
    return out, lengths


def build_label_index_map(label_tensor):
    label_to_idx = defaultdict(list)
    labels_cpu = label_tensor.cpu().numpy()
    
    for i, lab in enumerate(labels_cpu):
        label_to_idx[int(lab)].append(i)
    
    return label_to_idx


def sample_real_by_labels(data_tensor, label_tensor, gen_y, lengths_tensor=None, label_to_idx=None, device='cpu'):
    if label_to_idx is None:
        label_to_idx = build_label_index_map(label_tensor)
    
    batch_real, batch_lab, batch_len = [], [], []
    
    for lab in gen_y.cpu().tolist():
        idx_list = label_to_idx.get(int(lab), None)
        idx = random.choice(idx_list) if idx_list else random.randrange(0, data_tensor.size(0))
        
        batch_real.append(data_tensor[idx].cpu().numpy())
        batch_lab.append(int(lab))
        batch_len.append(int(lengths_tensor[idx].cpu().item()) if lengths_tensor is not None else data_tensor.size(1))
    
    real_x = torch.tensor(np.stack(batch_real), dtype=torch.float32, device=device)
    real_y = torch.tensor(batch_lab, dtype=torch.long, device=device)
    real_lengths = torch.tensor(batch_len, dtype=torch.long, device=device)
    
    return real_x, real_y, real_lengths


# -------------------------------------------------------------------------
# GENERATOR FUNCTIONS
# -------------------------------------------------------------------------
def generate(model, latent_dim, seq_len, latent_step_dim, num_classes, batch_size=1, labels=None, device='cpu'):
    z = torch.randn(batch_size, latent_dim, device=device)
    z_step = torch.randn(batch_size, seq_len, latent_step_dim, device=device)
    
    if labels is None:
        labels = torch.randint(0, num_classes, (batch_size,), device=device)
    elif isinstance(labels, list):
        labels = torch.tensor(labels, device=device)
    
    with torch.no_grad():
        return model(z, z_step, labels)


def generate_sequence(model, n_generate, label_class, latent_dim, seq_len, latent_step_dim, device='cpu'):
    z = torch.randn((n_generate, latent_dim), device=device)
    z_step = torch.randn((n_generate, seq_len, latent_step_dim), device=device)
    labels = torch.full((n_generate,), label_class, dtype=torch.long, device=device)
    
    with torch.no_grad():
        x = model(z, z_step, labels)
    
    return x.detach().cpu().numpy()


def tokens_to_words_batch(generated_sequences, model_word2vec, shared_vocab, pad_threshold=1e-8):
    vocab_list = list(shared_vocab)
    vocab_vectors = np.array([model_word2vec.wv[w] for w in vocab_list])
    
    all_sentences = []
    for seq in generated_sequences:
        words = []
        for vec in seq:
            if np.all(np.abs(vec) < pad_threshold):
                continue
            scores = cosine_similarity([vec], vocab_vectors)[0]
            best_word = vocab_list[int(np.argmax(scores))]
            words.append(best_word)
        all_sentences.append(" ".join(words))
    
    return all_sentences



# -------------------------------------------------------------------------
# GENERATE INDONESIAN SENTENCES (Self-contained)
# -------------------------------------------------------------------------
def generate_indonesian_sentences(model_generator, latent_dim, seq_len, latent_step_dim,
                                  w2v_path=None, # Jadikan argumen
                                  device='cpu', n_generate=5, label_class=0, pad_threshold=1e-8):
    
    if w2v_path is None:
        # Cari file relatif terhadap lokasi file utils.py
        w2v_path = os.path.join(os.path.dirname(__file__), "wiki.id.case.finetuned.model")


    if not os.path.exists(w2v_path):
        raise FileNotFoundError(f"Model Word2Vec tidak ditemukan di: {w2v_path}")
        
    model_word2vec = Word2Vec.load(w2v_path)

    ds = load_dataset("haipradana/indonesian-twitter-hate-speech-cleaned")
    corpus = ds["train"]["text"]
    
    # Shared vocab (TF-IDF ∩ Word2Vec)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_vectorizer.fit(corpus)
    tfidf_vocab = set(tfidf_vectorizer.get_feature_names_out())
    w2v_vocab = set(model_word2vec.wv.index_to_key)
    shared_vocab = tfidf_vocab.intersection(w2v_vocab)
    
    vocab_list = list(shared_vocab)
    vocab_vectors = np.array([model_word2vec.wv[w] for w in vocab_list])
    
    # Generate latent
    device = torch.device(device)
    z = torch.randn((n_generate, latent_dim), device=device)
    z_step = torch.randn((n_generate, seq_len, latent_step_dim), device=device)
    labels = torch.full((n_generate,), label_class, dtype=torch.long, device=device)
    
    # Generate sequence
    with torch.no_grad():
        x_synthetic = model_generator(z, z_step, labels)
    
    x_synthetic_np = x_synthetic.detach().cpu().numpy() if torch.is_tensor(x_synthetic) else x_synthetic
    
    # Token → Words
    all_sentences = []
    for seq in x_synthetic_np:
        words = []
        for vec in seq:
            if np.all(np.abs(vec) < pad_threshold):
                continue
            scores = cosine_similarity([vec], vocab_vectors)[0]
            words.append(vocab_list[int(np.argmax(scores))])
        all_sentences.append(" ".join(words))
    
    return all_sentences
