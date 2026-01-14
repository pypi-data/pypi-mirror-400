import json
import chromadb
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

class AgentRegistration(BaseModel):
    name: str
    description: str
    url: str
    domain: str = "default"
    agent_schema: Dict[str, Any]

class DeleteRequest(BaseModel):
    names: List[str] = []
    delete_all: bool = False

class Registry:
    def __init__(self, chroma_path: str = "./chroma"):
        self.app = FastAPI(title="Agentic Registry")
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(name="agent")
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/register")
        async def register_agent(agent: AgentRegistration, overwrite: bool = False):
            """
            Register a new agent
            """
            try:
                if not agent.description:
                    raise HTTPException(status_code=400, detail="Description is required")

                if not overwrite:
                    existing = self.collection.get(ids=[agent.name])
                    if existing["ids"]:
                        raise HTTPException(status_code=409, detail=f"Agent with name '{agent.name}' already exists")

                print("Registering agent: ", agent.name)
                self.collection.upsert(
                    documents=[agent.description],
                    metadatas=[{
                        "name": agent.name,
                        "url": agent.url,
                        "domain": agent.domain,
                        "schema": json.dumps(agent.agent_schema)
                    }],
                    ids=[agent.name]
                )
                return {"status": "registered", "agent": agent.name}
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/search")
        async def search_agents(intent: str, domain: str = "default", exclude: Optional[str] = None):
            """
            Search for agents based on intent
            (Domain ignored for now, but kept in signature for compatibility)
            """
            try:
                print(f"Searching for agents with intent: '{intent}' (exclude: {exclude})")
                
                # Query more results so we can filter out the excluded agent
                results = self.collection.query(
                    query_texts=[intent],
                    n_results=5 
                )

                if not results["ids"][0]:
                    return {"found": False}
                
                # Iterate through results and pick the first one that is NOT the excluded agent
                best_match = None
                for i, agent_id in enumerate(results["ids"][0]):
                     if exclude and agent_id == exclude:
                         continue
                     
                     # Found a valid one
                     metadata = results["metadatas"][0][i]
                     best_match = {
                        "found": True, 
                        "name": metadata["name"],
                        "url": metadata["url"],
                        "agent_schema": json.loads(metadata["schema"])
                     }
                     break
                
                if best_match:
                    return best_match
                    
                return {"found": False}

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/ping")
        async def ping():
            """
            Health check ensuring registry is running
            Returns names of all agents and total count
            """
            try:
                all_agents = self.collection.get()
                agent_names = all_agents["ids"]
                return {
                    "status": "alive",
                    "total_agents": len(agent_names),
                    "agents": agent_names
                }
            except Exception as e:
                 raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/delete")
        async def delete_agents(request: DeleteRequest):
            """
            Delete agents.
            - Provide 'names' list to delete specific agents.
            - Set 'delete_all' to true (or send "ALL" in names) to wipe registry.
            """
            try:
                if request.delete_all or "ALL" in request.names:
                    print("DELETE REQUEST: Wiping all agents...")
                    
                    all_data = self.collection.get()
                    all_ids = all_data["ids"]
                    
                    if not all_ids:
                        return {"status": "empty", "message": "Registry was already empty."}

                    self.collection.delete(ids=all_ids)
                    return {"status": "deleted", "count": len(all_ids), "message": "All agents removed."}

                if request.names:
                    print(f"DELETE REQUEST: Removing {request.names}")
                    
                    existing = self.collection.get(ids=request.names)
                    found_ids = existing["ids"]
                    
                    if not found_ids:
                        return {"status": "failed", "message": "No matching agents found to delete."}
                    
                    self.collection.delete(ids=found_ids)
                    return {
                        "status": "deleted", 
                        "deleted_agents": found_ids,
                        "requested_count": len(request.names),
                        "actual_deleted_count": len(found_ids)
                    }

                return {"status": "no_action", "message": "No names provided and delete_all is False."}

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

def run():
    import argparse
    parser = argparse.ArgumentParser(description="Start the Agentic Registry")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    registry = Registry()
    registry.run(host=args.host, port=args.port)

if __name__ == "__main__":
    run()