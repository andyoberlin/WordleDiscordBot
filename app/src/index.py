# from nacl.signing import VerifyKey
# from nacl.exceptions import BadSignatureError

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': 'Hello'
    }