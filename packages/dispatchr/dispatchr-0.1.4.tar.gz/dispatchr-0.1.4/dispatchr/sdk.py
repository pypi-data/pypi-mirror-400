import inspect
import requests
import functools

def get_type_name(t):
    """
    Helper to convert python type to json schema type
    """
    if t == int:
        return "integer"
    elif t == str:
        return "string"
    elif t == bool:
        return "boolean"
    elif t == float:
        return "number"
    elif t == list:
        return "array"
    elif t == dict:
        return "object"
    else:
        return "string"

def register(url: str, registry_url: str = "http://localhost:8000/register", overwrite: bool = False):
    """
    Decorator to automatically register an agent
    Usage: @register(url, registry_url="...", overwrite=True)
    """
    def decorator(func):
        agent_name = func.__name__
        if not func.__doc__:
            agent_description = ""
        else:
            agent_description = func.__doc__.strip()

        sig = inspect.signature(func)
        parameters = {}
        for name, param in sig.parameters.items():
            param_type = get_type_name(param.annotation)
            parameters[name] = {"type": param_type}

        schema = {
            "type": "object",
            "properties": parameters,
            "required": list(parameters.keys())
        }

        payload = {
            "name": agent_name,
            "description": agent_description,
            "url": url,
            "domain": "default", # Hardcoded default for compatibility
            "agent_schema": schema
        }

        try:
            params = {"overwrite": overwrite}
            # Use the provided registry_url
            response = requests.post(registry_url, json=payload, params=params)
            response.raise_for_status()
            print(f"Registered '{agent_name}' with Agentic Directory!")
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 409:
                print(f"Agent '{agent_name}' already registered (ignoring).")
            elif e.response is not None:
                try:
                    detail = e.response.json().get("detail", e.response.text)
                except ValueError:
                    detail = e.response.text
                error_msg = f"Failed to register agent '{agent_name}'. Server responded: {detail}"
                print(error_msg)
                raise Exception(error_msg) from None
            else:
                error_msg = f"Failed to register agent '{agent_name}': {e}"
                print(error_msg)
                raise Exception(error_msg) from None
    
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator