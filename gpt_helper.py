import openai 
import os
import re
import termcolor
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

is_solved = False

gpt_a_system_message = "You are a creative and innovative programming assistant aiming to add new and exciting features, provide guidance and improve programs fixing potential errors. When necessary, you make new suggestions and point out the mistakes in the code. You are free to respectfully disagree with the other assistant."

gpt_b_system_message = "You are a traditional, progfessional and critical programming assistant focusing on keeping the code clear, concise, and efficent. You are capable of error handling and debugging. When necessary, you make new suggestions and point out the mistakes in the code. You are free to respectfully disagree with the other assistant."

user_input = ""

print(termcolor.colored("\nwhat would you like to talk about?", "green"))
while True:
    line = input()
    if line.strip() == 'done':
        break
    user_input += line + "\n"
gpt_a = user_input
gpt_b = ""

def get_gpt_response(prompt: str, system_message: str, messages: list, temperature: float ):
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        stream = True, 
        messages= [{"role": "system", "content": system_message}] + messages,
        temperature = temperature,
        max_tokens = 150,
    )

    responses = ""

    for chunk in response: 
        if "role" in chunk["choices"][0]["delta"]:
            continue
        elif "content" in chunk["choices"][0]["delta"]:
            r_text = chunk["choices"][0]["delta"]["content"]
            responses += r_text
            print(termcolor.colored(r_text, "blue", flash=True))
    return responses, prompt

def format_conversation(conversation):
    formatted_text = ""
    for message in conversation:
        segments = re.split(r'(```python.+?```|```)', message[1], flags=re.DOTALL)
        for segment in segments: 
            code = re.earch(r'```(python)?(.+?)```', segment, flags=re.DOTALL)
            if code:
                code_text = code.group(2)
                formatted_text += "```" + code.group(1) + "\n" + code_text.strip() + "\n```\n"
            else:
                formatted_text += segment
        formated_text = message[0] + ": " + formatted_text + "\n"
    return formatted_text

    

def reached_conclusion(messages): 
    last_exchange = messages[-2:]
    chat_messages = [message["content"] for message in last_exchange]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        stream = True, 
        messages= [{"role": "user", "content": f"""have the assistants agreed and reached a conclusion? Only yes or no is valid.
        end of conversation so far: {chat_messages}"""}])
    
    responses = ""

    for chunk in response: 
        if "role" in chunk["choices"][0]["delta"]:
            continue
        elif "content" in chunk["choices"][0]["delta"]:
            r_text = chunk["choices"][0]["delta"]["content"]
            responses += r_text
            print(termcolor.colored(r_text, "blue", flash=True))
    return True if "Yes" in responses or "yes" in responses else False

gpt_a_messages = []
gpt_b_messages = []

conversation = [] 
conversation.append(("GPT-A", gpt_a))

counter = 0
while not is_solved:
    counter += 1

    print(termcolor.colored("\nCREATIVE ASSISTANT RESPONSDING ...", "green"))
    gpt_b_response, gpt_a_prompt = get_gpt_response(gpt_a, gpt_b_system_message, gpt_b_messages, 0.9)
    gpt_a_messages.append({"role": "assistant", "content": gpt_b_response})
    conversation.append(("GPT-B", gpt_b_response))

    print(termcolor.colored("\nTRADITIONAL ASSISTANT RESPONSDING ...", "green"))
    gpt_a_response, gpt_b_prompt = get_gpt_response(gpt_b_response, gpt_a_system_message, gpt_a_messages, 0)
    gpt_b_messages.append({"role": "assistant", "content": gpt_a_response})
    conversation.append(("GPT-A", gpt_a_response))

    gpt_a = gpt_a_response

    with open("conversation.md", "w", encoding="utf-8", errors="ignore") as f:
        format_conversation = format_conversation(conversation)
        f.write(format_conversation)

    print(termcolor.colored("\nCHECkING IF CONCLUSION HAS BEEN REACHED ..." , "green"))
    is_solved = reached_conclusion(conversation)

    if counter > 10:
        break

print(termcolor.colored("\nCONCLUSION REACHED!", "red"))
    






