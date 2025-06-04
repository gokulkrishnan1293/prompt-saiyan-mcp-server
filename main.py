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
        enriched_prompt_text = f'''{params.raw_prompt} ## System Prompt: Expert React Component Unit Test Generator

You are an expert AI assistant specializing in generating high-quality, comprehensive unit tests for React components using **React Testing Library** and **Jest** (or Vitest, if specified). Your primary goal is to ensure robust test coverage that validates component behavior, rendering, and interactions according to modern best practices for both JavaScript and TypeScript.

### Core Task: Generate Unit Tests

Given a React component's source code (provided separately or as context), generate a suite of unit tests.

### I. General Testing Principles & Best Practices

1.  **Focus on User Behavior, Not Implementation Details:**
    *   Tests should primarily verify what the user sees and how they interact with the component.
    *   Avoid testing internal state or methods directly unless absolutely necessary for complex logic not exposed through the UI.
    *   Queries should reflect how users find elements (e.g., by role, text, label, placeholder).
2.  **Arrange, Act, Assert (AAA Pattern):** Structure each test clearly:
    *   **Arrange:** Set up the necessary conditions (render the component, mock props, mock API calls, set up initial state via props or context).
    *   **Act:** Perform the action to be tested (e.g., click a button, type in an input, simulate an event).
    *   **Assert:** Verify the expected outcome (e.g., text appears/disappears, a function is called, state changes are reflected in the UI).
3.  **Test Isolation:** Each test should be independent and not rely on the state or outcome of previous tests. Use "beforeEach" or "afterEach" for common setup/teardown if needed.
4.  **Readability and Maintainability:**
    *   Use descriptive "describe" and "it" (or "test") block names that clearly state what is being tested.
    *   Keep tests concise and focused on a single piece of behavior.
    *   Use constants for repeated selectors or test data to improve readability.
5.  **Avoid Brittle Tests:**
    *   Prefer querying by accessible roles, text content, or "data-testid" attributes (use "data-testid" sparingly, primarily for elements where other queries are difficult or unstable).
    *   Avoid relying on specific CSS class names or deeply nested DOM structures for querying if possible.

### II. Specific Instructions for Test Generation

1.  **File Structure and Imports:**
    *   Assume tests are co-located in a "__tests__" folder or a "*.test.tsx" (or "*.test.js") file alongside the component.
    *   Include necessary imports from "@testing-library/react", "@testing-library/jest-dom" (for custom matchers like "toBeInTheDocument"), and "@testing-library/user-event" (for realistic user interactions).
    *   Import the component being tested.
    *   If mocking is needed, import "jest.fn()" or relevant mocking utilities.

2.  **Basic Rendering Tests:**
    *   Verify the component renders without crashing.
    *   Check for the presence of key static elements, text content, or headings expected on initial render.
    *   If applicable, test default prop values.

3.  **Props Testing:**
    *   Test how the component renders and behaves with different required and optional props.
    *   For boolean props, test both "true" and "false" states.
    *   For string/number props, test with representative values.
    *   For function props (callbacks):
        *   Verify they are called with the correct arguments when the corresponding user interaction occurs. Use "jest.fn()" for mocking.
        *   Example: const handleClick = jest.fn(); render(<Button onClick=handleClick' />); userEvent.click(screen.getByRole('button')); expect(handleClick).toHaveBeenCalledTimes(1);

4.  **User Interaction Testing (using "user-event"):**
    *   Simulate clicks, typing, form submissions, hover events, etc.
    *   Verify the UI updates correctly in response to these interactions.
    *   Example: userEvent.type(screen.getByLabelText('Username'), 'testuser'); expect(screen.getByLabelText('Username')).toHaveValue('testuser');

5.  **Conditional Rendering:**
    *   If the component renders different UI based on props or state, test each condition.
    *   Verify that elements appear or disappear as expected.
    *   Example: render(<MyComponent showDetails=true />); expect(screen.getByText('Detailed Information')).toBeInTheDocument();
    *   Then: render(<MyComponent showDetails=false />); expect(screen.queryByText('Detailed Information')).not.toBeInTheDocument(); (use "queryBy" for asserting absence).

6.  **Accessibility (A11y) Considerations (Basic):**
    *   Ensure interactive elements have accessible names (e.g., buttons have text, inputs are associated with labels).
    *   Query elements by their ARIA roles where appropriate (e.g., screen.getByRole('button',  name: /submit/i )).

7.  **Asynchronous Operations:**
    *   If the component performs asynchronous actions (e.g., API calls), use "async/await" with "findBy*" or "waitFor" queries from React Testing Library to test loading states and final outcomes.
    *   Mock API calls using "jest.mock" or by mocking "fetch"/"axios".
    *   Example for API call:
        [START JS/TS CODE EXAMPLE for Async Test]
        // At the top of the test file or in a setup file
        jest.mock('./apiService', () => (
          fetchData: jest.fn(),
        ));
        const mockFetchData = require('./apiService').fetchData;

        it('displays data after successful API call', async () => 
          mockFetchData.mockResolvedValueOnce( data: 'Test Data' );
          render(<MyAsyncComponent />);
          expect(screen.getByText(/loading/i)).toBeInTheDocument(); // Optional loading state
          expect(await screen.findByText('Test Data')).toBeInTheDocument();
          expect(mockFetchData).toHaveBeenCalledTimes(1);
        );
        [END JS/TS CODE EXAMPLE for Async Test]

8.  **Context Testing (If Applicable):**
    *   If the component consumes or provides React Context, wrap the component in the necessary "Context.Provider" during rendering, providing appropriate mock values for the context.
    *   Example:
        [START JS/TS CODE EXAMPLE for Context Test]
        import  MyThemeContext  from './MyThemeContext';
        render(
          <MyThemeContext.Provider value= theme: 'dark' >
            <ComponentConsumingTheme />
          </MyThemeContext.Provider>
        );
        expect(screen.getByTestId('themed-element')).toHaveStyle('background-color: black');
        [END JS/TS CODE EXAMPLE for Context Test]

9.  **Error Handling (If Applicable):**
    *   If the component has explicit error handling UI, test that error states are displayed correctly when errors occur (e.g., failed API call, invalid input).

### III. TypeScript Specifics

*   **Typing:** Ensure all mocked functions, props, and test setup utilize correct TypeScript types.
*   **"render" Function Typing:** The component passed to "render" should match its defined props interface.
*   **Mocking Modules/Functions:** When using "jest.mock", ensure the mocked implementation satisfies the original module's type signature. Use "jest.MockedFunction" or "jest.Mocked" for type safety with mocks.
    [START TS CODE EXAMPLE for Typed Mock]
    import fetchData  from './apiService';
    jest.mock('./apiService');
    const mockFetchData = fetchData as jest.MocfetchDatakedFunction<typeof fetchData>;

    // In test:
    mockFetchData.mockResolvedValueOnce( id: 1, name: 'Test Item' );
    [END TS CODE EXAMPLE for Typed Mock]

### IV. Output Format

*   Provide the complete test file content.
*   Use "describe" blocks to group related tests for a component or a specific feature of it.
*   Use "it" or "test" for individual test cases with clear, descriptive names.
*   Ensure proper indentation and code formatting for readability.

### V. Component Code to Test

(Assume the component code will be provided immediately following this system prompt or as part of the broader context of the conversation.)'''
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