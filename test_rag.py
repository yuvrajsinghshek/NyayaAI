from ai.rag.retriever import retrieve_chunks
from ai.rag.generator import generate_answer

question = "What is digital arrest scam?"
chunks   = retrieve_chunks(question)
result   = generate_answer(question, chunks)

print("\nQuestion:", question)
print("\nAnswer:", result["answer"])
print("\nSource:", result["source"])
print("\nCategory:", result["category"])
