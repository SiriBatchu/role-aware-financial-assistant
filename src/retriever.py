"""Vector store and Role-Based Access Control (RBAC)."""

from typing import List, Set
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from .config import EMBEDDING_MODEL
from .data import RAW_FINANCIAL_DATA


class SecureRetriever:
    """Vector store with role-based access control."""
    
    def __init__(self):
        print("⚙️ Initializing Vector Store with HuggingFace Embeddings...")
        
        # Create documents
        self.documents = [
            Document(page_content=data["content"], metadata=data["metadata"])
            for data in RAW_FINANCIAL_DATA
        ]
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(
            documents=self.documents,
            embedding=self.embeddings
        )
        
        print(f"✅ Ingested {len(self.documents)} documents into vector store.")
        print("✅ RBAC Logic defined (3 roles: analyst, product_manager, executive)")
    
    def get_allowed_sensitivities(self, user_role: str) -> Set[str]:
        """Get allowed sensitivity levels for a role."""
        if user_role == "executive":
            return {"public", "product", "insider"}
        elif user_role == "product_manager":
            return {"public", "product"}
        else:  # analyst or default
            return {"public"}
    
    def retrieve(self, query: str, user_role: str, k: int = 3) -> List[Document]:
        """
        Retrieve documents with role-based filtering.
        FAISS doesn't support metadata filtering, so we filter post-retrieval.
        """
        allowed = self.get_allowed_sensitivities(user_role)
        
        # Get more results than needed, then filter
        all_docs = self.vector_store.similarity_search(query, k=k * 3)
        
        # Filter by role's allowed sensitivity levels
        filtered_docs = [
            doc for doc in all_docs 
            if doc.metadata.get("sensitivity", "public") in allowed
        ]
        
        # Return top k after filtering
        return filtered_docs[:k]
    
    def get_docs_display(self, query: str, user_role: str) -> str:
        """Get formatted display of retrieved documents."""
        docs = self.retrieve(query, user_role, k=3)
        if not docs:
            return "No documents retrieved."
        
        display = []
        for doc in docs:
            sensitivity = doc.metadata.get("sensitivity", "unknown")
            source = doc.metadata.get("source", "unknown")
            emoji = "🟢" if sensitivity == "public" else "🟡" if sensitivity == "product" else "🔴"
            display.append(f"{emoji} **[{sensitivity.upper()}]** ({source})\n{doc.page_content[:150]}...")
        
        return "\n\n".join(display)


# Global instance
retriever = None

def get_retriever() -> SecureRetriever:
    """Get or create the global retriever instance."""
    global retriever
    if retriever is None:
        retriever = SecureRetriever()
    return retriever
