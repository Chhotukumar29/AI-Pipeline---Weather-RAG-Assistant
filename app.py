import streamlit as st
import os
from ai_pipeline import AIPipeline
from config import Config
import json

# Page configuration
st.set_page_config(
    page_title="AI Pipeline - Weather & RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "vector_store_info" not in st.session_state:
    st.session_state.vector_store_info = {}

def initialize_pipeline():
    """Initialize the AI pipeline"""
    try:
        Config.validate_config()
        pipeline = AIPipeline()
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize pipeline: {str(e)}")
        return None

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🤖 AI Pipeline - Weather & RAG Assistant")
    st.markdown("""
    This application demonstrates an AI pipeline using LangChain, LangGraph, and LangSmith.
    It can answer weather queries and questions from uploaded PDF documents.
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check if pipeline is initialized
        if st.session_state.pipeline is None:
            if st.button("Initialize Pipeline"):
                with st.spinner("Initializing AI Pipeline..."):
                    st.session_state.pipeline = initialize_pipeline()
                    if st.session_state.pipeline:
                        st.success("Pipeline initialized successfully!")
                        st.session_state.vector_store_info = st.session_state.pipeline.get_vector_store_info()
                    else:
                        st.error("Failed to initialize pipeline. Check your API keys.")
        
        # Show pipeline status
        if st.session_state.pipeline:
            st.success("✅ Pipeline Ready")
            
            # Vector store info
            st.subheader("📚 Vector Store Info")
            if st.session_state.vector_store_info:
                info = st.session_state.vector_store_info
                if "error" not in info:
                    pass
                    #st.write(f"Documents: {info.get('points_count', 0)}")
                    #st.write(f"Collection: {info.get('name', 'N/A')}")
                else:
                    st.warning("Vector store not accessible")
            
            # PDF upload section
            st.subheader("📄 Upload PDF")
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload a PDF document to enable RAG functionality"
            )
            
            if uploaded_file is not None:
                if st.button("Process PDF"):
                    with st.spinner("Processing PDF..."):
                        result = st.session_state.pipeline.upload_pdf(uploaded_file)
                        if result["success"]:
                            st.success(f"✅ PDF processed successfully!")
                            st.write(f"Documents stored: {result['documents_processed']}")
                            st.session_state.vector_store_info = st.session_state.pipeline.get_vector_store_info()
                        else:
                            st.error(f"❌ Error processing PDF: {result['error']}")
        else:
            st.warning("⚠️ Pipeline not initialized")
            st.markdown("""
            **Required API Keys:**
            - OPENAI_API_KEY
            - OPENWEATHER_API_KEY  
            - LANGSMITH_API_KEY
            - QDRANT_URL
            - QDRANT_API_KEY
            
            Please set these in your `.env` file.
            """)
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show additional info for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                with st.expander("🔍 Response Details"):
                    metadata = message["metadata"]
                    st.write(f"**Query Type:** {metadata.get('query_type', 'N/A')}")
                    
                    if metadata.get('weather_data'):
                        st.write("**Weather Data:**")
                        st.json(metadata['weather_data'])
                    
                    if metadata.get('evaluation'):
                        st.write("**Response Evaluation:**")
                        st.write(metadata['evaluation'].get('evaluation', 'N/A'))
    
    # Chat input
    if prompt := st.chat_input("Ask me about weather or upload a PDF and ask questions about it..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Processing your query..."):
                if st.session_state.pipeline:
                    result = st.session_state.pipeline.process_query(prompt)
                    
                    if "error" in result:
                        response = result["response"]
                        st.error(f"Pipeline Error: {result['error']}")
                    else:
                        response = result["response"]
                        
                        # Show response details in expander
                        with st.expander("🔍 Response Details"):
                            st.markdown("### 📊 Response Analysis")
                            
                            # Query Type
                            query_type = result.get('query_type', 'N/A')
                            st.write(f"**🔍 Query Type:** {query_type}")
                            
                            if query_type == "weather":
                                st.info("🌤️ This was processed by Weather Intelligence Agent (GPT-4.1 Nano)")
                            elif query_type == "rag":
                                st.info("📚 This was processed by RAG System Agent (GPT-4.1 Nano)")
                            
                            # Show agent information
                            st.markdown("### 🤖 Multi-Agent System")
                            st.write("**Active Agents:**")
                            st.write("• **WeatherIntelligence**: GPT-4.1 Nano")
                            st.write("• **RAGSystem**: GPT-4.1 Nano") 
                            st.write("• **AIPipeline**: GPT-4.1 Nano")
                            
                            # Weather Data (if available)
                            if result.get('weather_data'):
                                st.markdown("### 🌤️ Weather Data Retrieved")
                                weather_data = result['weather_data']
                                if 'error' not in weather_data:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Temperature", f"{weather_data.get('temperature', 'N/A')}°C")
                                        st.metric("Humidity", f"{weather_data.get('humidity', 'N/A')}%")
                                    with col2:
                                        st.metric("Wind Speed", f"{weather_data.get('wind_speed', 'N/A')} m/s")
                                        st.metric("Pressure", f"{weather_data.get('pressure', 'N/A')} hPa")
                                    
                                    st.json(weather_data)
                                else:
                                    st.error(f"Weather data error: {weather_data['error']}")
                            
                            # Retrieved Documents (if available)
                            if result.get('retrieved_docs'):
                                st.markdown("### 📚 Retrieved Documents")
                                docs = result['retrieved_docs']
                                st.write(f"**Found {len(docs)} relevant document chunks:**")
                                for i, doc in enumerate(docs[:3]):  # Show first 3 docs
                                    st.write(f"**Document {i+1}** (Score: {doc.get('score', 'N/A'):.3f})")
                                    st.text_area(f"Content {i+1}", doc.get('content', 'No content'), height=100, key=f"doc_{i}")
                                    st.markdown("---")
                            
                            # Response Evaluation (if available)
                            if result.get('evaluation'):
                                st.markdown("### 📈 Response Evaluation")
                                evaluation = result['evaluation']
                                if 'error' not in evaluation:
                                    # Display evaluation scores
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Accuracy", f"{evaluation.get('accuracy', 'N/A')}/5")
                                    with col2:
                                        st.metric("Relevance", f"{evaluation.get('relevance', 'N/A')}/5")
                                    with col3:
                                        st.metric("Completeness", f"{evaluation.get('completeness', 'N/A')}/5")
                                    with col4:
                                        st.metric("Clarity", f"{evaluation.get('clarity', 'N/A')}/5")
                                    
                                    # Overall score
                                    overall_score = evaluation.get('overall_score', 0)
                                    st.metric("Overall Score", f"{overall_score:.1f}/5")
                                    
                                    # Feedback
                                    if evaluation.get('feedback'):
                                        st.write("**Feedback:**")
                                        for feedback in evaluation['feedback']:
                                            st.write(f"• {feedback}")
                                else:
                                    st.warning("Evaluation not available")
                            
                            # Pipeline Information
                            st.markdown("### 🤖 Pipeline Information")
                            st.write(f"**Processing Time:** Real-time")
                            st.write(f"**Model Used:** GPT-4.1 Nano")
                            st.write(f"**Vector Store:** Qdrant Database")
                    
                    st.markdown(response)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "metadata": {
                            "query_type": result.get("query_type"),
                            "weather_data": result.get("weather_data"),
                            "evaluation": result.get("evaluation")
                        }
                    })
                else:
                    response = "Please initialize the pipeline first using the sidebar."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Footer with Project Features button
    st.markdown("---")
    
    # Project Features section
    if st.button("📋 Project Features", help="Click to view all project features"):
        st.markdown("""
        ## 🚀 AI Pipeline Features
        
        ### 🌤️ Weather Intelligence
        - **Real-time Weather Data**: Fetch current weather from OpenWeatherMap API
        - **City Recognition**: Automatic city extraction from natural language queries
        - **Comprehensive Data**: Temperature, humidity, wind, pressure, visibility
        - **Formatted Responses**: User-friendly weather reports with emojis
        
        ### 📚 Document Intelligence (RAG)
        - **PDF Processing**: Upload and extract text from PDF documents
        - **Smart Chunking**: Intelligent text segmentation with overlap
        - **Vector Embeddings**: Store document chunks in Qdrant vector database
        - **Semantic Search**: Find relevant information using similarity search
        - **Context-Aware Responses**: Answer questions based on document content
        
        ### 🤖 AI Pipeline Architecture
        - **LangGraph Decision Making**: Intelligent routing between weather and RAG
        - **State Management**: Maintains conversation context and query history
        - **Modular Design**: Clean, testable, and extensible code structure
        - **Error Handling**: Graceful error recovery and user feedback
        
        ### 📊 Quality Assurance
        - **LangSmith Integration**: Automatic response quality evaluation
        - **Performance Metrics**: Track accuracy, relevance, completeness, clarity
        - **Response Evaluation**: Rate responses from 1-5 on multiple criteria
        - **Continuous Monitoring**: Real-time quality assessment
        
        ### 🗄️ Data Management
        - **Qdrant Vector Database**: High-performance vector storage
        - **Document Persistence**: Store and retrieve document embeddings
        - **Metadata Tracking**: Source, chunk size, and processing information
        - **Scalable Architecture**: Handle multiple documents and queries
        
        ### 🛠️ Technical Stack
        - **LangChain**: LLM orchestration and prompt management
        - **LangGraph**: Stateful workflow and decision routing
        - **Google Gemini**: Advanced language model for responses
        - **Streamlit**: Modern, responsive web interface
        - **Qdrant**: Vector similarity search and storage
        """)
    
    # Quick features summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🌤️ **Weather Intelligence**")
    with col2:
        st.markdown("📚 **RAG System**")
    with col3:
        st.markdown("🤖 **AI Pipeline**")

if __name__ == "__main__":
    main() 