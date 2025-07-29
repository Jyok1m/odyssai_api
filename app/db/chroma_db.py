import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv, find_dotenv
from uuid import uuid4

# Load env variables
load_dotenv(find_dotenv())


class ChromaManager:
    """
    Utility class to manage ChromaDB Cloud duties via langchain.
    """

    def __init__(self, embedding_model="text-embedding-3-small"):
        """
        Initializes the ChromaDB Cloud Client.
        Configured to use an OpenAI model. Defaults to "text-embedding-3-small".
        """
        for key in ["CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE"]:
            if not os.getenv(key):
                raise EnvironmentError("Missing an environnement variable.")

        self.__embedding_function = OpenAIEmbeddings(model=embedding_model)
        self.__client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE"),
        )

    def __instanciate_collection(self, collection_name: str):
        """
        Gets or creates a collection in ChromaDB Cloud.
        """
        return Chroma(
            client=self.__client,
            embedding_function=self.__embedding_function,
            collection_name=collection_name,
        )

    def add_documents(self, collection_name: str, documents: list[Document]):
        """
        Adds documents to a collection in ChromaDB Cloud.
        """
        if not collection_name or not isinstance(collection_name, str):
            raise TypeError("Collection name must be a non-empty string.")
        for document in documents:
            if not isinstance(document, Document):
                raise TypeError(
                    "Each document must be an instance of langchain Document."
                )

        collection = self.__instanciate_collection(collection_name)
        return collection.add_documents(documents)

    def query_documents(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        search_type: str = "mmr",
    ):
        """
        Queries documents in a collection in ChromaDB Cloud based on a query string.
        This uses a retriever to find the most relevant documents.
        """
        if not collection_name or not isinstance(collection_name, str):
            raise TypeError("Collection name must be a non-empty string.")
        if not query or not isinstance(query, str):
            raise TypeError("Query must be a non-empty string.")
        if not isinstance(n_results, int) or n_results <= 0 or n_results > 100:
            raise ValueError("n_results must be an integer between 1 and 100.")
        if search_type not in ["mmr", "similarity"]:
            raise ValueError("search_type must be either 'mmr' or 'similarity'.")

        search_kwargs: dict[str, int | float] = {"k": n_results}

        if search_type == "mmr":
            search_kwargs["lambda_mult"] = 0.7

        collection = self.__instanciate_collection(collection_name)
        retriever = collection.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

        return retriever.invoke(input=query)

    def query_context_by_similarity(
        self, collection_name: str, world_name: str, k=10, step_type=""
    ):
        collection = self.__instanciate_collection(collection_name)

        if step_type == "world" or collection_name == "worlds":
            query_result = collection.get(where={"world": world_name})
            if not query_result["documents"]:
                return None
            else:
                world_id = query_result["metadatas"][0]["world_id"]
                context = "\n".join(query_result["documents"])
                return {"world_id": world_id, "context": context}

        retriever = collection.as_retriever(search_type="mmr", search_kwargs={"k": k})
        results = retriever.invoke(f"Important lore entries from world {world_name}")
        context = "\n".join([doc.page_content for doc in results])
        world_id = results[0].metadata["world_id"] if results else str(uuid4())

        return {"world_id": world_id, "context": context}
