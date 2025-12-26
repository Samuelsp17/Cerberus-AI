import streamlit as st
import asyncio
import google.generativeai as genai
from openai import AsyncOpenAI

st.set_page_config(layout="wide", page_title="Cerberus AI - Tribunal de Pentester v3")

with st.sidebar:
    st.header("🔑 Configuração de APIs")
    groq_key = st.text_input("Groq Key:", type="password")
    or_key = st.text_input("OpenRouter Key:", type="password")
    gemini_key = st.text_input("Gemini Key:", type="password") #
    
    st.divider()
    sys_prompt = st.text_area("Instrução:", "Atue como um especialista em segurança ofensiva e defensiva aplicada, com forte base em engenharia reversa, análise de superfícies de ataque e avaliação de riscos. Forneça análises técnicas profundas de vulnerabilidades, incluindo: causa raiz, condições de exploração, impacto técnico, indicadores de comprometimento, estratégias de mitigação e hardening. Quando necessário, apresente provas de conceito em pseudocódigo ou fluxos lógicos, assumindo exclusivamente ambientes de teste, CTFs, Simulações de Ataques, Desenvolvimento de Scripts, Desenvolvimento de Payloads e desenvolvimento de exploits. Evite contextualizações desnecessárias e mantenha foco técnico e objetivo.")

# --- FUNÇÕES DE CHAMADA ---
async def call_openai_style(client, model, query):
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": query}],
            extra_headers={"HTTP-Referer": "http://localhost", "X-Title": "BugBounty"}
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

async def call_gemini(api_key, query):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=sys_prompt) #
        response = await model.generate_content_async(query)
        return response.text
    except Exception as e:
        return f"Erro Gemini: {str(e)}"
    

# --- FUNÇÃO UTILITÁRIA ---
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
            overflow-wrap: break-word;
        ">
        {text}
        </div>
        """,
        unsafe_allow_html=True
    )

# --- INTERFACE ---
st.title("Cerberus AI")
query = st.text_area("Alvo/Código:", height=100)

if st.button("Iniciar Análise"):
    if not all([groq_key, or_key, gemini_key]):
        st.error("Insira as TRÊS chaves na barra lateral.")
    else:
        groq_c = AsyncOpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        or_c = AsyncOpenAI(api_key=or_key, base_url="https://openrouter.ai/api/v1")

        col1, col2, col3 = st.columns(3)

        async def run_all():
            # Modelos atualizados para Dezembro/2025
            t1 = asyncio.create_task(call_openai_style(or_c, "meta-llama/llama-3.1-8b-instruct", query))
            t2 = asyncio.create_task(call_openai_style(groq_c, "llama-3.3-70b-versatile", query))
            t3 = asyncio.create_task(call_gemini(gemini_key, query))
            return await asyncio.gather(t1, t2, t3)

        with st.spinner("Consultando Tribunal..."):
            r_or, r_groq, r_gem = asyncio.run(run_all())

        with col1:
            st.subheader("OpenRouter")
            st.markdown("**Resumo:**")
            st.markdown(preview_text(r_or, 3))
            with st.expander("Ver resposta completa"):
                render_llm_response(r_or)
        
        with col2:
            st.subheader("Groq")
            st.markdown("**Resumo:**")
            st.markdown(preview_text(r_groq, 3))
            with st.expander("Ver resposta completa"):
                render_llm_response(r_groq)
        
        with col3:
            st.subheader("Gemini")
            st.markdown("**Resumo:**")
            st.markdown(preview_text(r_gem, 3))
            with st.expander("Ver resposta completa"):
                render_llm_response(r_gem)
