import os
import logging
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
import json
from .document_ingestor import IngestConfig, DocumentIngestor



class RAGPipeline:
    def __init__(
        self,
        doc_folder: str = "./data",
        model_name: str = "model_name1",
        embedding_model: str = "nomic-embed-text",
        vector_store_name: str = "simple-rag",
        chroma_path: str = "./chroma_store",
        uuid: str = "0",
        language: str = "en",
        memory_dir: str = "./memory",
        max_memory_length: int = 10,
        libre_office_path: str = None,
        ai_template: str = "you are a AI asistent ",
        system_prompt: str = "You are a multilingual AI assistant Always reason in English internally for clarity and precision. Then respond in the language specified: "

    ):
        self.doc_folder = doc_folder
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.vector_store_name = vector_store_name
        self.chroma_path = chroma_path
        self.chain = None
        self.uuid = uuid
        self.language = language
        self.MEMORY_DIR = memory_dir
        self.MAX_MEMORY_LENGTH = max_memory_length
        self._setup_logging()
        self.LibreOffice_path = libre_office_path
        self.ai_template = ai_template
        self.system_prompt = system_prompt

        self.llm = ChatOllama(model=self.model_name,temperature=0.3)
        self.vector_db = self._setup_vector_db()
        if self.vector_db:
            self.retriever = self._create_retriever()
            self.chain = self._create_chain()

    def load_memory(self, uuid):
        os.makedirs(self.MEMORY_DIR, exist_ok=True)
        filepath = os.path.join(self.MEMORY_DIR, f"{uuid}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_memory(self, uuid, prompt, answer):
        memory = self.load_memory(uuid)
        memory.append({"prompt": prompt, "answer": answer})
        memory = memory[-self.MAX_MEMORY_LENGTH:]
        filepath = os.path.join(self.MEMORY_DIR, f"{uuid}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

    def build_context_from_memory(self, uuid):
        memory = self.load_memory(uuid)
        memory_context = "\n".join(
            f"User: {m['prompt']}\nAI: {m['answer']}" for m in memory
        )
        return memory_context

    @staticmethod
    def _setup_logging():
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def _setup_vector_db(self):
        togle = True
        if self.LibreOffice_path is None:
            togle=False
        # Bygg vektordatabasen (eller öppna befintlig) via DocumentIngestor
        cfg = IngestConfig(
            doc_folder=self.doc_folder,
            chroma_path=self.chroma_path,
            vector_store_name=self.vector_store_name,
            embedding_model=self.embedding_model,
            chunk_size=1000,
            chunk_overlap=200,
            verbose=True,

            # Ange LibreOffice-path om den inte ligger i PATH
            soffice_path=self.LibreOffice_path,

            # Aktivera konverteringar/fallbacks

            convert_doc_with_soffice=togle,
            convert_ods_with_soffice=togle,
            convert_odt_with_soffice=togle,
            convert_odp_with_soffice=togle,
            convert_ppt_with_soffice=togle,

            # Rekursiv genomsökning av hela doc_folder-trädet
            recursive=True,
            follow_symlinks=False,
            # ignore_dirs kan justeras i DocumentIngestor om du vill
        )
        ingestor = DocumentIngestor(cfg)

        # Vill du peka ut specifika filer/URL:er (t.ex. Google Sheets) gör så här:
        # return ingestor.build_or_update_vector_db(files=[
        #     r"undermapp\minfil.pdf",
        #     "https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=0",
        # ])

        return ingestor.build_or_update_vector_db()

    def _create_retriever(self):
        query_prompt = PromptTemplate(
            input_variables=["question"],
            template=(self.ai_template
            )

        )

        return MultiQueryRetriever.from_llm(
            self.vector_db.as_retriever(), self.llm, prompt=query_prompt
        )

    def _create_chain(self):
        template = (
            "Answer the question based ONLY on the following context:\n"
            "{context}\n"
            "Question: {question}"
        )

        prompt = ChatPromptTemplate.from_template(template)
        return (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        if not self.chain:
            logging.error("Chain was not initialized.")
            return "Error: Chain not available."

        memory_context = self.build_context_from_memory(self.uuid)

        # Språkstyrning
        lang_directive = {
            "en": "Respond in English.",
            "sv": "Svara på svenska.",
            "da": "Svar på dansk.",
            "no": "Svar på norsk.",
            "fi": "Vastaa suomeksi.",
            "de": "Antworte auf Deutsch.",
            "fr": "Répondez en français.",
            "es": "Responde en español.",
            "pt": "Responda em português.",
            "it": "Rispondi in italiano.",
            "nl": "Antwoord in het Nederlands.",
            "pl": "Odpowiedz po polsku.",
            "cs": "Odpověz česky.",
            "sk": "Odpovedzte po slovensky.",
            "ro": "Răspunde în română.",
            "hu": "Válaszolj magyarul.",
            "ru": "Ответь по-русски.",
            "uk": "Відповідай українською.",
            "tr": "Türkçe cevap ver.",
            "el": "Απάντησε στα ελληνικά.",
            "bg": "Отговори на български.",
            "zh": "用中文回答。",
            "ja": "日本語で答えてください。",
            "ko": "한국어로 대답하세요.",
            "ar": "أجب باللغة العربية.",
            "hi": "हिंदी में उत्तर दें।",
            "th": "ตอบเป็นภาษาไทย.",
            "vi": "Trả lời bằng tiếng Việt.",
            "id": "Jawab dalam bahasa Indonesia."
        }.get(self.language.lower(), "Respond in the user's language.")

        system_prompt = (
            self.system_prompt + f'{lang_directive}'

        )

        formatted_prompt = (
            f"{system_prompt}\n\n"
            f"Previous conversation (for context only):\n{memory_context}\n\n"
            f"User question:\n{question}"
        )

        answer = self.chain.invoke(f"question: {formatted_prompt}")
        self.save_memory(self.uuid, question, answer)
        return answer