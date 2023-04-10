import pinecone

class VectorDb:

    def __init__(self, api_key, env) -> None:
        pinecone.init(api_key=api_key,environment=env)

    def upsert(self, indexName, vectors):
        index = pinecone.Index(indexName)
        
        upsert_response = index.upsert(
            vectors=vectors
        )

        print(upsert_response)
        return upsert_response
    
    def query(self, indexName, vector, num_results=10):
        index = pinecone.Index(indexName)

        query_response = index.query(
            top_k=num_results,
            include_values=True,
            include_metadata=True,
            vector=vector,
        )
            
        return query_response