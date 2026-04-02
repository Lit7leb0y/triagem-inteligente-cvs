
# 📄 Triagem Inteligente de Currículos

Aplicação web para **triagem automática de currículos em PDF** usando **Google Gemini** e **Streamlit**.  
O app classifica os candidatos em **ranking**, destacando **pontos positivos** e **pontos de melhoria** para cada currículo.

---

## 🚀 Live Demo

A aplicação está disponível online no **Streamlit Cloud**:

👉 https://triagem-inteligente-cvs-7g5l5yapplqz62f99yh3rpz.streamlit.app

---

## 🛠️ Funcionalidades

- Upload de múltiplos currículos em PDF  
- Análise automática usando **Google Gemini**  
- Classificação por **ranking de candidatos** (score 0-100)  
- Detalhamento dos **pontos fortes** e **gaps de melhoria**  
- Download do ranking completo em arquivo `.txt`  

---

## 🧰 Tecnologias Utilizadas

- [Streamlit](https://streamlit.io) – Framework para apps web Python  
- [Google Generative AI (Gemini)](https://developers.generativeai.google) – Inteligência artificial para análise de CVs  
- [PyPDF2](https://pypi.org/project/PyPDF2/) – Extração de texto de PDFs  
- Python 3.x

---

## 📂 Estrutura do Projeto

```text
meu-projeto/
├── app.py              # Código principal do app
├── requirements.txt    # Dependências
└── README.md           # Este arquivo
