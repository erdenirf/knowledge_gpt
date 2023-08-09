import streamlit as st

from knowledge_gpt.components.faq import faq
from dotenv import load_dotenv
import os

load_dotenv()


def sidebar():
    with st.sidebar:
        st.markdown(
            "## Как пользоваться\n"
            "1. Введите ваш [OpenAI API ключ](https://platform.openai.com/account/api-keys) ниже🔑\n"  # noqa: E501
            "2. Загружайте pdf, docx, txt файлы📄\n"
            "3. Задавайте вопросы по документам💬\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="(sk-...)",
            help="Можете получить ключ API на https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input

        st.markdown("---")
        st.markdown("## О приложении")
        st.markdown(
            "📖ЗнанияGPT даёт загружать документы и получать ответы с цитированием текста из документов. (С) mmz_001"
        )
        st.markdown("---")

        faq()
