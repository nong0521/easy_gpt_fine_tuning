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
            
    if not os.path.exists('dataset_folder'):
        os.mkdir('dataset_folder')

    if st.session_state['latest dataset'] != []:
        if st.button("Datasetをリセット!"):
            st.session_state['latest dataset'] = []
        st.subheader("Dataset")
        st.write(st.session_state['latest dataset'])

        if len(st.session_state['latest dataset']) >= 10:
            st.session_state['dataset name'] = st.text_input("Datasetの名前を入力してください。", value=st.session_state['dataset name'])
            
            if st.button("Datasetを保存!"):
                try:
                    if st.session_state['dataset name'] not in os.listdir('dataset_folder'):
                        vm.save_dataset(st.session_state['dataset name'], st.session_state['latest dataset'])
                        st.session_state['dataset name'] = ""
                    else:
                        if st.button("Datasetを上書き"):
                            vm.save_dataset(st.session_state['dataset name'], st.session_state['latest dataset'])
                            st.session_state['dataset name'] = ""
                except Exception as e:
                    st.write(f"An error occurred: {e}")

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
                            st.experimental_rerun()
                        if st.form_submit_button("Datasetを削除"):
                            os.remove(os.path.join(folder_name, file_name))
                            st.session_state['file_name'] = ''
                            st.experimental_rerun()

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
            st.experimental_rerun()

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
            st.experimental_rerun()

def setting_api_page():
    st.header("Setting API")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''
    api_key = st.text_input("API keyを入力してください。", type='password', value=st.session_state['api_key'])

    if st.button("Save OpenAI API key!"):
        vm.on_save_api_key_clicked(api_key)
        st.session_state['api_key'] = api_key

def document_page():
    st.title("使い方")
    st.write("このWebアプリケーションでは、OpenAIのAPIを用いて、簡単にDatasetを作成し、ファインチューニングを行うことができます。")
    st.header("ファインチューニングとは？")
    st.write("""ここで行うファインチューニングとは、GPTをあるタスクに特化させることを指します。
例えば、GPTを好きな語尾をござるにしたり、画像生成用のプロンプトを作るようにしたりできます。
""")

    st.header("このアプリケーションの使い方")
    st.subheader("Step1: API keyの設定")
    st.write("サイドメニューのAPI設定をクリックし、OpenAIのAPI keyを入力してください。")
    st.write("API keyはOpenAIの公式サイトより取得できます。https://platform.openai.com/overview")
    st.write("""アカウントを作成し、自分の名前のマークの入ったボタンをクリックし、その中の"View API keys"をクリックします。https://platform.openai.com/account/api-keys""")
    st.write("""Create new secret keys"を押して、API keyを作成してください。作成したAPI keyをコピーして、どこかに保存しておいてください。""")
    st.write("また作成したAPI keyは誰にも教えないようにして下さい。")
    st.write("""続いて左のサイドメニューより"Billing"をクリックして"Start payment plan"をクリックして、支払い方法を登録してください。https://platform.openai.com/account/billing/overview""")
    st.write("""Billing"の中の"Usage limits"より、1か月のAPI利用料金の上限を設定することができます。https://platform.openai.com/account/billing/limits""")
    st.write("""左のサイドメニューの"Usage"より、今までのAPI利用料金を確認することができます。https://platform.openai.com/account/usage""")
    st.write("ファインチューニングされたモデルは通常のgpt-3.5-turboのAPI料金の8倍の料金がかかります。")
    st.write("またファインチューニング自体にも料金がかかります。")
    st.write("以下のOpenAI公式URLより料金を確認してください。")
    st.write("https://openai.com/pricing")
    st.write()
    st.subheader("Step2: Datasetの作成")
    st.write("サイドメニューのDataset作成をクリックし、user messagesのルールを決めてください。")
    st.write("ex.)日本語、一人称が朕")
    st.write()
    st.write("すると、user messagesが自動で作成されますので、それを確認して自分好みに編集してください。")
    st.write("編集が終わったら、どのような返答をしてほしいか考えて、system messageとuser messageを入力してください。どちらかにかならず{message}を入れてください。")
    st.write("{message}にはuser messagesが入ります。")
    st.write("ex.)")
    st.write("system message: userが天皇陛下であるように会話に応答します。")
    st.write("user message: {message}")
    st.write()
    st.write("これでDatasetの一案が提案されます。これも自分好みに編集してください。")
    st.write("Datasetを追加ボタンを押すと、Datasetが追加されます。")
    st.write("さらにDatasetを追加したい場合はStep2を上から繰り返してください。")
    st.write("Datasetを10個以上作成したら、Datasetの名前を入力して、Datasetを保存ボタンを押してください。")
    st.write("作ったDatasetはDataset編集で編集することができます。")
    st.write()
    st.subheader("Step3: ファインチューニング")
    st.write("サイドメニューのファインチューニングをクリックし、ファインチューニングするモデルを選択してください。")
    st.write("使用するDatasetを選択し、ファインチューニングするモデルを選択してください。")
    st.write("ファインチューニングの回数を選択してください。これで学習回数が決定します。")
    st.write("ファインチューニング後のモデルの名称を入力してください。")
    st.write("ファインチューニングを開始ボタンを押すと、ファインチューニングが開始されます。")
    st.write("ファインチューニングには10分以上時間がかかることもありますので、しばらくお待ちください。")
    st.write("statusの確認ボタンを押すと現在の状態を確認でき、runnningであれば実行途中、succeededであれば実行完了です。")
    st.write("モデルを削除ボタンで選択したモデルを削除することができます。")
    st.write()
    st.subheader("Step4: Playgroundで利用する")
    st.write("作成したファインチューニングモデルはOpenAI公式のPlaygroundで使用することができます。https://platform.openai.com/playground")
    st.write("右側のModel選択から使用するファインチューンされたモデルを選択すると、Playgroundで使用することができます。")