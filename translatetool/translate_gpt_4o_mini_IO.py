

from pydantic import BaseModel
from novelmaster.translatetool.gpt_4o_mini_IO import GPT_IO


"""response format for chat completion request."""
class WordSet(BaseModel):
    proper_noun: str
    translated_proper_noun: str
    
class TranslateResponse(BaseModel):
    translation: str
    proper_noun_dict: list[WordSet]


"""response format for batch request."""
TRANSLATE_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "TranslateResponse",
        "schema": TranslateResponse.model_json_schema()
    }
}


class Translate_GPT_IO(GPT_IO):
    def __init__(
        self,
        api_key: str
    ) -> None:
        """initialize with api_key.
        """
        
        GPT_IO.__init__(
            self,
            api_key = api_key
        )
    
    
    def custom_id(self) -> None:
        """
        return custom_id for translation.
        self.info["novel_id"], self.info["source_lang"],
        self.target_lang, self.episode required.
        """
        
        return (
            self.info["novel_id"]
            + "_"
            + self.episode
            + "_"
            + self.info["source_lang"]
            + "2"
            + self.target_lang
        )
    
    
    def translate_messages_format(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
    ) -> list[str]:
        """return the list of messages.
        """
        
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
    
    
    def translate_byChat(
        self,
        source_lang: str,
        target_lang: str,
        text: str
    ) -> TranslateResponse:
        """translate text by chat completion.
        """
        
        translate_messages = self.translate_messages_format(
            source_lang,
            target_lang,
            text
        )
        translate_completion = self.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=translate_messages,
            temperature=0.2,
            response_format=TranslateResponse
        )
        translate_response = translate_completion.choices[0].message.parsed
        return translate_response
    
    
    def translate_batch_request(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
    )-> str:
        """batch request to translate text, with proper noun processing.
        """
        
        translate_messages = self.translate_messages_format(
            source_lang,
            target_lang,
            text
        )
        
        
        return self.batch_request(
            messages = translate_messages,
            response_format = TRANSLATE_RESPONSE_FORMAT,
            custom_id = self.custom_id()
        )
          
    
    def translate_byBatch(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
    ) -> TranslateResponse|None:
        """
        translate text by batch.
        return TranslateResponse object when batch has completed,
        return None when batch has failed or cancelled.
        """
        
        self.translate_batch_request(
            source_lang,
            target_lang,
            text
        )
        print("batch requested")
        response = self.batchResponse()
        return response
    
    