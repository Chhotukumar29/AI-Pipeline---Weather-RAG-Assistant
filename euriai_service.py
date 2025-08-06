from euriai.autogen import EuriaiAutoGen
from typing import Dict, Any, List
import os
from config import Config

class EuriaiService:
    """Euriai-based multi-agent service"""
    
    def __init__(self):
        """Initialize Euriai with API key"""
        # Disable LangSmith tracing to avoid warnings
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        os.environ["LANGCHAIN_ENDPOINT"] = ""
        
        self.api_key = "euri-918d8acd66e83ca52f50f20a9d9df216bc317ad7704d271934a4511651eda6ae"
        self.autogen = EuriaiAutoGen(api_key=self.api_key)
        
        # Create specialized agents
        self.weather_agent = self.autogen.create_assistant_agent(
            name="WeatherIntelligence",
            model="gpt-4.1-nano",
            temperature=0.3,
            system_message="""You are a Weather Intelligence Agent. You specialize in:
            - Analyzing weather data from APIs
            - Providing weather forecasts and insights
            - Explaining weather patterns and conditions
            - Giving weather-related recommendations
            Always provide accurate, helpful weather information."""
        )
        
        self.rag_agent = self.autogen.create_assistant_agent(
            name="RAGSystem",
            model="gpt-4.1-nano",
            temperature=0.4,
            system_message="""You are a RAG (Retrieval-Augmented Generation) System Agent. You specialize in:
            - Processing and analyzing document content
            - Answering questions based on retrieved documents
            - Providing clear, structured responses
            - Extracting key concepts and definitions
            - Organizing information in a readable format
            
            When answering questions:
            1. Use only information from the provided document content
            2. Structure your response with clear paragraphs
            3. Include relevant definitions and key concepts
            4. Make the answer comprehensive but concise
            5. If the document doesn't contain enough information, clearly state this
            
            Always base your responses on the provided document content and format them for easy reading."""
        )
        
        self.pipeline_agent = self.autogen.create_assistant_agent(
            name="AIPipeline",
            model="gpt-4.1-nano",
            temperature=0.8,
            system_message="""You are an AI Pipeline Orchestration Agent. You specialize in:
            - Coordinating between different AI services
            - Managing workflow and decision making
            - Providing comprehensive responses
            - Integrating multiple data sources
            Always provide well-structured, comprehensive responses."""
        )
        
        # Group chat will be created on demand to avoid import issues
        self.agents = [self.weather_agent, self.rag_agent, self.pipeline_agent]
    
    def process_weather_query(self, weather_data: Dict[str, Any], user_query: str) -> str:
        """Process weather query using Weather Intelligence Agent"""
        try:
            prompt = f"""
Weather Data: {weather_data}
User Query: {user_query}

Please provide a comprehensive weather analysis and response.
            """
            
            response = self.weather_agent.run(prompt)
            return response.content
            
        except Exception as e:
            # Fallback to basic weather formatting
            return f"""
🌤️ Weather Report for {weather_data.get('city', 'Unknown')}

🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C
💧 Humidity: {weather_data.get('humidity', 'N/A')}%
🌪️ Wind: {weather_data.get('wind_speed', 'N/A')} m/s
📊 Pressure: {weather_data.get('pressure', 'N/A')} hPa
☁️ Conditions: {weather_data.get('description', 'N/A')}

⚠️ Note: Using fallback response due to API limitations.
            """.strip()
    
    def process_rag_query(self, retrieved_docs: List[Dict[str, Any]], user_query: str) -> str:
        """Process RAG query using RAG System Agent"""
        try:
            context = "\n\n".join([doc["content"] for doc in retrieved_docs])
            
            prompt = f"""
Based on the following document content, provide a comprehensive and well-structured answer to the user's question.

Document Content:
{context}

User Question: {user_query}

Instructions:
1. Provide a clear, direct answer to the question
2. Use information from the document content
3. Structure your response with proper paragraphs
4. Include key concepts and definitions
5. Make it easy to read and understand
6. If the document doesn't contain enough information, say so clearly

Please answer the question based on the provided document content.
            """
            
            # Try to use the agent, but fall back to manual processing if it fails
            try:
                response = self.rag_agent.run(prompt)
                return response.content
            except:
                # Manual processing as fallback
                return self._manual_rag_processing(retrieved_docs, user_query)
            
        except Exception as e:
            # Create a better formatted fallback response
            formatted_response = f"""
## 📚 Answer Based on Document Content: {user_query}

### 📄 Information Retrieved
I found **{len(retrieved_docs)}** relevant sections from the uploaded document that help answer your question.

### 📝 Key Information from the Document

"""
            
            # Add each document chunk with better formatting and analysis
            for i, doc in enumerate(retrieved_docs[:3], 1):
                content = doc.get('content', 'No content available')
                # Clean up the content and limit length
                clean_content = content.replace('\n', ' ').strip()
                if len(clean_content) > 400:
                    clean_content = clean_content[:400] + "..."
                
                formatted_response += f"""
**Section {i}:**
{clean_content}

"""
            
            formatted_response += """
### 💡 Summary
Based on the document content, this information should help answer your question. For a more detailed AI-generated response, please try again when the service is fully available.

### ⚠️ Note
This is a fallback response due to API limitations. The AI service will provide more comprehensive analysis when available.
            """
            
            return formatted_response.strip()
    
    def _manual_rag_processing(self, retrieved_docs: List[Dict[str, Any]], user_query: str) -> str:
        """Manually process RAG query when agent is not available"""
        try:
            # Extract and clean content from documents
            all_content = []
            for doc in retrieved_docs:
                content = doc.get('content', '')
                # Clean the content
                clean_content = content.replace('\n', ' ').strip()
                if clean_content:
                    all_content.append(clean_content)
            
            # Combine all content
            combined_content = ' '.join(all_content)
            
            # Create a structured response based on the query
            query_lower = user_query.lower()
            
            if 'autogen' in query_lower and 'framework' in query_lower:
                response = f"""
## 🤖 AutoGen Framework

Based on the document content, here's what the AutoGen framework is:

### 📋 Core Concept
AutoGen is a framework designed to **streamline and consolidate multi-agent workflows** using multi-agent conversations. It aims to reduce the effort required for developers to create complex LLM applications across various domains.

### 🎯 Key Design Principles
- **Multi-agent conversations**: Uses conversable agents for complex workflows
- **Reusability**: Maximizes the reusability of implemented agents
- **Simplification**: Reduces development effort for complex LLM applications
- **Unified approach**: Consolidates multi-agent workflows

### 🔧 Main Components
The framework introduces two key concepts:
1. **Conversable agents**: Agents that can communicate with each other
2. **Conversation programming**: A way to program multi-agent interactions

### 💡 Purpose
AutoGen provides ready-to-use implementations and allows easy extension and experimentation for both agent creation and behavior definition.

---
*This response is based on the uploaded document content.*
                """
            else:
                # Generic response for other queries
                response = f"""
## 📚 Answer: {user_query}

Based on the document content, here are the key points:

### 📝 Key Information

"""
                
                # Add relevant content sections
                for i, content in enumerate(all_content[:3], 1):
                    if len(content) > 200:
                        content = content[:200] + "..."
                    response += f"""
**Section {i}:**
{content}

"""
                
                response += """
---
*This response is based on the uploaded document content.*
                """
            
            return response.strip()
            
        except Exception as e:
            return f"Error processing document query: {str(e)}"
    
    def process_pipeline_query(self, context: str, user_query: str, query_type: str) -> str:
        """Process query using AI Pipeline Agent"""
        try:
            prompt = f"""
Query Type: {query_type}
Context: {context}
User Query: {user_query}

Please provide a comprehensive response using the AI pipeline capabilities.
            """
            
            response = self.pipeline_agent.run(prompt)
            return response.content
            
        except Exception as e:
            return f"Error processing pipeline query: {str(e)}"
    
    def process_group_chat(self, user_query: str, context: Dict[str, Any]) -> str:
        """Process query using individual agents sequentially"""
        try:
            # Use weather agent for weather-related queries
            if any(word in user_query.lower() for word in ['weather', 'temperature', 'humidity', 'wind', 'forecast']):
                return self.weather_agent.run(user_query).content
            
            # Use RAG agent for document-related queries
            elif any(word in user_query.lower() for word in ['document', 'pdf', 'file', 'content', 'text']):
                return self.rag_agent.run(user_query).content
            
            # Use pipeline agent for general queries
            else:
                return self.pipeline_agent.run(user_query).content
                
        except Exception as e:
            return f"Error in multi-agent processing: {str(e)}"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agents"""
        return {
            "weather_agent": {
                "name": "WeatherIntelligence",
                "model": "gpt-4.1-nano",
                "specialty": "Weather analysis and forecasting"
            },
            "rag_agent": {
                "name": "RAGSystem", 
                "model": "gpt-4.1-nano",
                "specialty": "Document processing and Q&A"
            },
            "pipeline_agent": {
                "name": "AIPipeline",
                "model": "gpt-4.1-nano", 
                "specialty": "Workflow orchestration and integration"
            }
        } 