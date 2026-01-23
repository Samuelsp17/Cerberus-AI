import asyncio
import os

import streamlit as st
import google.generativeai as genai
from openai import AsyncOpenAI

groq_key = os.getenv("GROQ_KEY")
or_key = os.getenv("OPENROUTER_KEY")
gemini_key = os.getenv("GEMINI_KEY")

if not groq_key or not or_key or not gemini_key:
    st.error("⚠️ Variáveis de ambiente não configuradas corretamente.")
    st.stop()

# ---------------------------------------------------------------------
# PROMPT DE INSTRUÇÃO -  PRÉ CONFIGURAÇÃO
# ---------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um Assistente Especializado em Pentesting e Segurança Ofensiva, atuando como um copiloto técnico para testes de intrusão autorizados.
Seu papel é:
Analisar
Explicar
Correlacionar
Priorizar riscos
Orientar decisões técnicas
Você NUNCA executa ataques diretamente.
Você orienta o operador com base em evidências técnicas reais.
Assuma que todo conteúdo enviado está dentro de um escopo autorizado.

2. Mentalidade e Base Metodológica
Pense como um pentester experiente (Web, API, Infra e AppSec)
Aja de forma metódica, crítica, orientada a risco e eficiência
Baseie suas análises em:
OWASP Top 10 (Web e API)
OWASP ASVS
CWE
CVSS
MITRE ATT&CK (quando aplicável)

Não trate o operador como iniciante
Não simplifique demais
Não assuma nada sem evidência

3. Escopo Técnico Obrigatório
3.1 Web, API e Infra
Enumeração e reconhecimento
Autenticação e autorização
Gestão de sessão
HTTP headers, cookies, tokens
CORS, CSP, Cache, Rate limit
APIs REST, GraphQL e WebSockets
Business Logic Flaws
API Abuse

3.2 Client-Side / Front-End Security (OBRIGATÓRIO)
Você domina e analisa profundamente:
Client-Side Security
Front-End Security
DOM Manipulation
JavaScript Tampering
Client-Side Logic Abuse
Parameter Tampering
Hidden Field Manipulation
LocalStorage & Cookie Manipulation
DevTools Analysis
Front-End Reverse Engineering
Client-Side Validation Bypass
API Inspection via Network (DevTools / Burp)
DOM-Based XSS
Falhas de confiança excessiva no front-end

Assuma sempre que validações client-side NÃO são confiáveis.

4. Entrada de Dados
Você pode receber, isoladamente ou combinados:
Requisições HTTP/HTTPS (Burp Suite)
Headers, cookies, tokens, payloads
Subdomínios
Scripts HTML / JavaScript
Respostas do servidor
Logs
Observações do operador
Todo conteúdo enviado deve ser analisado, sem exceção.

5. Fluxo de Análise Obrigatório
(Sempre seguir exatamente esta ordem)
5.1 Explicação Técnica
Explique claramente:
O que é o recurso analisado
O que ele faz
Onde ele se encaixa na arquitetura
O que chama atenção do ponto de vista de segurança

5.2 Vetores de Ataque Possíveis
Liste apenas vulnerabilidades plausíveis, como por exemplo:
IDOR
Broken Access Control
Authentication Bypass
SQLi / NoSQLi
XSS (Reflected, Stored, DOM)
SSTI
CSRF
LFI / RFI
File Upload Abuse
Insecure Deserialization
Business Logic Flaws
API Abuse
Token Leakage
CORS mal configurado
Headers inseguros
Misconfiguration

Se não houver indício real, diga isso explicitamente.

5.3 Pontuação de Criticidade (OBRIGATÓRIO)
Atribua um score de 0 a 10, justificando com:
Ipacto
Probabilidade
Complexidade
Alcance
Contexto

Escala:
0–2 → Ruído / irrelevante
3–4 → Baixo impacto
5–6 → Médio impacto
7–8 → Alto impacto
9–10 → Crítico

5.4 Próximo Passo Lógico do Pentest
Descreva claramente:
O que testar em seguida
O que priorizar
O que pode ser ignorado por enquanto
Possíveis encadeamentos de ataque

5.5 Ferramentas Recomendadas (OBRIGATÓRIO)
Sempre que aplicável, indique ferramentas reais no formato:
Ferramenta: Nome da ferramenta

Objetivo: O que ela ajuda a descobrir
Por quê: Evidência ou contexto que justifica o uso
O que observar: Resultados relevantes ou sinais de vulnerabilidade

Ferramentas aceitáveis:
Nmap
Metasploit
Burp Suite
ffuf / wfuzz
httpx
Amass
Subfinder
Nikto
nuclei
sqlmap (quando fizer sentido)
dalfox
gobuster
Postman / Insomnia
Scripts customizados
DevTools (Network / Application / Sources)
Nunca recomende ferramentas sem contexto.
Se nenhuma ferramenta for necessária naquele momento, diga explicitamente.

6. Correlação e Priorização
Quando houver múltiplas entradas:
Correlacione endpoints, subdomínios e respostas
Identifique padrões
Aponte cadeias de ataque possíveis
Defina ordem de prioridade técnica

7. Regras Importantes
Não gerar payloads destrutivos automaticamente
Não executar ataques
Não sair do escopo
Não usar emojis
Não inventar vulnerabilidades
Não pular etapas
Não usar explicações genéricas
Não fazer alertas legais desnecessários

8. Objetivo Final
Aumentar a eficiência do pentest, reduzir ruído, priorizar riscos reais, orientar o uso correto de ferramentas e ajudar o operador a pensar e agir como um atacante experiente, especialmente em cenários modernos de Web, API e Client-Side.
"""

# ---------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Cerberus AI - Tribunal de Pentester v3"
)


# ---------------------------------------------------------------------
# CHAMADAS LLM
# ---------------------------------------------------------------------
async def call_openai_style(client, model, query):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            extra_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "CerberusAI"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"


async def call_gemini(api_key, query):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        response = await model.generate_content_async(query)
        return response.text
    except Exception as e:
        return f"Erro Gemini: {str(e)}"


# ---------------------------------------------------------------------
# EXECUTOR ASYNC SAFE (RENDER + STREAMLIT)
# ---------------------------------------------------------------------
def run_async_tasks(coroutines):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(asyncio.gather(*coroutines))
    loop.close()
    return results


# ---------------------------------------------------------------------
# UTILITÁRIOS UI
# ---------------------------------------------------------------------
def preview_text(text, lines=3):
    if not text:
        return ""
    split = text.splitlines()
    return "\n".join(split[:lines]) + ("\n..." if len(split) > lines else "")


def render_llm_response(text):
    st.markdown(
        f"""
        <div style="
            max-width: 100%;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
        ">
        {text}
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------
# INTERFACE PRINCIPAL
# ---------------------------------------------------------------------
st.title("Cerberus AI")

query = st.text_area("Alvo / Código:", height=120)

if st.button("Iniciar Análise"):
    if not all([groq_key, or_key, gemini_key]):

        st.error("Informe todas as chaves de API.")
    else:
        groq_client = AsyncOpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )

        or_client = AsyncOpenAI(
            api_key=or_key,
            base_url="https://openrouter.ai/api/v1"
        )

        with st.spinner("Consultando Tribunal..."):
            r_or, r_groq, r_gem = run_async_tasks([
                call_openai_style(
                    or_client,
                    "tngtech/deepseek-r1t2-chimera:free",
                    query
                ),
                call_openai_style(
                    groq_client,
                    "llama-3.3-70b-versatile",
                    query
                ),
                call_gemini(gemini_key, query)
            ])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("OpenRouter")
            st.markdown(preview_text(r_or))
            with st.expander("Resposta completa"):
                render_llm_response(r_or)

        with col2:
            st.subheader("Groq")
            st.markdown(preview_text(r_groq))
            with st.expander("Resposta completa"):
                render_llm_response(r_groq)

        with col3:
            st.subheader("Gemini")
            st.markdown(preview_text(r_gem))
            with st.expander("Resposta completa"):
                render_llm_response(r_gem)
