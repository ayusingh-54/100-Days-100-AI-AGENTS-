"""
Chatbot Simulation Backend Module
==================================
This module provides the core functionality for simulating conversations
between a chatbot and a virtual user using LangChain and LangGraph.

Architecture:
    1. ChatBot: Customer support agent
    2. SimulatedUser: Virtual customer for testing
    3. Simulation Workflow: LangGraph-based conversation flow
    4. Analysis Tools: Conversation evaluation utilities

Author: AI Assistant
Date: October 2025
"""

import os
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.adapters.openai import convert_message_to_dict

# LangGraph imports
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

# OpenAI client
from openai import OpenAI


# ============================================================================
# Configuration Constants
# ============================================================================

class Config:
    """Configuration class for chatbot simulation."""
    
    # Conversation control
    MAX_CONVERSATION_TURNS = 12
    FINISH_KEYWORD = "FINISHED"
    
    # Model settings
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.7
    
    # System prompts
    SUPPORT_BOT_SYSTEM_PROMPT = "You are a customer support agent for an airline."
    
    SIMULATED_USER_SYSTEM_PROMPT = """You are a customer of an airline company.
You are interacting with a customer support person.

{instructions}

When you are finished with the conversation, respond with a single word 'FINISHED'
"""


# ============================================================================
# State Definition
# ============================================================================

class ConversationState(TypedDict):
    """State structure for conversation tracking."""
    messages: Annotated[list, add_messages]


# ============================================================================
# ChatBot Implementation
# ============================================================================

class ChatBot:
    """
    Customer support chatbot implementation.
    Handles customer inquiries using OpenAI's API.
    """
    
    def __init__(self, api_key: str, system_prompt: str = None, model: str = None):
        """
        Initialize the chatbot.
        
        Args:
            api_key (str): OpenAI API key
            system_prompt (str): System prompt for the bot
            model (str): OpenAI model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = system_prompt or Config.SUPPORT_BOT_SYSTEM_PROMPT
        self.model = model or Config.DEFAULT_MODEL
    
    def respond(self, messages: List[dict]) -> dict:
        """
        Generate a response to customer messages.
        
        Args:
            messages (List[dict]): List of conversation messages
            
        Returns:
            dict: Bot's response message
        """
        # Prepend system message
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages
        
        # Get completion from OpenAI
        completion = self.client.chat.completions.create(
            messages=full_messages,
            model=self.model
        )
        
        return completion.choices[0].message.model_dump()


# ============================================================================
# Simulated User Implementation
# ============================================================================

class SimulatedUser:
    """
    Virtual customer for testing chatbot interactions.
    Uses LangChain to generate realistic customer behavior.
    """
    
    def __init__(self, api_key: str, instructions: str, model: str = None, temperature: float = None):
        """
        Initialize the simulated user.
        
        Args:
            api_key (str): OpenAI API key
            instructions (str): Customer scenario/behavior instructions
            model (str): OpenAI model to use
            temperature (float): Response variability (0.0-1.0)
        """
        # Set API key in environment
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Build prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", Config.SIMULATED_USER_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Inject instructions
        self.prompt = self.prompt.partial(instructions=instructions)
        
        # Initialize model
        self.model = ChatOpenAI(
            model=model or Config.DEFAULT_MODEL,
            temperature=temperature or Config.DEFAULT_TEMPERATURE
        )
        
        # Create chain
        self.chain = self.prompt | self.model
    
    def respond(self, messages: list) -> AIMessage:
        """
        Generate customer response based on conversation history.
        
        Args:
            messages (list): List of LangChain messages
            
        Returns:
            AIMessage: Customer's response
        """
        return self.chain.invoke({"messages": messages})


# ============================================================================
# LangGraph Node Functions
# ============================================================================

def create_chatbot_node(chatbot: ChatBot):
    """
    Create a LangGraph node for the chatbot.
    
    Args:
        chatbot (ChatBot): Initialized chatbot instance
        
    Returns:
        function: Node function for LangGraph
    """
    def chatbot_node(state: dict) -> dict:
        """
        Process messages through the customer support bot.
        
        Args:
            state (dict): Current conversation state
            
        Returns:
            dict: State update with bot's response
        """
        messages = state["messages"]
        
        # Convert to OpenAI format
        openai_messages = [convert_message_to_dict(msg) for msg in messages]
        
        # Get bot response
        response = chatbot.respond(openai_messages)
        
        # Return as AIMessage
        return {"messages": [AIMessage(content=response["content"])]}
    
    return chatbot_node


def create_simulated_user_node(simulated_user: SimulatedUser):
    """
    Create a LangGraph node for the simulated user.
    
    Args:
        simulated_user (SimulatedUser): Initialized simulated user instance
        
    Returns:
        function: Node function for LangGraph
    """
    def swap_message_roles(messages: list) -> list:
        """Swap AI and Human message roles for proper conversation flow."""
        swapped = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                swapped.append(HumanMessage(content=msg.content))
            else:
                swapped.append(AIMessage(content=msg.content))
        return swapped
    
    def simulated_user_node(state: dict) -> dict:
        """
        Process messages through the simulated customer.
        
        Args:
            state (dict): Current conversation state
            
        Returns:
            dict: State update with customer's response
        """
        messages = state["messages"]
        
        # Swap roles for user perspective
        swapped = swap_message_roles(messages)
        
        # Get user response
        response = simulated_user.respond(swapped)
        
        # Return as HumanMessage
        return {"messages": [HumanMessage(content=response.content)]}
    
    return simulated_user_node


def create_control_function(max_turns: int = None, finish_keyword: str = None):
    """
    Create conversation control function.
    
    Args:
        max_turns (int): Maximum conversation turns
        finish_keyword (str): Keyword to end conversation
        
    Returns:
        function: Control function for LangGraph
    """
    max_turns = max_turns or Config.MAX_CONVERSATION_TURNS
    finish_keyword = finish_keyword or Config.FINISH_KEYWORD
    
    def should_continue(state: dict) -> str:
        """
        Determine if conversation should continue.
        
        Args:
            state (dict): Current conversation state
            
        Returns:
            str: "continue" or "end"
        """
        messages = state["messages"]
        
        # Check conversation length
        if len(messages) > max_turns:
            return "end"
        
        # Check for finish keyword
        if messages[-1].content.strip() == finish_keyword:
            return "end"
        
        return "continue"
    
    return should_continue


# ============================================================================
# Simulation Manager
# ============================================================================

class SimulationManager:
    """
    Manages the complete chatbot simulation workflow.
    Orchestrates chatbot, simulated user, and LangGraph workflow.
    """
    
    def __init__(
        self,
        api_key: str,
        customer_instructions: str,
        bot_system_prompt: str = None,
        max_turns: int = None,
        model: str = None
    ):
        """
        Initialize the simulation manager.
        
        Args:
            api_key (str): OpenAI API key
            customer_instructions (str): Customer behavior instructions
            bot_system_prompt (str): Chatbot system prompt
            max_turns (int): Maximum conversation turns
            model (str): OpenAI model to use
        """
        self.api_key = api_key
        self.customer_instructions = customer_instructions
        self.bot_system_prompt = bot_system_prompt or Config.SUPPORT_BOT_SYSTEM_PROMPT
        self.max_turns = max_turns or Config.MAX_CONVERSATION_TURNS
        self.model = model or Config.DEFAULT_MODEL
        
        # Initialize components
        self.chatbot = None
        self.simulated_user = None
        self.simulation = None
        self.last_conversation = []
    
    def build_workflow(self):
        """Build the LangGraph workflow."""
        # Initialize chatbot
        self.chatbot = ChatBot(
            api_key=self.api_key,
            system_prompt=self.bot_system_prompt,
            model=self.model
        )
        
        # Initialize simulated user
        self.simulated_user = SimulatedUser(
            api_key=self.api_key,
            instructions=self.customer_instructions,
            model=self.model
        )
        
        # Create nodes
        chatbot_node = create_chatbot_node(self.chatbot)
        user_node = create_simulated_user_node(self.simulated_user)
        control_func = create_control_function(self.max_turns)
        
        # Build graph
        graph_builder = StateGraph(ConversationState)
        
        # Add nodes
        graph_builder.add_node("chat_bot", chatbot_node)
        graph_builder.add_node("user", user_node)
        
        # Define edges
        graph_builder.add_edge(START, "chat_bot")
        graph_builder.add_edge("chat_bot", "user")
        graph_builder.add_conditional_edges(
            "user",
            control_func,
            {
                "continue": "chat_bot",
                "end": END,
            },
        )
        
        # Compile
        self.simulation = graph_builder.compile()
    
    def run_simulation(self) -> List[Dict[str, Any]]:
        """
        Run the complete simulation.
        
        Returns:
            List[Dict]: Conversation history with metadata
        """
        if not self.simulation:
            self.build_workflow()
        
        conversation = []
        turn_count = 0
        
        # Stream simulation
        for chunk in self.simulation.stream({"messages": []}):
            if END not in chunk:
                node_name = list(chunk.keys())[0]
                message = chunk[node_name]["messages"][0]
                
                # Store conversation data
                conversation.append({
                    "turn": turn_count,
                    "speaker": "Bot" if node_name == "chat_bot" else "Customer",
                    "role": node_name,
                    "message": message.content,
                    "timestamp": datetime.now().isoformat()
                })
                
                turn_count += 1
        
        self.last_conversation = conversation
        return conversation
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the last conversation.
        
        Returns:
            Dict: Conversation statistics
        """
        if not self.last_conversation:
            return {}
        
        bot_turns = sum(1 for c in self.last_conversation if c["speaker"] == "Bot")
        customer_turns = sum(1 for c in self.last_conversation if c["speaker"] == "Customer")
        
        return {
            "total_turns": len(self.last_conversation),
            "bot_turns": bot_turns,
            "customer_turns": customer_turns,
            "completed": any(
                Config.FINISH_KEYWORD in c["message"] 
                for c in self.last_conversation
            ),
            "conversation": self.last_conversation
        }


# ============================================================================
# Predefined Scenarios
# ============================================================================

class Scenarios:
    """Predefined customer scenarios for testing."""
    
    REFUND_REQUEST = """Your name is Harrison.
You are trying to get a refund for a trip you took to Alaska.
You want them to give you ALL the money back.
This trip happened 5 years ago."""
    
    FLIGHT_DELAY = """Your name is Sarah.
Your flight was delayed by 8 hours yesterday.
You missed an important meeting because of this.
You want compensation and an explanation."""
    
    BAGGAGE_LOST = """Your name is Michael.
The airline lost your baggage on your international flight.
It contained important documents and medication.
You need urgent help to locate it or get compensation."""
    
    SEAT_UPGRADE = """Your name is Emma.
You have a long 12-hour flight coming up next week.
You want to upgrade to business class if possible.
You're willing to pay extra if needed."""
    
    BOOKING_ISSUE = """Your name is David.
You tried to book a flight online but the payment failed.
However, you were charged on your credit card.
You need this resolved and the flight confirmed."""


# ============================================================================
# Utility Functions
# ============================================================================

def format_conversation_for_display(conversation: List[Dict[str, Any]]) -> str:
    """
    Format conversation for text display.
    
    Args:
        conversation (List[Dict]): Conversation data
        
    Returns:
        str: Formatted conversation text
    """
    output = []
    for turn in conversation:
        speaker = "🤖 SUPPORT BOT" if turn["speaker"] == "Bot" else "👤 CUSTOMER"
        output.append(f"\n{speaker}:")
        output.append(f"{turn['message']}")
        output.append("-" * 60)
    
    return "\n".join(output)


def export_conversation(conversation: List[Dict[str, Any]], format: str = "txt") -> str:
    """
    Export conversation in specified format.
    
    Args:
        conversation (List[Dict]): Conversation data
        format (str): Export format ('txt', 'md', 'json')
        
    Returns:
        str: Formatted export string
    """
    import json
    
    if format == "json":
        return json.dumps(conversation, indent=2)
    
    elif format == "md":
        output = "# Chatbot Simulation Report\n\n"
        output += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        output += "## Conversation\n\n"
        
        for turn in conversation:
            speaker = "🤖 **Support Bot**" if turn["speaker"] == "Bot" else "👤 **Customer**"
            output += f"### {speaker}\n\n"
            output += f"{turn['message']}\n\n"
            output += "---\n\n"
        
        return output
    
    else:  # txt format
        output = "CHATBOT SIMULATION REPORT\n"
        output += "=" * 60 + "\n"
        output += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += "=" * 60 + "\n\n"
        output += format_conversation_for_display(conversation)
        return output


# ============================================================================
# Main Test Function
# ============================================================================

if __name__ == "__main__":
    """Test the backend functionality."""
    import sys
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print("🧪 Testing Chatbot Simulation Backend\n")
    
    # Create simulation manager
    manager = SimulationManager(
        api_key=api_key,
        customer_instructions=Scenarios.REFUND_REQUEST,
        max_turns=6
    )
    
    print("🔧 Building workflow...")
    manager.build_workflow()
    
    print("🚀 Running simulation...\n")
    conversation = manager.run_simulation()
    
    print("📋 Results:")
    print(format_conversation_for_display(conversation))
    
    print("\n📊 Summary:")
    summary = manager.get_conversation_summary()
    print(f"Total turns: {summary['total_turns']}")
    print(f"Completed: {summary['completed']}")
