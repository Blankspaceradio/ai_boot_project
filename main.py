import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
from prompty import system_prompt
from call_function import *
import sys


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing (check your .env file)")
client = genai.Client(api_key=api_key)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    for i in range(20):
        if args.verbose:
            print(f"--- iteration {i} ---")
        response = client.models.generate_content(
        model='gemini-2.5-flash', contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt,temperature=0),
        )
        for cand in (response.candidates or []):
            if cand.content:
                messages.append(cand.content)
        if not response.usage_metadata:
            raise RuntimeError("Metadata is missing!")


        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        

    
        if response.function_calls:
            function_results = []
            for fun_call in response.function_calls:  
                function_call_result = call_function(fun_call, args.verbose)
                if not function_call_result.parts:
                    raise Exception("No parts in function call result")
                if function_call_result.parts[0].function_response is None:
                    raise Exception("Function response is None")
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception("Function response is None")
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            messages.append(types.Content(role="user", parts=function_results))    
        else:
             print("Final response:")
             print(response.text)
             return
    print("max iterations reached")
    sys.exit(1)

if __name__ == "__main__":
    main()
