import ollama
import faiss
import numpy as np
from pathlib import Path
import PyPDF2
from docx import Document


class SimpleRAG:
    def __init__(self, file_path, llm_model="tinyllama:latest", embed_model="nomic-embed-text"):
        self.file_path = file_path
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.index = None
        self.chunks = []
        self.load_and_index()

    def extract_text(self):
        """Extract text from TXT, PDF, or Word document"""
        file_ext = Path(self.file_path).suffix.lower()

        if file_ext == '.txt':
            return Path(self.file_path).read_text()

        elif file_ext == '.pdf':
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text

        elif file_ext == '.docx':
            doc = Document(self.file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text

        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def load_and_index(self):
        """Load document, split into chunks, and create FAISS index"""
        try:
            text = self.extract_text()
            self.chunks = [text[i:i + 500] for i in range(0, len(text), 500)]

            # Create embeddings
            embeddings = [ollama.embeddings(model=self.embed_model, prompt=chunk)['embedding'] for chunk in self.chunks]
            embeddings = np.array(embeddings).astype('float32')

            # Initialize FAISS index
            dimension = len(embeddings[0])
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)

        except Exception as e:
            print(f"Error processing document: {e}")
            raise

    def query(self, question, k=3):
        """Query the LLM with retrieved context"""
        try:
            # Get query embedding
            query_embed = np.array([ollama.embeddings(model=self.embed_model, prompt=question)['embedding']]).astype(
                'float32')

            # Search for top-k relevant chunks
            distances, indices = self.index.search(query_embed, k)
            context = "\n".join([self.chunks[i] for i in indices[0]])

            # Create prompt with context
            prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer concisely:"

            # Query LLM
            response = ollama.generate(model=self.llm_model, prompt=prompt)
            return response['response']

        except Exception as e:
            print(f"Error generating answer: {e}")
            return "Error generating response."


def main():
    # aq nebismier files avtvirtavt pdf txt da docxs
    rag = SimpleRAG("input.txt")#txt, .pdf, or .docx

    question = "What is the main topic of the document?"
    answer = rag.query(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()