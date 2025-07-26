import os
import tiktoken
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MAX_TOTAL_TOKENS = 60_000
RESERVED_FOR_OUTPUT = 10_000
MAX_INPUT_TOKENS = MAX_TOTAL_TOKENS - RESERVED_FOR_OUTPUT

class PromptManager:
    def __init__(self, llm_model="gpt-4o", temperature=0.7, streaming=False):
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("Missing OPENAI_API_KEY environment variable.")

        self.__model_name = llm_model
        self.__base_model = ChatOpenAI(
            model=llm_model,
            temperature=temperature,
            streaming=streaming,
            max_retries=2,
        )
        self.__lore_schema = "app/db/schemas/lore_schema.json"

    def __count_tokens(self, text: str) -> int:
        enc = tiktoken.encoding_for_model(self.__model_name)
        return len(enc.encode(text))

    def __truncate_by_tokens(self, text: str, max_tokens: int) -> str:
        enc = tiktoken.encoding_for_model(self.__model_name)
        return enc.decode(enc.encode(text)[:max_tokens])

    def __sanitize_contexts(self, *contexts: str) -> list[str]:
        token_counts = [self.__count_tokens(ctx) for ctx in contexts]
        total_tokens = sum(token_counts)

        if total_tokens <= MAX_INPUT_TOKENS:
            return list(contexts)

        overflow = total_tokens - MAX_INPUT_TOKENS
        ctxs = list(contexts)

        for i in range(len(ctxs)):
            if overflow <= 0:
                break
            if token_counts[i] > 1000:
                reduction = min(token_counts[i] - 1000, overflow)
                new_token_count = token_counts[i] - reduction
                ctxs[i] = self.__truncate_by_tokens(ctxs[i], new_token_count)
                overflow -= reduction

        return ctxs

    def initiate_world(self, world_id: str, world_name: str, lang="English"):
        schema = Path(self.__lore_schema).read_text(encoding="utf-8")
        formatted_schema = schema.replace("{", "{{").replace("}", "}}")
        template = f"""
            You are a narrative generator for a procedural RPG game.
            Your task is to generate 1 entry for the world "{{world_name}}".
            
            Here are parameters to consider for the JSON:
            - The language will be: {{lang}}.
            - The world id will be: {{world_id}}.

            The entry must follow this exact JSON structure:
            {formatted_schema}

            Respond with a array of 1 JSON object, with no quotes around. Nothing else.
            """

        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(
            world_name=world_name,
            lang=lang,
            world_id=world_id,
        )
        llm_json = self.__base_model.invoke(formatted_prompt).content
        return llm_json

    def initiate_lore(
        self,
        world_id: str,
        world_name: str,
        n: int,
        world_context: str,
        lore_context: str,
        lang="English",
    ):
        world_context, lore_context = self.__sanitize_contexts(world_context, lore_context)

        schema = Path(self.__lore_schema).read_text(encoding="utf-8")
        formatted_schema = schema.replace("{", "{{").replace("}", "}}")
        template = f"""
            You are a narrative generator for a procedural RPG game.
            Your task is to generate {{n}} lore entries for the world "{{world_name}}".

            Here is the world context :

            --- START OF LORE CONTEXT ---

            {{world_context}}

            --- END OF LORE CONTEXT ---

            Here are pre-existing lore contexts that have been already generated. Take them into consideration to remain coherent. \
            If none has been provided start fresh :

            --- START OF LORE CONTEXT ---

            {{lore_context}}

            --- END OF LORE CONTEXT ---
            
            Here are parameters to consider for the JSON:
            - The language will be: {{lang}}.
            - The world id will be: {{world_id}}.

            Each entry must follow this exact JSON structure:
            {formatted_schema}

            Respond with a array of JSON objects, with no quotes around. Nothing else.
            """
        
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(
            n=n,
            world_name=world_name,
            lang=lang,
            world_id=world_id,
            lore_context=lore_context,
            world_context=world_context,
        )
        llm_json = self.__base_model.invoke(formatted_prompt).content
        return llm_json
    
    def initiate_events(
        self,
        world_id: str,
        world_name: str,
        n: int,
        world_context: str,
        lore_context: str,
        event_context: str,
        lang="English",
    ):
        world_context, lore_context, event_context = self.__sanitize_contexts(
            world_context, lore_context, event_context
        )

        schema = Path(self.__lore_schema).read_text(encoding="utf-8")
        formatted_schema = schema.replace("{", "{{").replace("}", "}}")
        template = f"""
            You are a narrative generator for a procedural RPG game.
            Your task is to generate {{n}} world event entries for the world "{{world_name}}".
            The entries must be coherent with the lore and the world settings.

            Here is the world context :

            --- START OF LORE CONTEXT ---

            {{world_context}}

            --- END OF LORE CONTEXT ---

            Here are pre-existing lore contexts that have been already generated. Take them into consideration to remain coherent. \
            If none has been provided start fresh :

            --- START OF LORE CONTEXT ---

            {{lore_context}}

            --- END OF LORE CONTEXT ---

            Here are pre-existing event contexts that have been already generated. Take them into consideration to remain coherent. \
            If none has been provided start fresh :

            --- START OF EVENT CONTEXT ---

            {{event_context}}

            --- END OF EVENT CONTEXT ---
            
            Here are parameters to consider for the JSON:
            - The language will be: {{lang}}.
            - The world id will be: {{world_id}}.

            Each entry must follow this exact JSON structure:
            {formatted_schema}

            Respond with a array of JSON objects, with no quotes around. Nothing else.
            """
        
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(
            n=n,
            world_name=world_name,
            lang=lang,
            world_id=world_id,
            lore_context=lore_context,
            world_context=world_context,
            event_context=event_context
        )
        llm_json = self.__base_model.invoke(formatted_prompt).content
        return llm_json