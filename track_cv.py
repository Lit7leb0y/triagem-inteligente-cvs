import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import time
import os

st.set_page_config(page_title="Triagem Inteligente de CVs", page_icon="📄", layout="wide")
st.title("📄 Triagem Inteligente de Candidaturas")
st.caption("Usando Google Gemini • Upload de CVs em PDF + Ranking automático")

# ===================== CONFIGURAÇÃO DA API =====================
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""

# tenta carregar da variável de ambiente ou do Streamlit secrets
default_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if default_key:
    st.session_state.gemini_key = default_key
    try:
        genai.configure(api_key=default_key)
    except Exception:
        # ignore configuration errors for now
        pass

# campo para inserir manualmente (tipo password) — não mostra o valor
api_input = st.text_input(
    "Gemini API Key (deixe em branco se definida em secrets/env)",
    value="",
    type="password",
    help="Defina GEMINI_API_KEY em .streamlit/secrets.toml ou na variável de ambiente GEMINI_API_KEY para não inserir aqui."
)

if api_input:
    st.session_state.gemini_key = api_input
    genai.configure(api_key=api_input)

# ===================== INTERFACE =====================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Descrição da Vaga")
    job_description = st.text_area(
        "Coloque aqui a descrição da vaga", 
        height=300,
        placeholder="Seja bem detalhista"
    )

with col2:
    st.subheader("📤 Upload dos CVs")
    uploaded_files = st.file_uploader(
        "Envie os CVs em PDF (pode selecionar vários)", 
        type=["pdf"],
        accept_multiple_files=True
    )

if st.button("🚀 Iniciar Triagem", type="primary", disabled=not (st.session_state.gemini_key and job_description and uploaded_files)):
    if not st.session_state.gemini_key:
        st.error("Por favor, insira sua Gemini API Key")
        st.stop()
    
    if not uploaded_files:
        st.error("Envie pelo menos um CV")
        st.stop()

    # Processamento
    results = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        progress_bar.progress((i) / len(uploaded_files))
        
        with st.spinner(f"Analisando {file.name}..."):
            # Extrair texto do PDF
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            if not text.strip():
                results.append({
                    "nome": file.name,
                    "score": 0,
                    "justificativa": "Não foi possível extrair texto do PDF."
                })
                continue

            # Prompt poderoso para o Gemini
            prompt = f"""
Você é um recrutador especialista em triagem de currículos.

**Descrição da Vaga:**
{job_description}

**Currículo do Candidato:**
{text[:8000]}  # limite para não estourar tokens

Analise o currículo acima em relação à vaga e responda **APENAS** no seguinte formato JSON:

{{
  "nome_candidato": "Nome extraído ou nome do arquivo",
  "score": número inteiro de 0 a 100,
  "justificativa": "Explicação clara e objetiva em português, com pontos fortes, gaps e recomendação",
  "principais_pontos_positivos": "lista curta",
  "principais_gaps": "lista curta"
}}

Seja justo, direto e profissional.
"""

            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                # Tentativa de extrair JSON da resposta
                import json
                import re
                
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    data = {
                        "nome_candidato": file.name,
                        "score": 50,
                        "justificativa": response.text[:500],
                        "principais_pontos_positivos": "Não extraído",
                        "principais_gaps": "Não extraído"
                    }
                
                results.append({
                    "nome": data.get("nome_candidato", file.name),
                    "score": data.get("score", 50),
                    "justificativa": data.get("justificativa", response.text),
                    "positivos": data.get("principais_pontos_positivos", ""),
                    "gaps": data.get("principais_gaps", "")
                })
                
            except Exception as e:
                results.append({
                    "nome": file.name,
                    "score": 0,
                    "justificativa": f"Erro na análise: {str(e)}"
                })
        
        time.sleep(0.5)  # pequena pausa para não sobrecarregar

    progress_bar.progress(100)

    # ===================== RESULTADOS =====================
    st.success("✅ Triagem concluída!")
    
    # Ordenar por score (ranking)
    results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)
    
    st.subheader("🏆 Ranking dos Candidatos")
    
    for idx, candidato in enumerate(results_sorted, 1):
        with st.expander(f"#{idx} - {candidato['nome']} → **{candidato['score']} / 100**"):
            st.write("**Justificativa:**")
            st.write(candidato['justificativa'])
            
            if candidato.get('positivos'):
                st.write("**Pontos Fortes:**", candidato['positivos'])
            if candidato.get('gaps'):
                st.write("**Pontos de Melhoria:**", candidato['gaps'])

    # Botão para baixar resultados (opcional)
    if st.button("Baixar ranking como texto"):
        texto = "\n\n".join([f"#{i+1} - {r['nome']} | Score: {r['score']}\n{r['justificativa']}" for i, r in enumerate(results_sorted)])
        st.download_button("Baixar .txt", texto, file_name="ranking_cvs.txt")
