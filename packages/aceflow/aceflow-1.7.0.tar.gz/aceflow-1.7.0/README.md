# AceFlow - Seq2Seq Model Library

<div align="center">

![AceFlow Logo](https://img.shields.io/badge/AceFlow-Seq2Seq-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![PyTorch](https://img.shields.io/badge/PyTorch-1.9%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

A powerful Python library for building and training Sequence-to-Sequence models with attention mechanisms.

</div>

## 🚀 Features

- **Multiple RNN Types**: LSTM, GRU, RNN, and bidirectional variants
- **Attention Mechanisms**: Bahdanau and Luong-style attention
- **Custom Model Format**: Save/load models in `.ace` format
- **Advanced Tokenization**: Flexible preprocessing and vocabulary management
- **Production Ready**: Comprehensive training utilities and inference tools

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start](docs/quickstart.md)
- [API Reference](docs/api/)
- [User Guides](docs/guides/)
- [Examples](docs/examples/)

## 🎯 Quick Example

```python
from aceflow import Seq2SeqModel
from aceflow.utils import Tokenizer

# Initialize model
model = Seq2SeqModel(
    src_vocab_size=1000,
    tgt_vocab_size=1000,
    hidden_size=256,
    rnn_type='lstm',
    use_attention=True
)

# Train and save
model.save("model.ace")

# Load model
loaded_model = Seq2SeqModel.load("model.ace")
```

## 📦 Installation



For detailed installation instructions, see [Installation Guide](docs/installation.md).


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

<div align="center">
Made with ❤️ by Maaz Waheed
</div>
```
