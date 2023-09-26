import streamlit as st
from view import auto_dataset_producter_page, saved_dataset_page,fine_tuning_page, setting_api_page, document_page
from model import DatasetModel

def main():
    st.set_page_config(
        page_title="簡単ファインチューニング",
        page_icon="🧊",
    )

    model = DatasetModel()

    if 'user messages saved' not in st.session_state:
        st.session_state['user messages saved'] = False

    if 'rules' not in st.session_state:
        st.session_state['rules'] = ''

    if 'user messages' not in st.session_state: 
        st.session_state['user messages'] = []

    if 'system message' not in st.session_state:
        st.session_state['system message'] = ''
    
    if 'user message' not in st.session_state:
        st.session_state['user message'] = ''

    if 'user message and prompt saved' not in st.session_state:
        st.session_state['user message and prompt saved'] = False

    if 'dataset' not in st.session_state:
        st.session_state['dataset'] = []

    if 'latest dataset' not in st.session_state:
        st.session_state['latest dataset'] = []

    if 'dataset name' not in st.session_state:
        st.session_state['dataset name'] = ''

    if 'model_id' not in st.session_state:
        st.session_state['model_id'] = ''

    if 'model_name' not in st.session_state:
        st.session_state['model_name'] = ''

    if 'loaded api key' not in st.session_state:
        #st.session_state['loaded api key'] = model.load_api_key()
        st.session_state['loaded api key'] = ''

    if 'is valid openai key' not in st.session_state:
        st.session_state['is valid openai key'] = model.is_valid_openai_key(st.session_state['loaded api key'])

    st.sidebar.title("メニュー")

    if st.session_state['is valid openai key']:
        default_page = 'Dataset作成'
    else:
        default_page = '使い方'

    if 'page' not in st.session_state:
        st.session_state['page'] = default_page

    if st.session_state['is valid openai key']:
        if st.sidebar.button('Dataset作成'):
            st.session_state['page'] = 'Dataset作成'
        if st.sidebar.button('Dataset編集'):
            st.session_state['page'] = 'Dataset編集'
        if st.sidebar.button('ファインチューニング'):
            st.session_state['page'] = 'ファインチューニング'
    
    if st.sidebar.button('API設定'):
        st.session_state['page'] = 'API設定'
    if st.sidebar.button('使い方'):
        st.session_state['page'] = '使い方'

    if st.session_state['page'] == 'Dataset作成':
        auto_dataset_producter_page()
    elif st.session_state['page'] == 'Dataset編集':
        saved_dataset_page()
    elif st.session_state['page'] == 'ファインチューニング':
        fine_tuning_page()
    elif st.session_state['page'] == 'API設定':
        setting_api_page()
    elif st.session_state['page'] == '使い方':
        document_page()

if __name__ == "__main__":
    main()
