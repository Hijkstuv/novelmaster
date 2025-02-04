

import os
import json
from pathlib import Path

class Local_IO():
    def readTXT(
        self,
        file_path: str,
    ) -> str|None:
        """read txt file.
        """
        
        try:
            with open(file_path, 'r', encoding='UTF8') as f:
                lines = f.readlines()
            text = ""
            for line in lines:
                text += line
            return text
        except FileNotFoundError:
            print(f"No such file directory: {file_path}")
            
    
    def writeTXT(
        self,
        file_path: str,
        text: str
    ) -> None:
        """write txt file.
        """
        
        file_dir = Path(file_path).parent
        os.makedirs(file_dir, exist_ok=True)
        with open(file_path, 'w', encoding = 'UTF8') as f:
            f.write(text)
    
    
    def readJSON(
        self,
        file_path: str
    ) -> dict|None:
        """read json file.
        """
        
        try:
            with open(file_path, encoding= 'UTF-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"No such file directory: {file_path}")
            return None
    
    def writeJSON(
        self,
        file_path: str,
        data: str
    ) -> None:
        """write json file.
        """
        
        file_dir = Path(file_path).parent
        os.makedirs(file_dir, exist_ok=True)
        with open(file_path, 'w', encoding= 'UTF-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        f.close()
    
    
    def writeJSONL(
        self,
        file_path: str,
        data: list[str]
    ) -> None:
        """write jsonl file.
        """
        
        file_dir = Path(file_path).parent
        os.makedirs(file_dir, exist_ok=True)
        with open(file_path, 'w', encoding= 'UTF-8') as f:
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")