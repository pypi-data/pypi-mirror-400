from fastapi import FastAPI
import uvicorn
import httpx
import asyncio
from typing import Optional, List, Dict
import socket

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .sdk import register 
from .models import AgentRequest, AgentResponse

import yaml
from pathlib import Path

DEFAULT_PLANNER_SYSTEM = """
You are a planner.
Decompose the user query into subtasks.
Return a JSON list of strings.
"""

DEFAULT_REFLECTOR_SYSTEM = """
You are a refresher.
Synthesize the answer based on the tool outputs.
"""

DEFAULT_PERSONA_SYSTEM = """
You are {name}.
Description: {description}.

User Query: {query}

Answer the user's question.
"""

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class BaseAgent:
    def __init__(
        self, 
        name: str, 
        description: str,
        port: int,
        model: BaseChatModel,
        registry_url: str = "http://localhost:8000",
        persona_prompt: str = DEFAULT_PERSONA_SYSTEM,
        use_local_server: bool = False
    ):
        self.name = name
        self.description = description
        self.port = port
        self.model = model
        self.registry_url = registry_url.rstrip("/")
        self.persona_system = persona_prompt
        self.use_local_server = use_local_server

        self.app = FastAPI(title=name, description=description)
        self._setup_routes()

    def _setup_routes(self):
        """Override this in subclasses"""
        raise NotImplementedError

    def _register_endpoint(self, endpoint):
        endpoint.__name__ = self.name
        endpoint.__doc__ = self.description
        
        if self.use_local_server:
             host = "localhost"
        else:
             host = get_ip()
             
        my_url = f"http://{host}:{self.port}/run"
        try:
            target_url = f"{self.registry_url}/register"
            print(f"[{self.name}] Registering {my_url} -> {target_url}")
            register(url=my_url, registry_url=target_url)(endpoint)
        except Exception as e:
            print(f"[{self.name}] Registration failed: {e}")

    async def internal_thought(self, query: str) -> str:
        """Direct answer using Persona Prompts."""
        prompt = ChatPromptTemplate.from_template(self.persona_system)
        chain = prompt | self.model | StrOutputParser()
        return chain.invoke({"name": self.name, "description": self.description, "query": query})

    def start(self):
        print(f"[{self.name}] | Started on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


class AgentLeaf(BaseAgent):
    """
    A simple worker agent. 
    It receives a query and answers it directly using its persona/tools.
    It DOES NOT decompose or delegate.
    """
    def __init__(
        self,
        name: str,
        description: str,
        port: int,
        model: BaseChatModel,
        registry_url: str = "http://localhost:8000",
        persona_prompt: str = DEFAULT_PERSONA_SYSTEM,
        use_local_server: bool = False
    ):
        super().__init__(name, description, port, model, registry_url, persona_prompt, use_local_server)
        self.persona_prompt = persona_prompt

    def _setup_routes(self):
        @self.app.post("/run", response_model=AgentResponse)
        async def run_endpoint(payload: AgentRequest):
            print(f"\n[{self.name}] | Leaf Input: '{payload.query}'")

            final_prompt = "system prompt\n" + self.persona_prompt + "\n" + "user prompt" + "\n"
            
            response = await self.internal_thought(final_prompt + payload.query)
            
            return AgentResponse(
                response=response,
                reflection="Direct Answer (Leaf)",
                sources=[]
            )

        self._register_endpoint(run_endpoint)


class AgentCore(BaseAgent):
    """
    An orchestrator agent.
    It can decompose tasks, search the registry, and delegate to other agents.
    """
    def __init__(
        self,
        name: str,
        description: str,
        port: int,
        model: BaseChatModel,
        registry_url: str = "http://localhost:8000",
        planner_prompt: str = DEFAULT_PLANNER_SYSTEM,
        reflector_prompt: str = DEFAULT_REFLECTOR_SYSTEM,
        persona_prompt: str = DEFAULT_PERSONA_SYSTEM,
        use_local_server: bool = False
    ):
        super().__init__(name, description, port, model, registry_url, persona_prompt, use_local_server)
        self.planner_system = planner_prompt
        self.reflector_system = reflector_prompt

    def _setup_routes(self):
        @self.app.post("/run", response_model=AgentResponse)
        async def run_endpoint(payload: AgentRequest):
            print(f"\n[{self.name}] | Core Input: '{payload.query}'")
            
            # 1. Decompose
            sub_tasks = await self.decompose(payload.query)
            
            # No subtasks? Just answer.
            if not sub_tasks:
                res = await self.internal_thought(payload.query)
                return AgentResponse(response=res, reflection="Direct Answer (Core)", sources=[])
            
            print(f"[{self.name}] | Subtasks: {sub_tasks}")
            
            # 2. Execute
            tool_outputs = await asyncio.gather(
                *[self._execute_subtask(task) for task in sub_tasks]
            )

            # 3. Reflect
            final_answer = await self.reflect(payload.query, tool_outputs)
            
            unique_sources = list({t['agent'] for t in tool_outputs if t['success']})

            return AgentResponse(
                response=final_answer, 
                reflection="Synthesized via Reflection", 
                sources=unique_sources
            )

        self._register_endpoint(run_endpoint)

    async def decompose(self, query: str) -> List[str]:
        """Generates a plan using the Planner Prompts."""
        import re
        import json

        final_prompt = ChatPromptTemplate.from_template(self.planner_system)
        chain = final_prompt | self.model | StrOutputParser()

        try:
            raw_text = chain.invoke({"query": query})
            
            # 1. Try to find a JSON list in the output
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            
            # 2. Fallback
            parsed = json.loads(raw_text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]

            return []
            
        except Exception as e:
            print(f"[{self.name}] Plan Failed: {e}. Raw Output: {raw_text!r}")
            return []

    async def reflect(self, query: str, tool_results: List[Dict]):
        """Synthesizes answers using Reflector Prompts."""
        # Debug: Print what the reflector sees
        print(f"[{self.name}] | Tool Results for Reflection: {tool_results}")
        
        context_str = "\n".join([
            f"- {res['agent']}: {res.get('output', res.get('error'))}" 
            for res in tool_results
        ])

        final_prompt = ChatPromptTemplate.from_template(self.reflector_system)
        chain = final_prompt | self.model | StrOutputParser()

        try:
            return chain.invoke({
                "name": self.name, 
                "context": context_str, 
                "query": query
            })
        except Exception as e:
            print(f"[{self.name}] Reflect Failed: {e}")
            return ""

    async def _execute_subtask(self, intent: str) -> Dict:
        """Executes a subtask using the appropriate tool."""
        
        search_query = str(intent)
        
        target = await self._search_registry(search_query)
        if not target: 
            return {"success": False, "agent": "Registry", "error": f"Not found: {search_query}"}
        
        try:
            async with httpx.AsyncClient() as client:
                print(f"[{self.name}] | Calling {target['name']} with: '{search_query}'")
                
                resp = await client.post(
                    target['url'], 
                    json={"query": str(search_query)}, 
                    timeout=15.0
                )
                
                resp.raise_for_status()
                
                data = resp.json()
                output = data.get("response", str(data))
                
                return {"success": True, "agent": target['name'], "output": output}
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            print(f"[{self.name}] | Child Failed: {target['name']} - {error_msg}")
            return {"success": False, "agent": target['name'], "error": error_msg}
            
        except Exception as e:
            print(f"[{self.name}] | Child Error: {target['name']} - {str(e)}")
            return {"success": False, "agent": target['name'], "error": str(e)}

    async def _search_registry(self, intent: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.registry_url}/search", 
                    params={"intent": intent, "exclude": self.name}
                )
                data = resp.json()
                if data.get("found"): return data
        except Exception: pass
        return None
