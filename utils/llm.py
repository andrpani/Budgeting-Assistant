import base64
from mimetypes import guess_extension, guess_type
from langchain_core.messages import HumanMessage
from typing import IO, Literal


class MultimodalMessage(HumanMessage):
    def __init__(self, name: str, data: IO[bytes], type: Literal['image', 'file', 'text'], 
                 prompt: str = '', mime_type: str = ''):
        encoded_file = base64.b64encode(data.read()).decode('utf-8')
        if not mime_type:
            guessed_types = guess_type(name)
            if guessed_types[0]:
                mime_type = guessed_types[0]
            else:
                mime_type = 'application/octet-stream'
        super().__init__(content=[
            {
                'type': 'text', 
                'text': prompt
            },
            {
                'type': type,
                'source_type': 'base64',
                'data': encoded_file,
                'mime_type': mime_type
            }
        ])
                


