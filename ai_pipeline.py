from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict
import re
from weather_service import WeatherService
from vector_store import VectorStore
from euriai_service import EuriaiService
from pdf_processor import PDFProcessor
from evaluation_service import EvaluationService

# Define state structure
class AgentState(TypedDict):
    user_query: str
    query_type: str
    weather_data: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    response: str
    evaluation: Dict[str, Any]

class AIPipeline:
    """Main AI pipeline using LangGraph"""
    
    def __init__(self):
        """Initialize the AI pipeline components"""
        self.weather_service = WeatherService()
        self.vector_store = VectorStore()
        self.euriai_service = EuriaiService()
        self.pdf_processor = PDFProcessor()
        self.evaluation_service = EvaluationService()
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("get_weather", self._get_weather)
        workflow.add_node("get_rag_response", self._get_rag_response)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("evaluate_response", self._evaluate_response)
        
        # Set entry point
        workflow.set_entry_point("classify_query")
        
        # Add conditional edges from classify_query
        workflow.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "weather": "get_weather",
                "rag": "get_rag_response"
            }
        )
        
        # Add edges from weather and rag nodes to generate_response
        workflow.add_edge("get_weather", "generate_response")
        workflow.add_edge("get_rag_response", "generate_response")
        
        # Add edge from generate_response to evaluate_response
        workflow.add_edge("generate_response", "evaluate_response")
        
        # Add edge from evaluate_response to END
        workflow.add_edge("evaluate_response", END)
        
        return workflow.compile()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify the type of query"""
        query = state["user_query"].lower()
        
        # Weather-related keywords
        weather_keywords = [
            "weather", "temperature", "forecast", "humidity", "wind", 
            "rain", "snow", "sunny", "cloudy", "hot", "cold", "degrees",
            "celsius", "fahrenheit", "precipitation", "atmosphere", "aqi",
            "air quality", "pollution", "air quality index"
        ]
        
        # Check if query contains weather keywords
        is_weather_query = any(keyword in query for keyword in weather_keywords)
        
        if is_weather_query:
            state["query_type"] = "weather"
        else:
            state["query_type"] = "rag"
        
        return state
    
    def _route_query(self, state: AgentState) -> str:
        """Route query to appropriate node"""
        return state["query_type"]
    
    def _get_weather(self, state: AgentState) -> AgentState:
        """Get weather data for the query"""
        try:
            query = state["user_query"].lower()
            
            # Check if it's an AQI query
            is_aqi_query = any(keyword in query for keyword in ["aqi", "air quality", "pollution", "air quality index"])
            
            # Extract city name from query
            city = self._extract_city_from_query(state["user_query"])
            
            if city:
                if is_aqi_query:
                    # Get AQI information
                    aqi_data = self.weather_service.get_aqi_info(city)
                    state["weather_data"] = aqi_data
                else:
                    # Get regular weather data
                    weather_data = self.weather_service.get_weather_by_city(city)
                    state["weather_data"] = weather_data
            else:
                # Default to Delhi for Indian queries, London for others
                if any(indian_city in query for indian_city in self.weather_service.get_indian_cities_list()):
                    default_city = "delhi"
                else:
                    default_city = "London"
                
                if is_aqi_query:
                    aqi_data = self.weather_service.get_aqi_info(default_city)
                    state["weather_data"] = aqi_data
                else:
                    weather_data = self.weather_service.get_weather_by_city(default_city)
                    state["weather_data"] = weather_data
                
        except Exception as e:
            state["weather_data"] = {"error": str(e)}
        
        return state
    
    def _get_rag_response(self, state: AgentState) -> AgentState:
        """Get RAG response from vector store"""
        try:
            query = state["user_query"]
            
            # Search for relevant documents
            retrieved_docs = self.vector_store.search(query, top_k=3)
            state["retrieved_docs"] = retrieved_docs
            
        except Exception as e:
            state["retrieved_docs"] = [{"content": f"Error retrieving documents: {str(e)}"}]
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response based on query type"""
        try:
            query = state["user_query"]
            query_type = state["query_type"]
            
            if query_type == "weather":
                weather_data = state["weather_data"]
                if "error" in weather_data:
                    response = f"Sorry, I couldn't get weather information: {weather_data['error']}"
                else:
                    response = self.euriai_service.process_weather_query(weather_data, query)
            
            elif query_type == "rag":
                retrieved_docs = state["retrieved_docs"]
                if not retrieved_docs or "error" in retrieved_docs[0]:
                    response = "I don't have enough information in my knowledge base to answer this question. Please upload a PDF document first."
                else:
                    response = self.euriai_service.process_rag_query(retrieved_docs, query)
            
            else:
                response = "I'm not sure how to handle this type of query."
            
            state["response"] = response
            
        except Exception as e:
            state["response"] = f"Error generating response: {str(e)}"
        
        return state
    
    def _evaluate_response(self, state: AgentState) -> AgentState:
        """Evaluate the response quality"""
        try:
            query = state["user_query"]
            response = state["response"]
            query_type = state["query_type"]
            
            evaluation = self.evaluation_service.evaluate_response(query, response, query_type)
            state["evaluation"] = evaluation
            
        except Exception as e:
            state["evaluation"] = {"error": f"Error evaluating response: {str(e)}"}
        
        return state
    
    def _extract_city_from_query(self, query: str) -> str:
        """Extract city name from weather query"""
        # Simple city extraction - can be improved with NLP
        query_lower = query.lower()
        
        # Common cities (including Indian cities)
        cities = [
            "london", "new york", "tokyo", "paris", "berlin", "moscow",
            "beijing", "sydney", "toronto", "vancouver", "san francisco", 
            "los angeles", "chicago", "miami", "boston", "seattle", "denver", 
            "phoenix", "dallas", "houston", "atlanta",
            # Indian cities
            "delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad",
            "pune", "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur",
            "indore", "thane", "bhopal", "visakhapatnam", "patna", "vadodara",
            "ghaziabad", "ludhiana"
        ]
        
        for city in cities:
            if city in query_lower:
                return city.title()
        
        # Try to extract city using regex patterns
        patterns = [
            r"weather in (\w+)",
            r"temperature in (\w+)",
            r"forecast for (\w+)",
            r"(\w+) weather",
            r"(\w+) temperature"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).title()
        
        return ""
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query through the pipeline"""
        try:
            # Initialize state
            initial_state = AgentState(
                user_query=user_query,
                query_type="",
                weather_data={},
                retrieved_docs=[],
                response="",
                evaluation={}
            )
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            return {
                "query": result["user_query"],
                "query_type": result["query_type"],
                "response": result["response"],
                "evaluation": result["evaluation"],
                "weather_data": result.get("weather_data", {}),
                "retrieved_docs": result.get("retrieved_docs", [])
            }
            
        except Exception as e:
            return {
                "error": f"Pipeline error: {str(e)}",
                "query": user_query,
                "response": "Sorry, I encountered an error processing your request."
            }
    
    def upload_pdf(self, pdf_file, source_name: str = "uploaded_pdf") -> Dict[str, Any]:
        """Upload and process a PDF document"""
        try:
            # Process PDF
            documents = self.pdf_processor.process_pdf_for_rag(pdf_file, source_name)
            
            # Add to vector store
            doc_ids = self.vector_store.add_documents(documents)
            
            # Get PDF info
            pdf_info = self.pdf_processor.get_pdf_info(pdf_file)
            
            return {
                "success": True,
                "documents_processed": len(documents),
                "documents_stored": len(doc_ids),
                "pdf_info": pdf_info,
                "source_name": source_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        return self.vector_store.get_collection_info() 