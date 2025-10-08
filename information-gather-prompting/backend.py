"""
================================================================================
BACKEND.PY - Prompt Generation Agent Backend
================================================================================

This module provides the backend logic for the Prompt Generation AI Agent.
It handles LLM interactions, state management, and workflow orchestration
using LangChain and LangGraph.

Architecture:
    - Modular design with clear separation of concerns
    - Type-safe with comprehensive type hints
    - Stateful conversation management with checkpointing
    - Tool-based structured information extraction

Author: AI Agent Development Team
Version: 1.0.0
Date: October 2025
================================================================================
"""

import os
from typing import List, Literal, Dict, Any, Optional
from typing_extensions import TypedDict
from datetime import datetime
import uuid

# LangChain Core - Message handling and LLM interaction
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)
from langchain_openai import ChatOpenAI

# Pydantic - Data validation and structure
from pydantic import BaseModel, Field

# LangGraph - Graph-based workflow orchestration
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# ============================================================================
# CONFIGURATION - System prompts and constants
# ============================================================================

INFO_GATHERING_TEMPLATE = """Your job is to get information from a user about what type of prompt template they want to create.

You should get the following information from them:

- What the objective of the prompt is
- What variables will be passed into the prompt template
- Any constraints for what the output should NOT do
- Any requirements that the output MUST adhere to

If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.

After you are able to discern all the information, call the relevant tool."""

PROMPT_GENERATION_TEMPLATE = """Based on the following requirements, write a good prompt template:

{reqs}"""


# ============================================================================
# DATA MODELS - Pydantic models for structured data
# ============================================================================

class PromptInfo(BaseModel):
    """
    Structured model for capturing prompt requirements from user.
    
    This model is used as a tool by the LLM to extract structured information
    from conversational input during the information gathering phase.
    
    Attributes:
        objective: The main goal/purpose of the prompt
        variables: List of variables that will be used in the prompt template
        constraints: Things the output should NOT do
        requirements: Things the output MUST do
    """
    objective: str = Field(
        description="The main goal or purpose of the prompt"
    )
    variables: List[str] = Field(
        description="Variables to be used in the prompt template"
    )
    constraints: List[str] = Field(
        description="Things the output should NOT do"
    )
    requirements: List[str] = Field(
        description="Things the output MUST adhere to"
    )


class State(TypedDict):
    """
    State definition for the LangGraph workflow.
    
    The state maintains the conversation history with automatic message merging
    using the add_messages reducer function.
    
    Attributes:
        messages: List of conversation messages (automatically merged)
    """
    messages: List[Any]


class ConversationMetadata(BaseModel):
    """
    Metadata for tracking conversation sessions.
    
    Attributes:
        session_id: Unique identifier for the conversation session
        started_at: Timestamp when conversation started
        last_updated: Timestamp of last message
        message_count: Total number of messages in conversation
        phase: Current phase (info_gathering or prompt_generation)
    """
    session_id: str
    started_at: datetime
    last_updated: datetime
    message_count: int
    phase: str


# ============================================================================
# BACKEND CLASS - Main backend logic
# ============================================================================

class PromptGenerationBackend:
    """
    Backend service for the Prompt Generation AI Agent.
    
    This class encapsulates all backend logic including:
    - LLM initialization and configuration
    - Workflow graph creation and management
    - Message processing and routing
    - Session management
    
    Attributes:
        llm: The OpenAI language model instance
        graph: The compiled LangGraph workflow
        memory: Checkpoint saver for conversation persistence
        sessions: Dictionary tracking active sessions
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0):
        """
        Initialize the backend with LLM and workflow configuration.
        
        Args:
            model: OpenAI model name (default: gpt-4)
            temperature: LLM temperature for response generation (default: 0)
        """
        # Initialize LLM
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # Initialize memory for checkpointing
        self.memory = InMemorySaver()
        
        # Build the workflow graph
        self.graph = self._build_graph()
        
        # Track active sessions
        self.sessions: Dict[str, ConversationMetadata] = {}
        
    
    # ========================================================================
    # HELPER FUNCTIONS - Message processing and filtering
    # ========================================================================
    
    def _get_info_messages(self, messages: list) -> list:
        """
        Prepare messages for the information gathering phase.
        
        Adds the system prompt to the beginning of the conversation to guide
        the LLM in extracting structured requirements from the user.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List with system message prepended to conversation history
        """
        return [SystemMessage(content=INFO_GATHERING_TEMPLATE)] + messages
    
    
    def _get_prompt_messages(self, messages: list) -> list:
        """
        Extract messages for the prompt generation phase.
        
        This function:
        1. Finds the tool call containing user requirements
        2. Filters out tool messages from the conversation
        3. Only includes messages AFTER the tool call
        4. Formats the system prompt with extracted requirements
        
        Args:
            messages: Full conversation history
            
        Returns:
            List of messages starting with formatted system prompt
        """
        tool_call = None
        other_msgs = []
        
        # Iterate through messages to find tool call and subsequent messages
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                # Extract the requirements from tool call arguments
                tool_call = msg.tool_calls[0]["args"]
            elif isinstance(msg, ToolMessage):
                # Skip tool messages in output (internal workflow only)
                continue
            elif tool_call is not None:
                # Include messages that came after tool call
                other_msgs.append(msg)
        
        # Create system message with requirements embedded
        system_msg = SystemMessage(
            content=PROMPT_GENERATION_TEMPLATE.format(reqs=tool_call)
        )
        
        return [system_msg] + other_msgs
    
    
    def _get_next_state(self, state: State) -> Literal["add_tool_message", "info", str]:
        """
        Determine the next state in the workflow based on the last message.
        
        State transition logic:
        1. If last message is AI with tool calls → "add_tool_message"
        2. If last message is not Human → END (conversation complete)
        3. Otherwise → "info" (continue gathering information)
        
        Args:
            state: Current workflow state
            
        Returns:
            Next state name or END
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if AI made a tool call (requirements gathered)
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "add_tool_message"
        
        # Check if waiting for human input
        elif not isinstance(last_message, HumanMessage):
            return END
        
        # Continue gathering information
        return "info"
    
    
    # ========================================================================
    # NODE FUNCTIONS - Core processing functions for each graph node
    # ========================================================================
    
    def _info_gathering_node(self, state: State) -> dict:
        """
        Node for gathering information from the user.
        
        This node:
        1. Prepares messages with the info gathering system prompt
        2. Binds the PromptInfo tool to the LLM for structured extraction
        3. Invokes the LLM to either ask clarifying questions or extract requirements
        
        Args:
            state: Current workflow state with message history
            
        Returns:
            Dictionary with new messages to add to state
        """
        # Prepare messages with system prompt
        messages = self._get_info_messages(state["messages"])
        
        # Bind the PromptInfo tool so LLM can extract structured data
        llm_with_tool = self.llm.bind_tools([PromptInfo])
        
        # Invoke LLM to process conversation
        response = llm_with_tool.invoke(messages)
        
        # Return response wrapped in dict for state update
        return {"messages": [response]}
    
    
    def _prompt_generation_node(self, state: State) -> dict:
        """
        Node for generating the final prompt template.
        
        This node:
        1. Extracts requirements from previous tool call
        2. Creates a new system prompt with those requirements
        3. Generates the final prompt template based on requirements
        
        Args:
            state: Current workflow state with complete requirements
            
        Returns:
            Dictionary with the generated prompt message
        """
        # Get messages filtered for prompt generation phase
        messages = self._get_prompt_messages(state["messages"])
        
        # Generate the prompt using LLM
        response = self.llm.invoke(messages)
        
        # Return the generated prompt
        return {"messages": [response]}
    
    
    def _add_tool_message_node(self, state: State) -> dict:
        """
        Node to add a tool message confirming requirements were extracted.
        
        This is a bridge node that:
        1. Acknowledges the tool call from info gathering
        2. Provides a confirmation message
        3. Transitions the workflow to prompt generation phase
        
        Args:
            state: Current state with tool call from info gathering
            
        Returns:
            Dictionary with tool confirmation message
        """
        # Get the tool call ID from the last AI message
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        
        # Create a tool message to acknowledge the requirements
        tool_msg = ToolMessage(
            content="Requirements received! Generating your prompt...",
            tool_call_id=tool_call_id
        )
        
        return {"messages": [tool_msg]}
    
    
    # ========================================================================
    # GRAPH CONSTRUCTION
    # ========================================================================
    
    def _build_graph(self) -> StateGraph:
        """
        Create and configure the prompt generation workflow graph.
        
        Graph Structure:
        
            START → info → [Conditional Routing]
                            ├─→ add_tool_message → prompt → END
                            ├─→ info (loop back for more questions)
                            └─→ END (conversation ended)
        
        Nodes:
            - info: Gathers requirements from user through conversation
            - add_tool_message: Confirms requirements were extracted
            - prompt: Generates the final prompt template
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Initialize the graph with State schema
        workflow = StateGraph(State)
        
        # Add nodes to the graph
        workflow.add_node("info", self._info_gathering_node)
        workflow.add_node("add_tool_message", self._add_tool_message_node)
        workflow.add_node("prompt", self._prompt_generation_node)
        
        # Set entry point
        workflow.add_edge(START, "info")
        
        # Add conditional routing from info node
        workflow.add_conditional_edges(
            "info",
            self._get_next_state,
            {
                "add_tool_message": "add_tool_message",  # Requirements gathered
                "info": "info",                          # Continue gathering
                END: END                                  # Conversation ended
            }
        )
        
        # Add edges for the prompt generation flow
        workflow.add_edge("add_tool_message", "prompt")
        workflow.add_edge("prompt", END)
        
        # Compile the graph with checkpointing enabled
        graph = workflow.compile(checkpointer=self.memory)
        
        return graph
    
    
    # ========================================================================
    # PUBLIC API METHODS
    # ========================================================================
    
    def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            Unique session ID for tracking the conversation
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session metadata
        self.sessions[session_id] = ConversationMetadata(
            session_id=session_id,
            started_at=datetime.now(),
            last_updated=datetime.now(),
            message_count=0,
            phase="info_gathering"
        )
        
        return session_id
    
    
    def send_message(
        self, 
        message: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User's message text
            session_id: Session identifier for conversation tracking
            
        Returns:
            Dictionary containing:
                - response: The agent's response text
                - session_id: Session identifier
                - phase: Current conversation phase
                - metadata: Additional conversation metadata
        """
        # Validate session exists
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        # Create configuration for graph execution with session
        config = {"configurable": {"thread_id": session_id}}
        
        # Prepare input state
        input_state = {"messages": [HumanMessage(content=message)]}
        
        # Invoke the graph with the user's message
        result = self.graph.invoke(input_state, config)
        
        # Extract the agent's response
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        # Update session metadata
        metadata = self.sessions[session_id]
        metadata.last_updated = datetime.now()
        metadata.message_count += 2  # User message + AI response
        
        # Determine current phase based on message types
        has_tool_call = any(
            isinstance(msg, AIMessage) and msg.tool_calls 
            for msg in result["messages"]
        )
        if has_tool_call:
            metadata.phase = "prompt_generation"
        
        # Return response with metadata
        return {
            "response": response_text,
            "session_id": session_id,
            "phase": metadata.phase,
            "metadata": {
                "message_count": metadata.message_count,
                "started_at": metadata.started_at.isoformat(),
                "last_updated": metadata.last_updated.isoformat()
            }
        }
    
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve the full conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        # Get state from checkpointer
        config = {"configurable": {"thread_id": session_id}}
        state = self.graph.get_state(config)
        
        # Convert messages to simple dict format
        history = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                if not msg.tool_calls:  # Skip tool call messages
                    history.append({"role": "assistant", "content": msg.content})
            # Skip SystemMessage and ToolMessage for cleaner history
        
        return history
    
    
    def reset_session(self, session_id: str) -> None:
        """
        Reset a session, clearing all conversation history.
        
        Args:
            session_id: Session identifier to reset
        """
        if session_id in self.sessions:
            # Remove session metadata
            del self.sessions[session_id]
            
            # Note: LangGraph's InMemorySaver doesn't have explicit delete
            # New session will override the old thread_id
    
    
    def get_session_metadata(self, session_id: str) -> Optional[ConversationMetadata]:
        """
        Get metadata for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationMetadata object or None if session doesn't exist
        """
        return self.sessions.get(session_id)


# ============================================================================
# SINGLETON INSTANCE - Reusable backend instance
# ============================================================================

# Create a global backend instance for use across the application
_backend_instance = None

def get_backend() -> PromptGenerationBackend:
    """
    Get or create the backend singleton instance.
    
    Returns:
        PromptGenerationBackend instance
    """
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = PromptGenerationBackend()
    return _backend_instance


# ============================================================================
# TESTING - Quick test when run as main module
# ============================================================================

if __name__ == "__main__":
    """Test the backend functionality."""
    
    print("🚀 Testing Prompt Generation Backend\n")
    
    # Initialize backend
    backend = get_backend()
    print("✅ Backend initialized")
    
    # Create a session
    session_id = backend.create_session()
    print(f"✅ Session created: {session_id}\n")
    
    # Test conversation
    test_messages = [
        "I want to create a prompt for code review",
        "It should review Python code for best practices and security",
        "Variables: code_snippet, language, focus_areas",
        "It should not suggest major refactoring, only point out issues",
        "It must provide specific line numbers and explanations"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"👤 User: {msg}")
        response = backend.send_message(msg, session_id)
        print(f"🤖 Agent: {response['response']}\n")
        print(f"   Phase: {response['phase']}")
        print(f"   Messages: {response['metadata']['message_count']}\n")
    
    print("✅ Test completed successfully!")
