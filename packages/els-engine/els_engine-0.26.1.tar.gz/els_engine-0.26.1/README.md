# els-engine

A lightweight, focused Python toolkit for performing **Equidistant Letter Sequence (ELS)** searches on Hebrew text.

Version: **0.26.1**

This package provides a clean, minimal API for scanning text at fixed skip intervals and returning structured ELS results.

---

## 📦 Installation

```bash
pip install els-engine


"""from els_engine import find_els

text = "בראשיתבראאלהיםאתהשמיםואתהארץ"
target = "אלהים"

results = find_els(text, target, skip=5)

for r in results:
    print(r)"""