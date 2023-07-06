import openai
from elasticsearch import AsyncElasticsearch
es = AsyncElasticsearch()

# Initialize elasticsearch instance or connection
es = Elasticsearch(
        hosts=["https://localhost:9200"],
        http_auth=('elastic', '+ocWHuuGH5wPcUG1*7O5'),
        verify_certs=False
    )

# Set the OpenAi key
openai.api_key = 'api-key-here'

# GPT-3 Prompt
prompt = "explain this information to me '{}'"
message = "Hello, World"

response = openai.Completion.create(
  engine="text-davinci-003",
  prompt=prompt.format(message),
  temperature=0.5,
  max_tokens=60
)

# Get the translated text answer from GPT-3
text_to_search = response['choices'][0]['text'].strip()

# Elasticsearch search query
body = {
    "query": {
        "match": {
            "content": {
                "query": text_to_search,
                "operator" : "or",
                "fuzziness": "AUTO"
            }
        }
    }
}

res = es.search(index="your_index", body=body)

# Print the search result.
for hit in res['hits']['hits']:
    print(f'Found result {hit["_source"]}')
