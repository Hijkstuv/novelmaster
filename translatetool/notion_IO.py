

from notion_client import Client

BOOK = "📖"

'''
notion_client = notion_IO.Client(auth = notion_token)
'''

class Notion_IO(Client):
    def __init__(
        self,
        auth: str,
        main_page_id: str
    ) -> None:
        """class for Notion upload/download.
        """
        
        Client.__init__(
            self,
            auth = auth
        )
        self.main_page_id = main_page_id
    
    
    def childBlockForm(
        line: str
    ) -> dict:
        """form of child block.
        """
        
        child_block_form = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": line
                        }
                    }
                ]
            }
        }
        return child_block_form
    
    
    def writeLine(
        self,
        page_id: str,
        line: str
    ) -> None:
        """
        append a text line to page.
        able to include \n, but not that good... maybe?
        """
        
        self.blocks.children.append(
            block_id = page_id,
            children = [Notion_IO.childBlockForm(line)]
        )
    
    
    def writeText(
        self,
        page_id: str,
        text: str
    ) -> None:
        """write text to page.
        """
        
        lineList = text.split("\n")
        for line in lineList:
            self.writeLine(line)
    
    
    def readText(
        self,
        page_id: str
    ) -> str:
        """
        read text from page.
        ignore child pages, images, etc.
        """
        
        text = ""
        child_list = self.blocks.children.list(block_id = page_id)["results"]
        for child in child_list:
            if child["type"] == "paragraph":
                lines = child["paragraph"]["rich_text"]
                for line in lines:
                    text += line["plain_text"] + "\n"
        return text
    
    
    def childPageForm(
        parent_page_id: str,
        new_page_title: str,
        new_page_emoji = str|None
    ) -> dict:
        """form of child page.
        """
        
        child_page_form = {
            "parent": {"page_id": parent_page_id},
            "properties": {
                "title": [
                    {"text": {"content": new_page_title}}
                ]
            }
        }
        if new_page_emoji:
            child_page_form["icon"] = {
                "type": "emoji",
                "emoji": new_page_emoji
            }
        
        return child_page_form
    
    
    def getChildPageList(
        self,
        page_id: str
    ) -> list:
        """get list of child pages.
        """
        
        if not page_id:
            return
        child_list = self.blocks.children.list(block_id = page_id)["results"]
        return child_list
    
    def searchPage(
        self,
        parent_page_id: str,
        search_page_title: str
    ) -> str|None:
        """search page in the page, with page_id and page_title.
        """
        
        child_page_list = self.getChildPageList(parent_page_id)
        
        if not child_page_list:
            return None
        
        for page in child_page_list:
            if page[page["type"]]["title"] == search_page_title:
                return page["id"]
        return None
    
    def createChildPage(
        self,
        page_id: str,
        new_page_title: str,
        new_page_emoji: str|None
    ) -> str:
        """create child page.
        """
        
        new_page = Notion_IO.childPageForm(
            page_id,
            new_page_title,
            new_page_emoji
        )
        new_page_id = self.pages.create(**new_page)
        return new_page_id
    
    
    def createNewChildPage(
        self,
        page_id: str,
        new_page_title: str,
        new_page_emoji: str|None
    ) -> str:
        """
        return child page id.
        if does not exist, then create such child page and return its id.
        """
        
        child_id = self.pageSearch(
            page_id,
            new_page_title
        )
        if child_id:
            return child_id
        
        return self.createChildPage(
            page_id,
            new_page_title,
            new_page_emoji
        )
    
    