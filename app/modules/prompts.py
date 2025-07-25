import os
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from uuid import uuid4

load_dotenv(find_dotenv())

class PromptManager:
    def __init__(self, llm_model="gpt-4o", temperature=0.7, streaming=False):
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("Missing OPENAI_API_KEY environment variable.")

        self.__base_model = ChatOpenAI(
            model=llm_model,
            temperature=temperature,
            streaming=streaming,
            max_retries=2,
        )
        self.__lore_schema = "app/db/schemas/lore_schema.json"

    def initiate_lore(self, world_id: str, world_name: str, n: int, lang="English"):
        schema = Path(self.__lore_schema).read_text(encoding="utf-8")
        formatted_schema = schema.replace("{", "{{").replace("}", "}}")
        template = (
            f"""
            You are a narrative generator for a procedural RPG game.
            Your task is to generate {{n}} lore entries for the world "{{world_name}}".
            
            Here are parameters to consider for the JSON:

            - The language will be: {{lang}}.
            - The world id will be: {{world_id}}.

            Each entry must follow this exact JSON structure:
            {formatted_schema}

            Respond with a array of JSON objects, with no quotes around. Nothing else.
            """
        )
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(
            n=n,
            world_name=world_name,
            lang=lang,
            world_id=world_id
        )
        generated_response = self.__base_model.invoke(formatted_prompt).content
        return generated_response
        
# world_uid = str(uuid4())  
# world_name = "Elysium"
# n_lores = 10

# prompt = PromptManager()
# generated_response = prompt.initiate_lore(
#     world_id=world_uid,
#     world_name=world_name,
#     n=n_lores
# )

# print(generated_response)