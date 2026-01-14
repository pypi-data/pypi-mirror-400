import requests
import time
import os
import inspect
from typing import get_origin, get_args, Literal

from langchain_core.messages import AIMessage
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
import uuid
from datetime import datetime
import re

def google_inference_request (system_prompt: str, user_prompt: str, base_url: str, format: dict = {},  model_name: str = "gemini-2.5-pro"):
    """Función para hacer una petición de inferencia al servicio de rotación de api keys interno de Unergy/Solenium. 
    Base URL corresponde con el puerto 8006 de la URL donde se esté conectand oal servidor. 'model_name' es, por defecto, gemini-2.5-pro. 
    Si no usará este modelo, asegúrese de usar otro de Google. 
    El formato corresponde con el diccionario que devuelve la función .model_json_schema() del objeto que quiere usar como formato, 
    que debe heredar de BaseModel de Pydantic y debe tener atributos serializables.
    """


    payload = {
        "model_name":  model_name,
        "system_message": system_prompt,
        "user_message": user_prompt,
        "flag": True,
        "provider": "google_genai",
        "format": format
    }


    print("Enviando tarea al servidor...")
    response = requests.post(f"{base_url}/inference", json=payload)

    if response.status_code != 200:
        print("Error:", response.text)
        exit()

    data = response.json()  
    task_id = data["task_id"]
    print(f"Tarea creada con ID: {task_id}")

    while True:
        time.sleep(3)
        result_response = requests.get(f"{base_url}/result/{task_id}")
        result_data = result_response.json()

        print(f"Estado actual: {result_data['status']}")

        if result_data["status"] == "SUCCESS":
            print("✅ Resultado listo:")
            print(result_data["data"])
            return result_data["data"]
            
        elif result_data["status"] == "FAILURE":
            print("❌ Error en la tarea:")
            return None
            


def function_to_schema(fn):
    sig = inspect.signature(fn)
    hints = fn.__annotations__

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        annotation = hints.get(name, str)

        prop = {}

        if get_origin(annotation) is Literal:
            prop["type"] = "string"
            prop["enum"] = list(get_args(annotation))
        elif annotation is str:
            prop["type"] = "string"
        elif annotation is int:
            prop["type"] = "integer"
        elif annotation is float:
            prop["type"] = "number"
        elif annotation is bool:
            prop["type"] = "boolean"
        else:
            prop["type"] = "string"

        # Default value
        if param.default is not inspect.Parameter.empty:
            prop["default"] = param.default
        else:
            required.append(name)

        properties[name] = prop

    return {
        "name": fn.__name__,
        "description": (fn.__doc__ or "").strip(),
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def langchain_formatter (output: dict, model_name: str):

    if len(output) == 2:
        #Esto es porque hay tanto una tool_call como respuesta

        tool_dict = output[1]

        tool_name = tool_dict['tool_call']['name']

        try: 
            assistant_text = output[0]['assistant']
        except Exception:
            print("Hubo la siguiente excepción: ", Exception)
            assistant_text  = ""
    
        ai_message = AIMessage(
            content=assistant_text,
            additional_kwargs={},  # can stay empty
            response_metadata={
                "model": model_name,
                "created_at": datetime.now(),
                "done": True,
                "done_reason": "stop",
                "model_provider": "custom",
            },
            id=f"lc_run--{uuid.uuid4().__str__()}",
            usage_metadata={
                "input_tokens": 0,
                "output_tokens": len(assistant_text.split()),
                "total_tokens": len(assistant_text.split()),
            },
            tool_calls= [{'name': tool_name, 'args': tool_dict['tool_call']['arguments'], 'id': uuid.uuid4().__str__(), 'type': 'tool_call'}]

        )
    elif len(output) == 1:
         
         assistant_text = output[0]['assistant']

         #aquí, ver como procesamos en caso de ser structured output!!

         ai_message = AIMessage(
            content=assistant_text,
            additional_kwargs={},  # can stay empty
            response_metadata={
                "model": model_name,
                "created_at": datetime.now(),
                "done": True,
                "done_reason": "stop",
                "model_provider": "custom",
            },
            id=f"lc_run--{uuid.uuid4().__str__()}",
            usage_metadata={
                "input_tokens": 0,
                "output_tokens": len(assistant_text.split()),
                "total_tokens": len(assistant_text.split()),
            })


    return ai_message

def langchain_deformatter (messages: any):

    deformatted_messages = []
    
    for message  in messages:
        if isinstance(message, SystemMessage):
            deformatted_messages.append({'system': message.content})
        elif isinstance(message, HumanMessage):
            deformatted_messages.append({'user': message.content})
        elif isinstance(message,AIMessage):

            if message.content != '':
                    deformatted_messages.append({'assistant': message.content})

            if message.tool_calls:
                tool_info = message.tool_calls

                tool_name = tool_info[0]['name']
                tool_args = tool_info[0]['args']

                deformatted_messages.append({'tool_call': {'name': tool_name, 'arguments': tool_args}})
                
        elif isinstance(message, ToolMessage):
            
            deformatted_messages.append({'tool_result': message.content})
    
    print("Mensajes deformateados: ", deformatted_messages)
    
    return deformatted_messages


import httpx
from typing import Dict, Any

class EngineClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def retrieve_model(self, model_name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/retrieve-model",
                params={"model_name": model_name},
            )
            r.raise_for_status()
            return r.json()

    async def start_engine(
        self,
        model_name: str,
        gpu_usage: float,
        kv_caching: bool,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/start_engine",
                params={
                    "model_name": model_name,
                    "gpu_usage": gpu_usage,
                    "kv_caching": kv_caching,
                },
            )
            r.raise_for_status()
            return r.json()

    async def unload_engine(self, model_name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/unload",
                params={"model_name": model_name},
            )
            r.raise_for_status()
            return r.json()

    async def reset_engine(self, model_name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/reset-engine",
                params={"model_name": model_name},
            )
            r.raise_for_status()
            return r.json()

    async def list_engines(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/engines")
            r.raise_for_status()
            return r.json()
    

    def general_inference_request (self, messages_from_state: dict = None, model_name: str = 'openai/gpt-oss-20b', system_message: str = "", user_message: str = "", structured_output: dir = None, tools: list = None, prefill_caching: bool = False, langgraph: bool = False, details: str = "", gpu_usage: int  = 0.55):

        base_url = self.base_url

        url = f'{base_url}/general_inference_request'


        if langgraph and messages_from_state:
            formatted_messages = langchain_deformatter(messages_from_state)
        else:
            if messages_from_state:
                formatted_messages = messages_from_state
            else:
                formatted_messages = [
                {"system": system_message},
                {"user": user_message}
            ]

        if structured_output and tools:
            print("Warning: El uso de tanto structured_output como de tool_calling es problemático. Evite este tipo de llamadas.")

        payload = { 
        "messages": formatted_messages,
        "model_name": model_name,
        "structured_output": structured_output,
        "functions": tools,
        "prefill_caching": prefill_caching,
        "gpu_usage": gpu_usage,
        "details": details
        }
        
        headers = {
        "Content-Type": "application/json"
    }
        
        response = requests.post(
        url,
        headers=headers,
        json=payload   # requests handles json.dumps internally
    ).json()
        

        try:
            if langgraph:
                print("Respuesta antes de formatter: ", response)
                response = langchain_formatter(response['output'], model_name= model_name)
                print("Langchain formatter: ", response)
                return response
                
            else:
                return response['output']
        except Exception as e:
            print("Error durante la inferencia: ", e)
            return {"Error": "Error durante la inferencia, vea los logs del servidor - puede ser error de parsing"}


    def deepseek_ocr_inference_request (self, path:str):

        base_url = self.base_url

        url = f'{base_url}/deepseek_inference_request'

        params = {
        "mode": "Tiny" 
    }
        # Archivo a enviar
        files = {
            "file": open(path, "rb") 
        }

        response = requests.post(url, params=params, files=files)

        files["file"].close()

        return response.json()




        

