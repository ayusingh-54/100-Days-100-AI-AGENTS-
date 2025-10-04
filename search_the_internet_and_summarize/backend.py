"""
Backend Module for AI-Powered Web Research Tool
================================================
This module provides the core functionality for web searching and AI-powered summarization.
It includes modular classes for search engines, summarization, and result management.

Author: AI Assistant
Date: October 2025
"""

import os
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import json

from langchain.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv


# ============================================================================
# Configuration and Environment Setup
# ============================================================================

class Config:
    """Configuration class for managing application settings."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.default_model = "gpt-4o-mini"
        self.default_temperature = 0.7
        self.max_results = 3
        
        # Validate API key
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        os.environ["OPENAI_API_KEY"] = self.openai_api_key


# ============================================================================
# Data Models
# ============================================================================

class SearchResult(BaseModel):
    """Model for individual search results."""
    snippet: str = Field(..., description="Preview text from the search result")
    title: str = Field(..., description="Title of the search result")
    link: str = Field(..., description="URL of the search result")


class SearchQuery(BaseModel):
    """Model for search query parameters."""
    query: str = Field(..., description="The search query text")
    specific_site: Optional[str] = Field(None, description="Optional specific website to search within")
    max_results: int = Field(3, description="Maximum number of results to return")


# ============================================================================
# Search Engine Module
# ============================================================================

class SearchEngine:
    """
    Handles web searching using DuckDuckGo search engine.
    Provides methods for general and site-specific searches.
    """
    
    def __init__(self):
        """Initialize the search engine."""
        self.search_tool = DuckDuckGoSearchResults()
        self.search_history: List[Dict[str, Any]] = []
    
    def parse_search_results(self, results_string: str) -> List[Dict[str, str]]:
        """
        Parse raw search results string into structured format.
        
        Args:
            results_string (str): Raw search results from DuckDuckGo
            
        Returns:
            List[Dict[str, str]]: Parsed results with snippet, title, and link
        """
        results = []
        
        try:
            # Split by snippet delimiter
            entries = results_string.split(', snippet: ')
            
            for entry in entries[1:]:  # Skip first empty split
                parts = entry.split(', title: ')
                
                if len(parts) == 2:
                    snippet = parts[0].strip()
                    title_link = parts[1].split(', link: ')
                    
                    if len(title_link) == 2:
                        title = title_link[0].strip()
                        link = title_link[1].strip()
                        
                        results.append({
                            'snippet': snippet,
                            'title': title,
                            'link': link
                        })
        except Exception as e:
            print(f"Error parsing search results: {str(e)}")
        
        return results
    
    def search(self, query: str, site: Optional[str] = None, max_results: int = 3) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Perform web search based on query with optional site restriction.
        
        Args:
            query (str): Search query
            site (Optional[str]): Specific website to search within
            max_results (int): Maximum number of results to return
            
        Returns:
            Tuple containing:
                - List of text snippets
                - List of tuples with (title, link) pairs
        """
        try:
            combined_results = []
            
            if site:
                # Site-specific search
                specific_query = f"site:{site} {query}"
                print(f"🔍 Searching within {site}: {query}")
                specific_results = self.search_tool.run(specific_query)
                specific_parsed = self.parse_search_results(specific_results)
                
                # General search excluding the site
                general_query = f"-site:{site} {query}"
                print(f"🔍 Searching general web (excluding {site}): {query}")
                general_results = self.search_tool.run(general_query)
                general_parsed = self.parse_search_results(general_results)
                
                # Combine results (prioritize site-specific)
                combined_results = (specific_parsed + general_parsed)[:max_results]
            else:
                # General web search
                print(f"🔍 Searching: {query}")
                web_results = self.search_tool.run(query)
                combined_results = self.parse_search_results(web_results)[:max_results]
            
            # Extract snippets and sources
            web_knowledge = [result.get('snippet', '') for result in combined_results]
            sources = [(result.get('title', 'Untitled'), result.get('link', '')) for result in combined_results]
            
            # Log search to history
            self._add_to_history(query, site, len(combined_results))
            
            return web_knowledge, sources
            
        except Exception as e:
            print(f"❌ Error in search: {str(e)}")
            return [], []
    
    def _add_to_history(self, query: str, site: Optional[str], result_count: int):
        """Add search to history log."""
        self.search_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'site': site,
            'result_count': result_count
        })
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Return the search history."""
        return self.search_history
    
    def clear_history(self):
        """Clear search history."""
        self.search_history = []


# ============================================================================
# Summarization Engine Module
# ============================================================================

class SummarizationEngine:
    """
    Handles AI-powered text summarization using OpenAI models.
    Provides flexible summarization with different styles and lengths.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the summarization engine.
        
        Args:
            model (str): OpenAI model to use
            temperature (float): Creativity level (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(temperature=temperature, model=model)
    
    def summarize(
        self, 
        text: str, 
        source: Tuple[str, str], 
        style: str = "bullet",
        max_points: int = 2
    ) -> str:
        """
        Summarize text with specified style.
        
        Args:
            text (str): Text to summarize
            source (Tuple[str, str]): Source title and URL
            style (str): Summary style ('bullet', 'paragraph', 'brief')
            max_points (int): Maximum number of bullet points
            
        Returns:
            str: Formatted summary with source attribution
        """
        try:
            # Select prompt based on style
            if style == "bullet":
                prompt_text = f"Please summarize the following text in {max_points} concise bullet points:\n\n{{text}}\n\nSummary:"
            elif style == "paragraph":
                prompt_text = "Please provide a concise paragraph summary of the following text:\n\n{text}\n\nSummary:"
            elif style == "brief":
                prompt_text = "Please provide a one-sentence summary of the following text:\n\n{text}\n\nSummary:"
            else:
                prompt_text = f"Please summarize the following text in {max_points} bullet points:\n\n{{text}}\n\nSummary:"
            
            # Create prompt template
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=["text"],
            )
            
            # Create chain and invoke
            summary_chain = prompt | self.llm
            input_data = {"text": text}
            summary = summary_chain.invoke(input_data)
            
            # Extract content
            summary_content = summary.content if hasattr(summary, 'content') else str(summary)
            
            # Format with source attribution
            formatted_summary = self._format_summary(summary_content, source)
            
            return formatted_summary
            
        except Exception as e:
            print(f"❌ Error in summarization: {str(e)}")
            return ""
    
    def _format_summary(self, summary: str, source: Tuple[str, str]) -> str:
        """
        Format summary with source information.
        
        Args:
            summary (str): Raw summary text
            source (Tuple[str, str]): Source title and URL
            
        Returns:
            str: Formatted summary with source
        """
        formatted = f"📌 **Source:** {source[0]}\n"
        formatted += f"🔗 **Link:** {source[1]}\n"
        formatted += f"📝 **Summary:**\n{summary.strip()}\n"
        formatted += "-" * 80 + "\n"
        return formatted
    
    def batch_summarize(
        self, 
        texts: List[str], 
        sources: List[Tuple[str, str]], 
        style: str = "bullet",
        max_points: int = 2
    ) -> List[str]:
        """
        Summarize multiple texts in batch.
        
        Args:
            texts (List[str]): List of texts to summarize
            sources (List[Tuple[str, str]]): List of source tuples
            style (str): Summary style
            max_points (int): Maximum bullet points
            
        Returns:
            List[str]: List of formatted summaries
        """
        summaries = []
        for text, source in zip(texts, sources):
            summary = self.summarize(text, source, style, max_points)
            if summary:
                summaries.append(summary)
        return summaries


# ============================================================================
# Search Manager - Main Orchestrator
# ============================================================================

class SearchManager:
    """
    Main orchestrator that combines search and summarization functionality.
    Provides high-level interface for the application.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the search manager.
        
        Args:
            config (Optional[Config]): Configuration object
        """
        self.config = config or Config()
        self.search_engine = SearchEngine()
        self.summarization_engine = SummarizationEngine(
            model=self.config.default_model,
            temperature=self.config.default_temperature
        )
        self.results_cache: Dict[str, Any] = {}
    
    def search_and_summarize(
        self,
        query: str,
        specific_site: Optional[str] = None,
        max_results: int = 3,
        summary_style: str = "bullet",
        max_points: int = 2
    ) -> Dict[str, Any]:
        """
        Perform search and summarization in one operation.
        
        Args:
            query (str): Search query
            specific_site (Optional[str]): Specific website to search
            max_results (int): Maximum results to retrieve
            summary_style (str): Style of summary ('bullet', 'paragraph', 'brief')
            max_points (int): Maximum bullet points
            
        Returns:
            Dict containing summaries, sources, and metadata
        """
        try:
            # Check cache
            cache_key = f"{query}_{specific_site}_{max_results}_{summary_style}"
            if cache_key in self.results_cache:
                print("📦 Loading results from cache...")
                return self.results_cache[cache_key]
            
            # Perform search
            web_knowledge, sources = self.search_engine.search(
                query=query,
                site=specific_site,
                max_results=max_results
            )
            
            if not web_knowledge or not sources:
                return {
                    'success': False,
                    'message': 'No results found',
                    'summaries': [],
                    'sources': [],
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Perform summarization
            print("📝 Generating summaries...")
            summaries = self.summarization_engine.batch_summarize(
                texts=web_knowledge,
                sources=sources,
                style=summary_style,
                max_points=max_points
            )
            
            # Prepare result
            result = {
                'success': True,
                'message': f'Found {len(summaries)} results',
                'summaries': summaries,
                'sources': sources,
                'query': query,
                'specific_site': specific_site,
                'timestamp': datetime.now().isoformat(),
                'summary_style': summary_style
            }
            
            # Cache result
            self.results_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"❌ Error in search_and_summarize: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'summaries': [],
                'sources': [],
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history from search engine."""
        return self.search_engine.get_search_history()
    
    def clear_cache(self):
        """Clear results cache."""
        self.results_cache = {}
        print("🗑️ Cache cleared")
    
    def clear_history(self):
        """Clear search history."""
        self.search_engine.clear_history()
        print("🗑️ History cleared")
    
    def export_results(self, results: Dict[str, Any], format: str = "txt") -> str:
        """
        Export results to specified format.
        
        Args:
            results (Dict[str, Any]): Results dictionary
            format (str): Export format ('txt', 'json', 'md')
            
        Returns:
            str: Formatted export string
        """
        if format == "json":
            return json.dumps(results, indent=2)
        
        elif format == "md":
            output = f"# Search Results: {results.get('query', 'N/A')}\n\n"
            output += f"**Date:** {results.get('timestamp', 'N/A')}\n"
            output += f"**Site:** {results.get('specific_site', 'All websites')}\n\n"
            output += "## Summaries\n\n"
            for summary in results.get('summaries', []):
                output += summary + "\n"
            return output
        
        else:  # txt format
            output = f"Search Results: {results.get('query', 'N/A')}\n"
            output += f"Date: {results.get('timestamp', 'N/A')}\n"
            output += f"Site: {results.get('specific_site', 'All websites')}\n"
            output += "=" * 80 + "\n\n"
            for summary in results.get('summaries', []):
                output += summary + "\n"
            return output


# ============================================================================
# Utility Functions
# ============================================================================

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def format_timestamp(iso_timestamp: str) -> str:
    """
    Format ISO timestamp to readable format.
    
    Args:
        iso_timestamp (str): ISO format timestamp
        
    Returns:
        str: Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return iso_timestamp


# ============================================================================
# Main Execution Guard
# ============================================================================

if __name__ == "__main__":
    """Test the backend functionality."""
    print("🧪 Testing Search & Summarize Backend\n")
    
    try:
        # Initialize
        manager = SearchManager()
        
        # Test search and summarize
        query = "Latest advancements in artificial intelligence"
        print(f"Query: {query}\n")
        
        results = manager.search_and_summarize(
            query=query,
            max_results=3,
            summary_style="bullet",
            max_points=2
        )
        
        if results['success']:
            print("✅ Success!\n")
            for summary in results['summaries']:
                print(summary)
        else:
            print(f"❌ Failed: {results['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
