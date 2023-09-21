def format_dataset(human_messages, ai_messages):
    if len(human_messages) != len(ai_messages):
        raise ValueError("The lengths of human_messages and ai_messages must be the same.")
    
    dataset = []
    for h_msg, a_msg in zip(human_messages, ai_messages):
        turn_data = {"messages":
            [
                {
                    "role": "user",
                    "content": h_msg
                },
                {
                    "role": "assistant",
                    "content": a_msg
                }
            ]
        }
        dataset.append(turn_data)
    
    return dataset

def format_edited_dataset(user_text, assistant_text):
    formated_data = {"messages":
            [
                {
                    "role": "user",
                    "content": user_text
                },
                {
                    "role": "assistant",
                    "content": assistant_text
                }
            ]
        }
    return formated_data

