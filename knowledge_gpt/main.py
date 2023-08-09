import streamlit as st

from knowledge_gpt.components.sidebar import sidebar

from knowledge_gpt.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from knowledge_gpt.core.caching import bootstrap_caching

from knowledge_gpt.core.parsing import read_file
from knowledge_gpt.core.chunking import chunk_file
from knowledge_gpt.core.embedding import embed_files
from knowledge_gpt.core.qa import query_folder

EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL = "openai"

# For testing
# EMBEDDING, VECTOR_STORE, MODEL = ["debug"] * 3

st.set_page_config(page_title="Знания_GPT", page_icon="📖", layout="wide")
st.header("📖Знания_GPT")

# Enable caching for expensive functions
bootstrap_caching()

sidebar()

openai_api_key = st.session_state.get("OPENAI_API_KEY")


if not openai_api_key:
    st.warning(
        "Введите свой ключ API OpenAI на боковой панели. Вы можете получить ключ в"
        " https://platform.openai.com/account/api-keys."
    )


uploaded_file = st.file_uploader(
    "Загрузите файл pdf, docx или txt",
    type=["pdf", "docx", "txt"],
    help="Отсканированные документы пока не поддерживаются!",
)

if not uploaded_file:
    st.stop()

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e)

chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

if not is_file_valid(file):
    st.stop()

if not is_open_ai_key_valid(openai_api_key):
    st.stop()


with st.spinner("Индексирование документа... Это может занять некоторое время⏳"):
    folder_index = embed_files(
        files=[chunked_file],
        embedding=EMBEDDING,
        vector_store=VECTOR_STORE,
        openai_api_key=openai_api_key,
    )

with st.form(key="qa_form"):
    query = st.text_area("Задать вопрос по документу")
    submit = st.form_submit_button("Поиск")


with st.expander("Расширенные настройки"):
    return_all_chunks = st.checkbox("Показать все фрагменты, полученные в результате векторного поиска")
    show_full_doc = st.checkbox("Показать проанализированное содержимое документа")


if show_full_doc:
    with st.expander("Документ"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)


if submit:
    if not is_query_valid(query):
        st.stop()

    # Output Columns
    answer_col, sources_col = st.columns(2)

    result = query_folder(
        folder_index=folder_index,
        query=query,
        return_all=return_all_chunks,
        model=MODEL,
        openai_api_key=openai_api_key,
        temperature=0,
    )

    with answer_col:
        st.markdown("#### Ответ")
        st.markdown(result.answer)

    with sources_col:
        st.markdown("#### Источники")
        for source in result.sources:
            st.markdown(source.page_content)
            st.markdown(source.metadata["source"])
            st.markdown("---")
