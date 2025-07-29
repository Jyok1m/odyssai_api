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
        self.__world_schema = "app/db/schemas/world_schema.json"
        self.__lore_schema = "app/db/schemas/lore_schema.json"
        self.__event_schema = "app/db/schemas/event_schema.json"
        self.__character_schema = "app/db/schemas/character_schema.json"

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

    def __get_schema_by_step_type(self, step_type: str):
        if step_type == "world":
            return self.__world_schema
        elif step_type == "lore":
            return self.__lore_schema
        elif step_type == "event":
            return self.__event_schema
        elif step_type == "character":
            return self.__character_schema
        return ""

    def __get_build_prompt_template(
        self,
        formatted_schema: str,
        step_type: str,
        world_context="",
        lore_context="",
        event_context="",
        character_context="",
    ):
        return f"""
        You are a narrative generator for a procedural RPG game.
        Your task is to generate {{n}} {step_type} entries for the world "{{world_name}}".
        Each event must be narratively consistent with the established contexts. 
        Avoid redundancy, and ensure each entry contributes to meaningful story development.

        Below are excerpts of previously generated content. Use them to remain coherent. 
        If any section is empty, disregard its context need:

        --- START OF WORLD CONTEXT ---
        {world_context}
        --- END OF WORLD CONTEXT ---

        --- START OF LORE CONTEXT ---
        {lore_context}
        --- END OF LORE CONTEXT ---

        --- START OF EVENT CONTEXT ---
        {event_context}
        --- END OF EVENT CONTEXT ---

        --- START OF CHARACTER CONTEXT ---
        {character_context}
        --- END OF CHARACTER CONTEXT ---

        Here are parameters to consider for the JSON:
        - The language will be: {{lang}}.
        - The world id will be: {{world_id}}.

        Each entry must strictly follow this JSON structure:
        {formatted_schema}

        Return only a valid JSON array of {{n}} objects with no quotes around. Do not include any explanations, comments, or markdown formatting.
        """

    def initiate_build(
        self,
        world_id: str,
        world_name: str,
        step_type: str,
        n: int,
        world_context="",
        lore_context="",
        event_context="",
        character_context="",
        lang="English",
    ):
        world_context, lore_context, event_context, character_context = (
            self.__sanitize_contexts(
                world_context, lore_context, event_context, character_context
            )
        )

        schema_type = self.__get_schema_by_step_type(step_type)
        schema = Path(schema_type).read_text(encoding="utf-8")
        formatted_schema = schema.replace("{", "{{").replace("}", "}}")

        prompt_template = self.__get_build_prompt_template(
            formatted_schema=formatted_schema,
            step_type=step_type,
            world_context=world_context,
            lore_context=lore_context,
            event_context=event_context,
            character_context=character_context,
        )
        prompt = PromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format(
            n=n,
            world_name=world_name,
            lang=lang,
            world_id=world_id,
        )
        llm_json = self.__base_model.invoke(formatted_prompt).content
        return llm_json
