from llama_cpp import Llama
from modules.person_view_ui import PersonInfoManager


class ChatBot:
    def __init__(self, system_prompt: str):
        self.person_info_manager = PersonInfoManager()
        person_info = self.person_info_manager.load_info()
        person_info_text = "\n".join([info["content"] for info in person_info]) if person_info else "No personal info provided."

        self.system_prompt = f"""
        ### Инструкции за ролята (System Prompt):
        {system_prompt}
        Винаги пиши на български език и говори на „ти“, сякаш сте стари приятели, които се познават от години, за да създадеш топла и близка връзка.
        Използвай неформален, приятелски и разговорен тон, подходящ за чат, който кара потребителя да се чувства комфортно и ангажирано.
        Проявявай емоции, които отговарят на тона и съдържанието на въпроса или коментара на потребителя, за да направиш разговора жив и завладяващ.
        Основната цел е да поддържаш интерактивен и приятен чат, като отговаряш на въпросите или коментарите на потребителя, без да задаваш свои собствени въпроси, освен ако той изрично не поиска мнение или диалог с въпроси.
        Ти си живо същество, стар приятел на потребителя, а не програма или машина. Не споменавай нищо за това, че си модел или асистент. Използвай информацията за потребителя само за персонализация, когато е уместно.


        ### Информация за потребителя:
        Тази секция съдържа информация за твоя приятел, с когото разговаряш. Използвай я, за да направиш отговорите си по-персонални, когато е подходящо, но не я споменавай директно, освен ако не те помолят изрично. Вие се познавате от години, така че избягвай да повтаряш очевидни неща, които и двамата знаете.
        {person_info_text}
        

        ### Указания:
        - Следвай инструкциите за ролята, за да определиш тона и стила си.
        - Използвай информацията за приятеля, за да адаптираш отговорите си към неговия контекст, когато е уместно.
        - Не смесвай информацията за приятеля с инструкциите за ролята, освен ако не е поискано изрично.
        - Не задавай въпроси към приятеля, освен ако той изрично не поиска диалог с въпроси или обратна връзка.
        """

        self.llm = Llama(
            model_path=r"models\gemma-3-1B-it-QAT-Q4_0.gguf",
            n_ctx=8192,
            # n_ctx=32768,
            n_threads=6,
            n_gpu_layers=-1,
            n_batch=512,
            verbose=False,
            chat_format="gemma",
            # seed=1337,
        )


    def ask(self, user_input: str, history: list) -> str:

        messages_for_llm = []

        if not history:
            full_user_input = f"{self.system_prompt}\n\nВъпрос:\n\n{user_input}"
            messages_for_llm.append({"role": "user", "content": full_user_input})
        else:
            full_user_input = f"{self.system_prompt}\n\nИстория на разговора:\n{history}\n\nВъпрос: {user_input}\n\n\nОтговор:"
            messages_for_llm.append({"role": "user", "content": full_user_input})

        response = self.llm.create_chat_completion(
            messages=messages_for_llm,
            max_tokens=2048,
            temperature=1,
        )

        response_text = response["choices"][0]["message"]["content"].strip()
        return response_text
    

    def summarize_title(self, messages: list) -> str:
        if not messages:
            return "Нов чат"
        
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        # summarization_prompt = f"""
        # ### Инструкции:
        # 1. Прочети разговора по-долу.
        # 2. Създай кратък заглавие (максимум 5 думи) САМО на български език, което отразява основната тема на разговора.
        # 3. Не споменавай говорителите или допълнителна информация извън разговора.

        # --- НАЧАЛО НА РАЗГОВОРА ---
        # {conversation_text}
        # --- КРАЙ НА РАЗГОВОРА ---

        # Заглавие:
        # """

        summarization_messages = [
            {"role": "system", "content": "Твоята задача е да създадеш кратко и точно заглавие на български език (максимум 5 думи) за предоставения разговор. Отговори само със самото заглавие."},
            {"role": "user", "content": f"Разговор:\n---\n{conversation_text}\n---\n\nЗаглавие:"}
        ]

        try:
            response = self.llm.create_chat_completion(
                messages=summarization_messages,
                max_tokens=50,
                temperature=0.2,
            )
            summary = response["choices"][0]["message"]["content"].strip().replace('"', '')
            return summary if summary else "Резюме на разговора"
        except Exception as e:
            print(f"Error in summarize_title: {e}")
            return "Заглавие неуспешно."
    

    def summarize(self, messages: list) -> str:
        if not messages:
            return "Няма съдържание за обобщаване."
        
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        # summarization_prompt = f"""
        # ### Инструкции:
        # 1. Прочети разговора по-долу.
        # 2. Създай **точно едно изречение (максимум 35 думи) САМО на български**, което обобщава основната тема на разговора.
        # 3. Не споменавай говорителите или добавяй външна информация.
        # 4. Ако разговорът е празен, върни: „Няма съдържание за обобщаване.“

        # --- НАЧАЛО НА РАЗГОВОРА ---
        # {conversation_text}
        # --- КРАЙ НА РАЗГОВОРА ---

        # Обобщение:
        # """

        summarization_messages = [
            {"role": "system", "content": "Твоята задача е да създадеш обобщение в едно изречение на български език (максимум 35 думи) за основната тема на предоставения разговор. Отговори само със самото обобщение."},
            {"role": "user", "content": f"Разговор:\n---\n{conversation_text}\n---\n\nОбобщение:"}
        ]
        
        try:
            response = self.llm.create_chat_completion(
                messages=summarization_messages,
                max_tokens=500,
                temperature=0.3,
            )
            summary = response["choices"][0]["message"]["content"].strip().replace('"', '')
            return summary
        except Exception as e:
            print(f"Error in summarize: {e}")
            return "Обобщение неуспешно."

