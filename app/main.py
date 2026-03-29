import argparse
import os
import sys
import json
from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

read_tool = {
  "type": "function",
  "function": {
    "name": "Read",
    "description": "Read and return the contents of a file",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path to the file to read"
        }
      },
      "required": ["file_path"]
    }
  }
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [
    { "role": "user", "content": args.p }
    ]
    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=messages,
        tools = [read_tool]
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage
    #print(chat.choices[0].message.content)
    response = chat.choices[0].message.content
    finish_reason = chat.choices[0].finish_reason
    while finish_reason != "stop":
        
            
            #messages.append({"role": "assistant", "content": response, "tool_calls": chat.choices[0].message.tool_calls})

            
            messages.append({"role": "assistant", "content": response})
            if chat.choices[0].message.tool_calls != None:
                
                for tool_call in chat.choices[0].message.tool_calls:
                    
                    tool_call = tool_call.model_dump()
                    response_tool = tool_call["function"]["name"]

                    response_tool_id = tool_call["id"]
                    response_args = json.loads(tool_call["function"]["arguments"])["file_path"]
                    with open(response_args, "r") as f:
                        file_contents = f.read()
                    #print(file_contents)
                        messages.append({"role": "tool","tool_call_id": response_tool_id, "content": file_contents})
                    

            chat = client.chat.completions.create(
                model="anthropic/claude-haiku-4.5",
                messages= messages,
                tools = [read_tool]
            )
            response = chat.choices[0].message.content
            finish_reason = chat.choices[0].finish_reason

    
    print(chat.choices[0].message.content)
    # else:
    #     response_tool = chat.choices[0].message.tool_calls[0].function.name
    #     response_args = json.loads(chat.choices[0].message.tool_calls[0].function.arguments)["file_path"]

    #     with open(response_args, "r") as f:
    #         file_contents = f.read()
    #         print(file_contents)

    

if __name__ == "__main__":
    main()
