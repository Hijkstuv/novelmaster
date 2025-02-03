

from openai import OpenAI
import tiktoken
from novelmaster.translatetool.local_IO import Local_IO
import time
import os
import json


def count_token(
    content: str|list|dict
) -> int:
    """count token for GPT-4o-mini.
    """
    
    tokenizer = tiktoken.get_encoding("cl100k_base")
    count = 0

    if type(content) is str:
        tokens = tokenizer.encode(content)
        count += len(tokens)
    elif type(content) is list:
        for message in content:
            tokens = count_token(message)
            count += tokens
    elif type(content) is dict:
        tokens = count_token(content["content"])
        count += tokens
    
    return count


def is_over_limit(
    content: str|list|dict,
    limit: int|None = 12000
) -> bool:
    """check whether input token count over the limit or not.
    """
    if not limit:
        limit = 12000
    if count_token(content) >= limit:
        return True
    return False


class GPT_IO(OpenAI, Local_IO):
    def __init__(
        self,
        api_key: str
    ) -> None:
        """initialize with api_key.
        """
        
        OpenAI.__init__(
            self,
            api_key = api_key
        )
    
    def translate_message_format(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
    ) -> str:
        """return custom id and message string, or None if text is too long.
        """
        
        if is_over_limit(text):
            return None
        
        system_message = {
            "role": "developer",
            "content": (
                f"You are a professional translator. Translate text from {source_lang} to {target_lang}."
                "identify all proper nouns in the source text and return them in a list of word set."
                "Placeholders like `</xxx>` are not proper noun and must remain unchange."
            )
        }
        translate_message = {
            "role": "user",
            "content": text
        }
        translate_messages = [system_message, translate_message]
        return translate_messages
    
    
    def chatCompletion(
        self,
        messages: list[str],
        limit: int|None = None,
        response_format: dict|None = None
    ) -> str|dict|None:
        """request immedietely, to chat completion.
        """
        
        if is_over_limit(messages, limit):
            return None
        
        if response_format:
            chat_completion = self.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
                response_format=response_format
            )
            chat_response = chat_completion.choices[0].message.parsed
        else:
            chat_completion = self.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2
            )
            chat_response = chat_completion.choices[0].message
        
        return chat_response
    
    
    def batch_request(
        self,
        messages: list[str],
        custom_id: str,
        limit: int|None = None,
        response_format: dict|None = None
    ) -> str:
        """request with batch, to chat completion.
        """
        
        if is_over_limit(messages, limit):
            return None
        
        batch_data = [{
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": messages
            }
        }]
        if response_format:
            batch_data[0]["body"]["response_format"] = response_format
        
        os.makedirs("batch", exist_ok = True)
        batch_file = os.path.join(
            "batch",
            f"{custom_id}" + ".jsonl"
        )
        self.writeJSONL(batch_file, batch_data)
        
        batch_input_file = self.files.create(
            file = open(batch_file, "rb"),
            purpose = "batch"
        )
        batch = self.batches.create(
            input_file_id = batch_input_file.id,
            endpoint = "/v1/chat/completions",
            completion_window = "24h"
        )
        self.batch_id = batch.id
        return self.batch_id
    
    
    def batch_status(
        self,
        batch_id: str|None = None
    ) -> str:
        """status of the batch request.
        """
        
        if not batch_id:
            batch_id = self.batch_id
        status = self.batches.retrieve(batch_id).status
        return status
    
    
    def batch_retrieve(
        self,
        batch_id: str|None = None
    ) -> str|dict|None:
        """retrieve batch response, with batch_id.
        """
        
        if not batch_id:
            batch_id = self.batch_id
        output_file = self.files.retrieve(batch_id).output_file_id
        response_dict = json.load(output_file.text)
        response = response_dict["response"]["body"]["choices"][0]["content"]
        return response
    
    
    def batch_error(
        self,
        batch_id: str|None = None
    ) -> None:
        """retrive error file, with batch_id
        """
        
        if not batch_id:
            batch_id = self.batch_id
        error_file = self.files.retrieve(batch_id).error_file_id
        print(json.load(error_file.text))
    
    
    def batchResponse(
        self,
        batch_id: str|None = None
    ) -> str|dict|None:
        """
        wait for the batch process ends.
        return output response when batch has completed,
        or None when failed or cancelled.
        """
        if not batch_id:
            batch_id = self.batch_id
        BATCH_END = [
            "completed",
            "failed",
            "cancelled",
            "expired"
        ]
        while True:
            time.sleep(20)
            if self.batch_status(batch_id) in BATCH_END:
                break
        
        if self.batch_status(batch_id) == "completed":
            print("batch completed")
            return self.batch_retrieve(batch_id)
        else:
            if self.batch_status(batch_id) == "failed":
                self.batch_error(batch_id)
            print(f"batch {self.batch_status()}")
    
    