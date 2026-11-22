import chromadb

client = chromadb.PersistentClient(path="storage/chroma_db")

for item in client.list_collections():
    name = item if isinstance(item, str) else item.name
    print(name, "->", client.get_collection(name).count(), "chunks")