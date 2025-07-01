from langchain_community.chat_models import ChatLlamaCpp
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory


class ChatBot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.llm = ChatLlamaCpp(
            model_path=r"models\gemma-3-1B-it-QAT-Q4_0.gguf",
            max_tokens=2048,
            model_kwargs={
                "n_ctx": 32768,
                "n_threads": 6,
                "n_gpu_layers": -1,
                "n_batch": 64,
                "temperature": 0.7,
                "chat_format": "gemma",
            },
            verbose=False,
        )

        self.prompt = (
            ChatPromptTemplate.from_messages([
                ("user", "{system_prompt}"),
                MessagesPlaceholder("history"),
                ("user", "{input}")
            ])
            .partial(system_prompt=self.system_prompt)
        )

        self._history = InMemoryChatMessageHistory()

        base_chain = self.prompt | self.llm

        self.chain = RunnableWithMessageHistory(
            base_chain,
            lambda _: self._history,
            input_messages_key="input",
            history_messages_key="history",
        )

        # print(f"✅ Създаден бот с промпт: {self.system_prompt}")


    def ask(self, user_input: str) -> str:
        response = self.chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "ram"}},
        )
        return response.content.strip()
    

    def summarize(self, messages: list) -> str:
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        summarization_prompt = f"""
        Read the following conversation and summarize it in a single, concise sentence in Bulgarian.
        The summary should capture the main topic of the discussion.

        Conversation:
        ---
        {conversation_text}
        ---

        Summary (one sentence):
        """
        
        response = self.llm.invoke(summarization_prompt)
        
        summary = response.content.strip()
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]
            
        return summary

