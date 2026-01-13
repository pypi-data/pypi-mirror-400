from tabpfn import TabPFNClassifier
import torch

if torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

clf = TabPFNClassifier()
print("TabPFN device:", clf.device)
