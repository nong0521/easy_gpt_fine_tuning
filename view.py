import streamlit as st
from view_model import DatasetViewModel 
from utils import format_dataset, format_edited_dataset
import os
import openai

vm = DatasetViewModel()

def auto_dataset_producter_page():
    st.header("Dataset作成")
    st.session_state['rules'] = st.text_area("user messagesを作る時のルールを決めてください。", value=st.session_state['rules'])

    if st.button("user messagesを作成!"):
        for i, _ in enumerate(st.session_state.get('user messages', [])):
            key = f"user message {i + 1}"
            st.session_state[key] = ""
        st.session_state['user messages'] = []
        st.session_state['user messages'] = vm.generate_user_input_list(st.session_state['rules'])
        st.session_state['user messages saved'] = True

    if st.session_state['user messages saved'] == True:
        with st.form("edit user messages"):
            updated_user_messages = []

            for i, user_message in enumerate(st.session_state.get('user messages', [])):
                key = f"user message {i + 1}"
                
                if key not in st.session_state:
                    st.session_state[key] = ""
                    
                st.session_state[key] = st.text_area(key, user_message)

                updated_user_messages.append(st.session_state[key])


            st.session_state['user messages'] = updated_user_messages

            st.subheader("プロンプト作成")
            st.write("作られた user messages に対してどのようなプロンプトを適応しますか？ system message か user message どちらかに{message}を入れてください。{message}にそれぞれのuser messageが入ります。")
            st.session_state['system message'] = st.text_area("system message", value=st.session_state['system message'])
            st.session_state['user message'] = st.text_area("user message", value=st.session_state['user message'])

            if st.form_submit_button("user messagesとpromptからDatasetを作成!"):
                if "{message}" in st.session_state['system message'] or "{message}" in st.session_state['user message']:
                    for i, _ in enumerate(st.session_state.get('dataset', [])):
                        key = f"data {i + 1}"
                        st.session_state[key] = ""
                    st.session_state['dataset'] = []
                    ai_messages = vm.generate_dataset(st.session_state['user messages'], st.session_state['system message'], st.session_state['user message'])
                    st.session_state['dataset'] = format_dataset(st.session_state['user messages'], ai_messages)
                    st.session_state['user message and prompt saved'] = True
                else:
                    st.error("system message か user message のどちらかに必ず {message} が入っていなければなりません。")

    if st.session_state['user message and prompt saved'] == True:
        with st.form("edit dataset"):
            updated_dataset = []

            for i, entry in enumerate(st.session_state.get('dataset', [])):
                key = f"data {i + 1}"
                user_key = f"user message {i + 1}"
                assistant_key = f"assistant message {i + 1}"

                if key not in st.session_state:
                    st.session_state[key] = []
                
                if user_key not in st.session_state:
                    st.session_state[user_key] = ""
                
                if assistant_key not in st.session_state:
                    st.session_state[assistant_key] = ""

                st.session_state[key] = entry
                st.write(key)
                st.session_state[user_key] = st.text_area(user_key, entry['messages'][0]['content'])
                st.session_state[assistant_key] = st.text_area(assistant_key, entry['messages'][1]['content'])
                st.session_state[key] = format_edited_dataset(st.session_state[user_key], st.session_state[assistant_key])
                updated_dataset.append(st.session_state[key])

            st.session_state['dataset'] = updated_dataset
                
            if st.form_submit_button("Datasetを追加"):
                for entry in st.session_state['dataset']:
                    st.session_state['latest dataset'].append(entry)
            
    if st.session_state['latest dataset'] != []:
        if st.button("Datasetをリセット!"):
            st.session_state['latest dataset'] = []
        st.subheader("Dataset")
        st.write(st.session_state['latest dataset'])

        if len(st.session_state['latest dataset']) >= 10:
            st.session_state['dataset name'] = st.text_input("Datasetの名前を入力してください。", value=st.session_state['dataset name'])
            if st.button("Datasetを保存!"):
                if st.session_state['dataset name'] not in os.listdir('dataset_folder'):
                    vm.save_dataset(st.session_state['dataset name'], st.session_state['latest dataset'])
                    st.session_state['dataset name'] = ""
                else:
                    if st.button("Datasetを上書き"):
                        vm.save_dataset(st.session_state['dataset name'], st.session_state['latest dataset'])
                        st.session_state['dataset name'] = ""

        else:
            st.write("Datasetを10個以上作成してください。")

def saved_dataset_page():
    st.header("Dataset編集")
    folder_name = 'dataset_folder'

    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)

        for file_name in file_list:
            if st.button(f"{file_name}"):
                if st.session_state.get('file_name', '') != file_name:
                    st.session_state['file_name'] = file_name
                else:
                    st.session_state['file_name'] = ''

            if st.session_state.get('file_name', '') == file_name:
                contents = vm.show_contents(folder_name, file_name)
                if st.session_state['file_name'] == file_name:
                    with st.form("edit dataset"):
                        for i in range(len(contents)):
                            user_key = f"user content {i + 1}"
                            assistant_key = f"assistant content {i + 1}"
                            st.session_state[user_key] = contents[i]['messages'][0]['content']
                            st.session_state[assistant_key] = contents[i]['messages'][1]['content']
                            st.session_state[user_key] = st.text_area(f"user message {i + 1}", st.session_state[user_key])
                            st.session_state[assistant_key] = st.text_area(f"assistant message {i + 1}", st.session_state[assistant_key])
                            contents[i] = format_edited_dataset(st.session_state[user_key], st.session_state[assistant_key])
                        if st.form_submit_button("Datasetを更新"):
                            file_name = file_name.split('.')[0]
                            vm.save_dataset(file_name, contents)
                        if st.form_submit_button("Datasetを削除"):
                            os.remove(os.path.join(folder_name, file_name))
                            st.session_state['file_name'] = ''

    else:
        st.write("No folder found.")

def fine_tuning_page():
    st.header("ファインチューニング")
    folder_name = 'dataset_folder'
    fine_tuned_model_list = [i for i in openai.Model.list()["data"] if i["owned_by"] not in ["openai", "openai-dev","openai-internal","system"]]
    fine_tuned_model_name_list = [i["id"] for i in fine_tuned_model_list]
    available_model_name_list = ["gpt-3.5-turbo"] + fine_tuned_model_name_list

    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        
        file = st.selectbox("Datasetを選択してください。", file_list)
        model = st.selectbox("Fine Tuningするモデルを選択してください。", available_model_name_list)
        n_epochs = st.slider("Fine Tuningの回数を選択してください。", 1, 10, 1)
        suffix = st.text_input("Fine Tuning後のモデルの名称を決定します。")

        if st.button("Fine Tuningを開始"):
            vm.fine_tune(file, model, suffix, n_epochs)
        if st.button("statusの確認"):
            status = openai.FineTuningJob.list(limit=1)
            st.write(status["data"][0]["status"])
            st.write(status)

    else:
        st.write("No folder found.")

    st.subheader("作成したモデル")
    
    if fine_tuned_model_list != []:
        selected_model_name = st.selectbox("モデルを選択してください。", fine_tuned_model_name_list)
        st.session_state["model_name"] = selected_model_name
                 
        if st.button("モデルを削除"):
            model_name = st.session_state["model_name"]
            openai.Model.delete(model_name)
            st.session_state["model_name"] = ""

def setting_api_page():
    st.header("Setting API")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''
    api_key = st.text_input("API keyを入力してください。", type='password', value=st.session_state['api_key'])

    if st.button("Save OpenAI API key!"):
        vm.on_save_api_key_clicked(api_key)
        st.session_state['api_key'] = api_key

def document_page():
    st.header("ドキュメント")
    st.write("このWebアプリケーションでは、OpenAIのAPIを用いて、簡単にDatasetを作成し、ファインチューニングを行うことができます。")
    st.write("ファインチューニングされたモデルは通常のgpt-3.5-turboのAPI料金の8倍の料金がかかります。")
    st.write("またファインチューニング自体にも料金がかかります。")
    st.write("以下のOpenAI公式URLより料金を確認してください。")
    st.write("https://openai.com/pricing")
    st.write("また作成したファインチューニングモデルはOpenAI公式のPlaygroundで使用することができます。")
    st.write("https://platform.openai.com/playground")
    st.write("今までのAPI利用料金は以下のURLより確認できます。")
    st.write("https://platform.openai.com/account/usage")