from tabpfn import TabPFNClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

X, y = make_classification(
    n_samples=200, n_features=20, random_state=0
)

clf = TabPFNClassifier(device="cpu")
clf.fit(X[:100], y[:100])  # very small subset
pred = clf.predict(X[100:])
print("F1:", f1_score(y[100:], pred))


import torch
# CRITICAL FIX: Force PyTorch to use 1 thread to prevent deadlock
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

