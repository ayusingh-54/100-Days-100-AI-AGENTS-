# Customer Support Agent with LangGraph

An intelligent customer support agent built using LangGraph, LangChain, and Streamlit. This application categorizes customer queries, analyzes sentiment, and provides appropriate responses or escalates issues when necessary.

## 🌟 Features

- **Query Categorization**: Automatically categorizes queries into Technical, Billing, or General
- **Sentiment Analysis**: Analyzes the emotional tone of customer queries (Positive, Neutral, Negative)
- **Intelligent Routing**: Routes queries to appropriate handlers based on category and sentiment
- **Automatic Escalation**: Escalates queries with negative sentiment to human agents
- **Interactive Web Interface**: User-friendly Streamlit interface
- **Query History**: Tracks and displays previous queries and responses
- **Workflow Visualization**: Visual representation of the LangGraph workflow

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key

## 🚀 Installation

1. Clone or download this repository

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

4. Add your OpenAI API key to the `.env` file:

```
OPENAI_API_KEY=your_actual_api_key_here
```

## 💻 Usage

### Running the Streamlit App

To launch the interactive web interface:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Using the Backend Directly

You can also use the backend module directly in your Python code:

```python
from backend import CustomerSupportAgent

# Initialize the agent
agent = CustomerSupportAgent(temperature=0)

# Process a query
result = agent.process_query("My internet connection keeps dropping. Can you help?")

print(f"Category: {result['category']}")
print(f"Sentiment: {result['sentiment']}")
print(f"Response: {result['response']}")
```

## 📁 Project Structure

```
customer_support_agent_langgraph/
│
├── customer_support_agent_langgraph.ipynb  # Original notebook
├── backend.py                               # Core agent logic (modular)
├── app.py                                   # Streamlit application
├── .env.example                             # Example environment variables
├── .env                                     # Your environment variables (create this)
└── README.md                                # This file
```

## 🎯 How It Works

1. **Query Input**: User submits a customer support query
2. **Categorization**: The agent categorizes the query into Technical, Billing, or General
3. **Sentiment Analysis**: The agent analyzes the emotional tone of the query
4. **Routing**: Based on sentiment and category:
   - Negative sentiment → Escalate to human agent
   - Technical category → Generate technical support response
   - Billing category → Generate billing support response
   - General category → Generate general support response
5. **Response**: The appropriate response is returned to the user

## 🔧 Configuration

### Temperature Setting

The temperature parameter controls the randomness of the model's responses:

- `0.0`: More focused and deterministic responses
- `1.0`: More creative and random responses

You can adjust this in the Streamlit sidebar or when initializing the `CustomerSupportAgent` class.

## 📊 Example Queries

### Technical Support

```
"My internet connection keeps dropping. Can you help?"
```

### Billing Support

```
"Where can I find my receipt?"
```

### General Support

```
"What are your business hours?"
```

### Escalation (Negative Sentiment)

```
"I'm very frustrated with your terrible service!"
```

## 🛠️ Customization

### Adding New Categories

To add new query categories, modify the `categorize` method in `backend.py`:

```python
def categorize(self, state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into one of these categories: "
        "Technical, Billing, General, Sales, Returns. Query: {query}"
    )
    # ... rest of the code
```

### Adding New Handlers

1. Add a new handler method to the `CustomerSupportAgent` class
2. Add the node to the workflow in `_build_workflow`
3. Update the `route_query` method to include routing logic
4. Add appropriate edges in the workflow

## 📝 Notes

- Ensure your OpenAI API key has sufficient credits
- The application requires an internet connection to access the OpenAI API
- Query processing time depends on OpenAI API response time

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements.

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [LangChain](https://github.com/langchain-ai/langchain)
- UI created with [Streamlit](https://streamlit.io/)
- Language model by [OpenAI](https://openai.com/)
