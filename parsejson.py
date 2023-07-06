import os
import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError

# Step 1: Parse the JSON Files
def load_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict):
                            data = [data]  # Wrap dictionary in a list
                        yield data
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {file}: {e}")
                    except UnicodeDecodeError as e:  # Handle UnicodeDecodeError
                        print(f"Error decoding Unicode in {file}: {e}")


# Step 2: Preprocess the Data
# This will depend on your specific needs, but might involve cleaning the data,
# normalizing location names, converting timestamps to a standard format, etc.

# Step 3: Vectorize the Data
# This will also depend on your specific needs, but might involve converting text into word vectors or embeddings,
# and/or normalizing numerical data.

# Step 4: Create an Elasticsearch Index
def create_index(es, index_name):
    try:
        es.indices.create(index=index_name, ignore=400)
    except RequestError as e:
        print(f"Error creating index {index_name}: {e}")

# Step 5: Index the Data
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def index_data(es, index_name, data):
    actions = [
        {
            "_index": index_name,
            "_source": flatten_dict(item)  # Flatten the item
        }
        for item in data
    ]
    success, failed = helpers.bulk(es, actions, raise_on_error=False)

    print(f"Successfully indexed {success} documents.")
    print(f"Failed to index {len(failed)} documents.")
    for i, fail in enumerate(failed, start=1):
        print(f"Error {i}: {fail}")

def main():
    directory = 'data/Semantic Location History'
    index_name = 'my_index'

    es = Elasticsearch(
        hosts=["https://localhost:9200"],
        http_auth=('username', 'password'),
        verify_certs=False
    )

    create_index(es, index_name)

    for data in load_json_files(directory):
        index_data(es, index_name, data)

if __name__ == '__main__':
    main()
