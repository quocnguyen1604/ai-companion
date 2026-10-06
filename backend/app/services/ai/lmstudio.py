from app.services.ai.base import AIProvider, MessageRole, ProviderMessage, ProviderSummary
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.prompts.default import system_prompt, summarize_prompt, system_prompt_compacted
from app.tools.memory import retrieve_memory

load_dotenv()
client = AsyncOpenAI(base_url=os.getenv("LMSTUDIO_API_URL"), api_key="lm-studio")

class LMStudioAIProvider:
    """LM Studio provider that uses the LM Studio API to generate responses."""

    async def generate_response(self, messages: list[ProviderMessage], previous_response_id: str | None):
        latest_user_message = next((message.content for message in reversed(messages) if message.role == MessageRole.USER), "")
        request = {
            "model": "google/gemma-4-26b-a4b-qat",
            "instructions": system_prompt,
            "input": latest_user_message,
            "temperature": 0.5,
            "reasoning": {"effort": "none"}
        }
        if previous_response_id is not None:
            request["previous_response_id"] = previous_response_id
        response = client.responses.create(
            **request
        )

        print("\n=== LM STUDIO RESPONSE ===")
        print(f"ID: {response.id}")
        print(f"Model: {response.model}")
        print(f"Status: {response.status}")

        print("\n--- Usage ---")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
        print(f"Reasoning tokens: {response.usage.output_tokens_details.reasoning_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

        print("\n--- Response ---")
        print(response.output_text)

        print("==========================\n")

        response_id = response.id
        response_text = None
        for item in response.output:
            if item.type == "message" and item.role == "assistant":
                for content in item.content:
                    if content.type == "output_text":
                        response_text = content.text
                        break
        return {
            "id": response_id,
            "content": response_text if response_text else "",
        }

    async def stream_response(self, messages: list[ProviderMessage], previous_response_id: str | None, previous_summary: ProviderSummary | None = None):
            temp_response_id = previous_response_id
            latest_user_message = next((message.content for message in reversed(messages) if message.role == MessageRole.USER), "")
            inputs = [{
                "role": "user",
                "content": latest_user_message
            }]
            tools = [retrieve_memory]
            while True:
                tool_calls = {}
                if (previous_summary is not None and previous_summary.content):
                    request = {
                        "model": "google/gemma-4-26b-a4b-qat",
                        "instructions": system_prompt_compacted + f"\n\nPrevious Summary: {previous_summary.content}",
                        "input": inputs,
                        "temperature": 0.5,
                        "reasoning": {"effort": "none"},
                        "tools": tools,
                        "stream": True
                    }
                    print("\n=== LM STUDIO STREAMING RESPONSE WITH COMPACTED CONTEXT ===")
                    print(request)
                else:
                    request = {
                        "model": "google/gemma-4-26b-a4b-qat",
                        "instructions": system_prompt,
                        "input": inputs,
                        "temperature": 0.5,
                        "reasoning": {"effort": "none"},
                        "tools": tools,
                        "stream": True
                    }
                if temp_response_id is not None:
                    request["previous_response_id"] = temp_response_id
                response_stream = await client.responses.create(
                    **request
                )

                inputs = []
        
                final_response = None
                final_chunk = None

                async for chunk in response_stream:
                    print("\n--- Chunk ---")
                    print(chunk)
                    if chunk.type == "response.output_item.added" and chunk.item.type == "function_call":
                        tool_calls[chunk.output_index] = chunk.item
                    elif chunk.type == "response.function_call_arguments.delta":
                        index = chunk.output_index

                        if tool_calls[index]:
                            tool_calls[index].arguments += chunk.delta
                    elif chunk.type == "response.output_text.delta" and chunk.delta is not None:
                        yield chunk
                    elif chunk.type == "response.completed":
                        final_chunk = chunk
                        final_response = chunk.response
                        break

                if tool_calls:
                    for index, tool_call in tool_calls.items():
                            print(f"\n--- Tool Call ---\n{tool_call}\n")
                            print(f"\n--- Tool Calls ---\n{tool_calls}\n")
                            function_name = tool_call.name
                            arguments = json.loads(tool_call.arguments)
                            print(f"\n--- Tool Call ---\nFunction: {function_name}\nArguments: {arguments}\n")
                            if function_name == "retrieve_memory":
                                search_query = arguments.get("search_query", "")
                                k = arguments.get("k", 3)
                                from app.services.memory import MemoryService
                                memory_service = MemoryService()
                                relevant_memories = memory_service.retrieve_memory(search_query, k, 0)
                                print(f"\n--- Retrieved Memories ---\n{relevant_memories}\n")
                                inputs.append({
                                    "type": "function_call_output",
                                    "call_id": tool_call.call_id,
                                    "output": json.dumps(relevant_memories),
                                })
                    temp_response_id = final_response.id
                    continue

                break

            print("\n=== LM STUDIO RESPONSE ===")
            print(f"ID: {final_response.id}")
            print(f"Model: {final_response.model}")
            print(f"Status: {final_response.status}")
                
            print("\n--- Usage ---")
            print(f"Input tokens: {final_response.usage.input_tokens}")
            print(f"Output tokens: {final_response.usage.output_tokens}")
            print(f"Reasoning tokens: {final_response.usage.output_tokens_details.reasoning_tokens}")
            print(f"Total tokens: {final_response.usage.total_tokens}")
                
            print("\n--- Response ---")
            print(final_response.output_text)
                
            print("==========================\n")

            yield final_chunk

    async def generate_summary(self, messages: list[ProviderMessage], previous_summary: ProviderSummary | None) -> ProviderSummary:
        if previous_summary is not None: 
            delattr(previous_summary, 'prompt_token_count')
            delattr(previous_summary, 'token_count')
        messages = [{"role": message.role.value, "content": message.content} for message in messages]
        input_object = json.dumps( {
            "previous_summary": previous_summary if previous_summary else None,
            "messages": messages
        })

        request = {
                        "model": "google/gemma-4-26b-a4b-qat",
                        "instructions": summarize_prompt,
                        "input": input_object,
                        "temperature": 0.5,
                        "reasoning": {"effort": "high"},
                        "stream": False
                    }

        response = await client.responses.create(
            **request
        )

        print("\n=== LM STUDIO SUMMARY RESPONSE ===")
        print(f"ID: {response.id}")
        print(f"Model: {response.model}")
        print(f"Status: {response.status}")

        print("\n--- Usage ---")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
        print(f"Reasoning tokens: {response.usage.output_tokens_details.reasoning_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

        print("\n--- Summary Response ---")
        print(response.output_text)
        print("==========================\n")

        return ProviderSummary(
            content=response.output_text,
            prompt_token_count=response.usage.input_tokens,
            token_count=response.usage.output_tokens
        )