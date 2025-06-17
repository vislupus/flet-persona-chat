from llama_cpp import Llama

llm = Llama(
    model_path=r"models\BgGPT-Gemma-2-2B-IT-v1.0.Q5_K_M.gguf", 
    n_ctx=2048,
    n_threads=6,
    n_gpu_layers=-1,
    chat_format="gemma",
    verbose=False
)

# prompt = "Напиши кратка история за робот, който мечтае да стане художник."

def ask_bot(prompt):
    # response = llm(prompt=prompt, max_tokens=512)
    # return response['choices'][0]['text'].strip()
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "Ти си мил асистент, който говори на български."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        # temperature=0.7
    )
    return response['choices'][0]['message']["content"].strip()

# print(ask_bot(prompt))
