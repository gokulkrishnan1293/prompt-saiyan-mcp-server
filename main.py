from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware

# --- MCP Server Configuration ---
SERVER_NAME = "prompt_enricher_mcp_server"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "MCP Server for enriching prompts based on project context."


class WorkspaceInfo(BaseModel):
    file_counts: Dict[str, int]
    project_type: str
    original_heuristic: str

class EnrichPromptInput(BaseModel):
    raw_prompt: str
    workspace_info: WorkspaceInfo

class EnrichedPromptData(BaseModel):
    enriched_prompt: str

class EnrichPromptOutput(BaseModel):
    data: EnrichedPromptData

async def enrich_prompt_tool(params: EnrichPromptInput) -> EnrichPromptOutput:
    enriched_prompt_text = params.raw_prompt
    if params.workspace_info.project_type == "frontend":
        # Example: Append a specific instruction for frontend projects
        enriched_prompt_text = f"{params.raw_prompt} Important: Consider modern frontend frameworks and responsive design principles."
    elif params.workspace_info.project_type == "backend-api":
        enriched_prompt_text = f"{params.raw_prompt} Important: Focus on scalability, security, and database interactions."
    elif params.workspace_info.project_type == "database":
        enriched_prompt_text = f"{params.raw_prompt} Important: Focus on scalability, security, and database interactions."
    else:
        enriched_prompt_text = ""

    return EnrichPromptOutput(data=EnrichedPromptData(enriched_prompt=enriched_prompt_text))


# --- Resource Definitions ---
# Example Resource: server_status
async def get_server_status_resource():
    return {"status": "running", "version": SERVER_VERSION}

# --- MCP Manifest ---
class MCPToolParameter(BaseModel):
    name: str
    description: str
    type: str 
    required: bool


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, MCPToolParameter] 
    output_schema: Dict[str, Any] 

class MCPResourceDefinition(BaseModel):
    uri_pattern: str 
    description: str
    

class MCPManifest(BaseModel):
    mcp_version: str = "1.0"
    server_name: str
    server_version: str
    description: str
    tools: List[MCPToolDefinition]
    resources: List[MCPResourceDefinition]

# --- FastAPI App ---
app = FastAPI(
    title=SERVER_NAME,
    version=SERVER_VERSION,
    description=SERVER_DESCRIPTION,
)

# Configure CORS
origins = [
    "*", 
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)


# --- MCP Endpoints ---
@app.get("/manifest", response_model=MCPManifest)
async def get_mcp_manifest():
    return MCPManifest(
        server_name=SERVER_NAME,
        server_version=SERVER_VERSION,
        description=SERVER_DESCRIPTION,
        tools=[
            MCPToolDefinition(
                name="enrich_prompt",
                description="Enriches a raw prompt based on workspace information.",
                input_schema={
                    "raw_prompt": MCPToolParameter(name="raw_prompt", description="The initial prompt text.", type="string", required=True),
                    "workspace_info": MCPToolParameter(
                        name="workspace_info",
                        description="Information about the workspace/project.",
                        type="object", # Pydantic model will be validated
                        required=false,
                        
                    ),
                },
                output_schema={ 
                    "data": {
                        "type": "object",
                        "properties": {
                            "enriched_prompt": {"type": "string"}
                        }
                    }
                }
            )
        ],
        resources=[
            MCPResourceDefinition(
                uri_pattern="mcp://status",
                description="Provides the current status of the server."
            )
        ]
    )

class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

@app.post("/execute_tool", response_model=Any) # Adjust response_model as needed
async def execute_mcp_tool(request: ExecuteToolRequest):
    if request.tool_name == "enrich_prompt":
        try:
            input_data = EnrichPromptInput(**request.arguments)
            result = await enrich_prompt_tool(input_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing tool '{request.tool_name}' (enrich_prompt): {str(e)}")
    else:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found.")

class AccessResourceRequest(BaseModel): 
    uri: str

@app.get("/access_resource", response_model=Any) 
async def access_mcp_resource(uri: str): 
    if uri == "mcp://status":
        try:
            result = await get_server_status_resource()
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error accessing resource '{uri}': {str(e)}")
    else:
        raise HTTPException(status_code=404, detail=f"Resource with URI '{uri}' not found.")

# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)