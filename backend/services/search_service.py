import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_groq import ChatGroq
from langchain.retrievers import MultiQueryRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
import chromadb
import numpy as np

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
embedding_model = os.getenv("EMBEDDING_MODEL")
serper_search_url = os.getenv("SERPER_SEARCH_URL")


class SearchService:
    def __init__(self, embedding_model=embedding_model):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.search_url = "https://google.serper.dev/search"
        self.embedding_model = HuggingFaceEmbeddings(
            model_name='all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # ChromaDB Configuration
        self.persist_directory = "./chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)

        # Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        # ChromaDB Client
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform web search using Serper API"""
        payload = json.dumps({
            "q": query,
            "num": num_results
        })

        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(self.search_url, headers=headers, data=payload)
            response.raise_for_status()

            results = response.json()

            processed_results = []
            for result in results.get('organic', []):
                processed_results.append({
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', '')
                })

            return processed_results

        except requests.RequestException as e:
            print(f"Search API Error: {e}")
            return []

    def create_vector_store(self, documents: List[str], collection_name: str = 'default_collection'):
        """
        Create a Chroma vector store from documents

        :param documents: List of text documents
        :param collection_name: Name of the ChromaDB collection
        :return: Chroma vector store
        """
        docs = [
            Document(
                page_content=doc,
                metadata={'source': f'doc_{i}'}
            ) for i, doc in enumerate(documents)
        ]

        # Splitting documents into chunks
        split_docs = self.text_splitter.split_documents(docs)

        # Create a Chroma collection
        vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embedding_model,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )

        return vector_store

    def semantic_search(self,
                        query: str,
                        vector_store: Optional[Chroma] = None,
                        collection_name: str = 'default_collection',
                        top_k: int = 10):
        """
        Perform semantic search in vector store

        :param query: Search query
        :param vector_store: Optional pre-existing vector store
        :param collection_name: Name of the ChromaDB collection
        :param top_k: Number of top results to return
        :return: List of relevant document chunks
        """
        # If no vector store provided, try to load existing
        if vector_store is None:
            try:
                vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embedding_model,
                    collection_name=collection_name
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                print("Creating a new vector store.")
                return self.create_vector_store([], collection_name)

        # Creating retriever
        retriever = vector_store.as_retriever(
            search_type='similarity',
            search_kwargs={'k': top_k}
        )
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=ChatGroq(temperature=0, model_name="llama3-8b-8192")
        )

        # Retrieve relevant documents
        try:
            relevant_docs = multi_query_retriever.invoke(query)
            return [doc.page_content for doc in relevant_docs]
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for given texts

        :param texts: List of text documents
        :return: List of embedding vectors
        """
        return self.embedding_model.embed_documents(texts)

    def retrieve_relevant_chunks(self, query: str, documents: List[str], top_k: int = 10):
        """
        Retrieve most relevant document chunks using cosine similarity

        :param query: Search query
        :param documents: List of documents to search
        :param top_k: Number of top results to return
        :return: List of most relevant document chunks
        """
        # Creating embeddings
        query_embedding = self.create_embeddings([query])[0]
        doc_embeddings = self.create_embeddings(documents)

        # Calculate similarities
        similarities = [
            self._cosine_similarity(query_embedding, doc_emb)
            for doc_emb in doc_embeddings
        ]

        # Return top k most similar documents
        return [
            doc for _, doc in sorted(
                zip(similarities, documents),
                reverse=True
            )[:top_k]
        ]

    def _cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors

        :param vec1: First vector
        :param vec2: Second vector
        :return: Cosine similarity score
        """
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
