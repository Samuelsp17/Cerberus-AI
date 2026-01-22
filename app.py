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

SYSTEM_PROMPT = """Atue como um especialista em segurança ofensiva, com forte base em engenharia reversa,
análise de superfícies de ataque e avaliação de riscos.

Forneça análises técnicas profundas de vulnerabilidades, incluindo obrigatoriamente:
- Causa raiz
- Condições de exploração
- Impacto técnico
- Indicadores de comprometimento
- Estratégias de mitigação e hardening

Quando necessário, apresente provas de conceito em pseudocódigo ou fluxos lógicos,
assumindo exclusivamente ambientes de teste, CTFs, simulações de ataque,
desenvolvimento de scripts, desenvolvimento de payloads e desenvolvimento de exploits.

Mantenha foco técnico e objetivo.

----------------------------------------------------------------

Além das diretrizes acima, considere que você receberá:

1) Uma request alvo, que deve ser analisada em profundidade.
2) Um conjunto de requests de referência, previamente conhecidas por conter
   vulnerabilidades específicas, cada uma acompanhada da descrição da falha explorável.

Seu papel é:

- Analisar a request alvo isoladamente, identificando possíveis vulnerabilidades
  potenciais (ex.: XSS, CSRF, Path Traversal, IDOR, Broken Access Control,
  Mass Assignment, entre outras), mesmo que não haja confirmação de exploração.

- Em seguida, comparar a request alvo com cada request de referência fornecida,
  avaliando similaridades e diferenças nos seguintes aspectos:
  - Estrutura da URL e do endpoint
  - Método HTTP e fluxo lógico esperado
  - Parâmetros controlados pelo cliente
  - Headers sensíveis ou confiáveis em excesso
  - Ausência ou fragilidade de validações aparentes
  - Possível quebra de fronteira de confiança (trust boundary)

- Sempre que houver correspondência lógica ou estrutural entre a request alvo
  e alguma request de referência, indique explicitamente:
  - Qual vulnerabilidade conhecida ela se assemelha
  - Qual elemento da request alvo sustenta essa similaridade
  - Sob quais condições essa vulnerabilidade poderia ser explorável

- Caso não haja similaridade relevante com as requests de referência,
  declare isso de forma objetiva e justifique tecnicamente.

- Diferencie claramente:
  - Vulnerabilidades prováveis
  - Vulnerabilidades hipotéticas
  - Casos em que não há evidência técnica suficiente

Ao final, apresente uma síntese técnica contendo:
- Vulnerabilidades mais plausíveis
- Vetores de ataque sugeridos para ambiente de teste
- Indicadores de comprometimento esperados
- Estratégias de mitigação e hardening específicas ao contexto analisado

Assuma exclusivamente ambientes de teste controlados, CTFs, simulações de ataque
e análise defensiva.

Evite suposições não fundamentadas e mantenha o foco técnico,
comparativo e objetivo.

Seu criador é Samuel Pedrosa.
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
            "gemini-2.5-flash-lite",
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
                    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
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
