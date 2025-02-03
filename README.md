# novelmaster
The python package for crawl & translate web novels, from [syosetukani narou(小説家になろう)].

You need these packages : [Dotenv, Selenium, openai, notion-client] <- use ```pip install (package_name)```.

You have to put [
  1. **your own openai api key**,
  2. your own notion page (optional),
  3. your own notion api auth token (optional)
] in .env file.

```.env
translate_gpt_api_key='(your openai api key)'
translate_notion_auth='(your notion auth)'
translate_notion_main_page_id='(your notion page id)'
```
