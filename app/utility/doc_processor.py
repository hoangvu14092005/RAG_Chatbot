from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config

class DocProcessor:
    def __init__(self):
        self.model_name = Config.EMBEDDING_MODEL

        self.embedder = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self.tokenizer,
            chunk_size=512,
            chunk_overlap=50
        )

    def split_text(self, text: str) -> list[str]:
        return self.text_splitter.split_text(text)

    def encode(self, texts: list[str] | str):
        if isinstance(texts, list):
            return self.embedder.embed_documents(texts)
        return self.embedder.embed_query(texts)