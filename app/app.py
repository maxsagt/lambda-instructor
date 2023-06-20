import json
from InstructorEmbedding import INSTRUCTOR

MODEL_PATH = './model/instructor-large'

def lambda_handler(event, context):
    model = INSTRUCTOR(MODEL_PATH)
    query = [event['sentence']]
    if event.get('instruction'): query.insert(0, event['instruction'])
    embeddings = model.encode(query)
    response = {
        'embeddings': embeddings.tolist(),# type: ignore
        'length': len(embeddings)
    }
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

# Uncomment to test locally without building the container first.
# print(lambda_handler({'sentence':'A sentence I want to get embeddings for.'},None))
