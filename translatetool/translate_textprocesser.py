

import re


class Translate_TextProcesser():
    """class for pre/postprocessing text.
    """
    def getText(self) -> str:
        return self.episode_text
    
    def setText(self, text: str) -> None:
        self.episode_text = text
    
    
    def addEndmark(self) -> None:
        """add japanese end mark, if there's no mark at the end of speech lines.
        """
        self.episode_text = re.sub(
            r'([^。？！])?(」+)', r'\1。\2',
            self.episode_text
        )
    
    def replaceChar(self) -> None:
        """replace japanese characters.
        """
        self.episode_text = re.sub(r'[「」]', '\"', self.episode_text)
        self.episode_text = self.episode_text.replace('『', '[')
        self.episode_text = self.episode_text.replace('』', ']')
        self.episode_text = self.episode_text.replace('　', ' ')
    
    def preprocess_japanese(self) -> None:
        """preprocess of japanese characters.
        """
        self.addEndmark()
        self.replaceChar()
    
    
    def textReplace(
            self,
            source_word: str,
            target_word: str
        ) -> None:
        """replace source_word in self.text with target_word
        """
        self.episode_text = self.episode_text.replace(source_word, target_word)
    
    def preprocess_proper_noun(
            self
        ) -> None:
        """preprocess of proper noun, before translation.
        """
        glossary = self.info["glossary"]
        
        for i in range(len(glossary)):
            self.textReplace(
                glossary[i]["source_word"],
                glossary[i]["placeholder"]
            )
    
    
    def postprocess_proper_noun(
            self
        ) -> None:
        """postprocess of proper noun, after translation.
        """
        glossary = self.info["glossary"]

        for i in range(len(glossary)):
            self.textReplace(
                glossary[i]["placeholder"],
                glossary[i]["target_word"]
            )
    
    
    def text_tool(
            self,
            tool: str
        ) -> None:
        """completion of text tools.
        """
        if tool == "pre_ja":
            self.preprocess_japanese()
        elif tool == "pre_pn":
            self.preprocess_proper_noun()
        elif tool == "post_pn":
            self.postprocess_proper_noun()
        else:
            print("Nonvalid tool error")
    
    
