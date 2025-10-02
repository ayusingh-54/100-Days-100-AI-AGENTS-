"""
Customer Support Agent Backend
This module contains the core logic for the customer support agent using LangGraph.
"""

from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')


class State(TypedDict):
    """State structure to hold query information throughout the workflow."""
    query: str
    category: str
    sentiment: str
    response: str


class CustomerSupportAgent:
    """Main class for the customer support agent workflow."""
    
    def __init__(self, temperature: float = 0):
        """
        Initialize the customer support agent.
        
        Args:
            temperature (float): Temperature parameter for the language model
        """
        self.temperature = temperature
        self.app = self._build_workflow()
    
    def categorize(self, state: State) -> State:
        """
        Categorize the customer query into Technical, Billing, or General.
        
        Args:
            state (State): Current state containing the query
            
        Returns:
            State: Updated state with category
        """
        prompt = ChatPromptTemplate.from_template(
            "Categorize the following customer query into one of these categories: "
            "Technical, Billing, General. Query: {query}"
        )
        chain = prompt | ChatOpenAI(temperature=self.temperature)
        category = chain.invoke({"query": state["query"]}).content
        return {"category": category}
    
    def analyze_sentiment(self, state: State) -> State:
        """
        Analyze the sentiment of the customer query.
        
        Args:
            state (State): Current state containing the query
            
        Returns:
            State: Updated state with sentiment
        """
        prompt = ChatPromptTemplate.from_template(
            "Analyze the sentiment of the following customer query. "
            "Respond with either 'Positive', 'Neutral', or 'Negative'. Query: {query}"
        )
        chain = prompt | ChatOpenAI(temperature=self.temperature)
        sentiment = chain.invoke({"query": state["query"]}).content
        return {"sentiment": sentiment}
    
    def handle_technical(self, state: State) -> State:
        """
        Provide a technical support response to the query.
        
        Args:
            state (State): Current state containing the query
            
        Returns:
            State: Updated state with response
        """
        prompt = ChatPromptTemplate.from_template(
            "Provide a technical support response to the following query: {query}"
        )
        chain = prompt | ChatOpenAI(temperature=self.temperature)
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    
    def handle_billing(self, state: State) -> State:
        """
        Provide a billing support response to the query.
        
        Args:
            state (State): Current state containing the query
            
        Returns:
            State: Updated state with response
        """
        prompt = ChatPromptTemplate.from_template(
            "Provide a billing support response to the following query: {query}"
        )
        chain = prompt | ChatOpenAI(temperature=self.temperature)
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    
    def handle_general(self, state: State) -> State:
        """
        Provide a general support response to the query.
        
        Args:
            state (State): Current state containing the query
            
        Returns:
            State: Updated state with response
        """
        prompt = ChatPromptTemplate.from_template(
            "Provide a general support response to the following query: {query}"
        )
        chain = prompt | ChatOpenAI(temperature=self.temperature)
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    
    def escalate(self, state: State) -> State:
        """
        Escalate the query to a human agent due to negative sentiment.
        
        Args:
            state (State): Current state
            
        Returns:
            State: Updated state with escalation message
        """
        return {"response": "This query has been escalated to a human agent due to its negative sentiment."}
    
    def route_query(self, state: State) -> str:
        """
        Route the query based on its sentiment and category.
        
        Args:
            state (State): Current state with category and sentiment
            
        Returns:
            str: Name of the next node to execute
        """
        if state["sentiment"] == "Negative":
            return "escalate"
        elif state["category"] == "Technical":
            return "handle_technical"
        elif state["category"] == "Billing":
            return "handle_billing"
        else:
            return "handle_general"
    
    def _build_workflow(self) -> StateGraph:
        """
        Build and compile the LangGraph workflow.
        
        Returns:
            StateGraph: Compiled workflow graph
        """
        # Create the graph
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("categorize", self.categorize)
        workflow.add_node("analyze_sentiment", self.analyze_sentiment)
        workflow.add_node("handle_technical", self.handle_technical)
        workflow.add_node("handle_billing", self.handle_billing)
        workflow.add_node("handle_general", self.handle_general)
        workflow.add_node("escalate", self.escalate)
        
        # Add edges
        workflow.add_edge("categorize", "analyze_sentiment")
        workflow.add_conditional_edges(
            "analyze_sentiment",
            self.route_query,
            {
                "handle_technical": "handle_technical",
                "handle_billing": "handle_billing",
                "handle_general": "handle_general",
                "escalate": "escalate"
            }
        )
        workflow.add_edge("handle_technical", END)
        workflow.add_edge("handle_billing", END)
        workflow.add_edge("handle_general", END)
        workflow.add_edge("escalate", END)
        
        # Set entry point
        workflow.set_entry_point("categorize")
        
        # Compile the graph
        return workflow.compile()
    
    def process_query(self, query: str) -> Dict[str, str]:
        """
        Process a customer query through the LangGraph workflow.
        
        Args:
            query (str): The customer's query
            
        Returns:
            Dict[str, str]: A dictionary containing the query's category, sentiment, and response
        """
        results = self.app.invoke({"query": query})
        return {
            "category": results["category"],
            "sentiment": results["sentiment"],
            "response": results["response"]
        }
    
    def get_graph_image(self):
        """
        Get the visual representation of the workflow graph.
        
        Returns:
            bytes: PNG image of the graph
        """
        from langchain_core.runnables.graph import MermaidDrawMethod
        return self.app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )


# Convenience function for direct usage
def run_customer_support(query: str) -> Dict[str, str]:
    """
    Process a customer query through the customer support agent.
    
    Args:
        query (str): The customer's query
        
    Returns:
        Dict[str, str]: A dictionary containing the query's category, sentiment, and response
    """
    agent = CustomerSupportAgent()
    return agent.process_query(query)
