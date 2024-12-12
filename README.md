# Celebro

**Celebro** is a powerful AI-powered search and query application designed to provide intelligent and accurate responses by combining web search, embedding models, and advanced text generation. It is built using modern frameworks and technologies to ensure scalability, flexibility, and efficiency.

## **Key Features**

1. **User Authentication**

   - Signup with unique username and email checks.
   - Login with JWT-based authentication.

2. **Intelligent Search**

   - Performs web searches using Serper API.
   - Generates AI-enhanced responses using Llama models hosted on Groq.

3. **Query History**

   - Stores user queries and responses for future reference.

4. **Embeddings for Advanced Search**

   - Uses HuggingFace embeddings via Langchain for semantic similarity.
   - Stores embeddings in ChromaDB for fast vector-based retrieval.

5. **Frontend**

   - Developed with TypeScript, React, and TailwindCSS for a seamless user experience.

## **Technologies Used**

### Backend

- **FastAPI**: For building robust REST APIs.
- **Langchain**: For integrating Llama models and HuggingFace embeddings.
- **Groq**: Hosting and managing the Llama-based text generation model.
- **Serper**: For performing web searches.
- **ChromaDB**: For storing vector embeddings.
- **MongoDB**: For storing user information and query history.

### Frontend

- **React**: For building a dynamic and responsive UI.
- **TypeScript**: Ensures type safety in development.
- **TailwindCSS**: For styling with utility-first CSS.

---

## **Setup Instructions**

### Prerequisites

Ensure the following are installed on your system:

- Python 3.10+
- Node.js and npm
- Docker (optional for containerization)
- MongoDB Atlas account

### Backend Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/<username>/Celebro.git
   cd celebro/backend
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the environment variables**:
   Create a `.env` file in the `backend` directory with the following content:

   ```env
   MONGODB_URI=<your-mongodb-uri>
   DATABASE_NAME=<your-database-name>
   GROQ_API_KEY=<your-groq-api-key>
   SERPER_API_KEY=<your-serper-api-key>
   EMBEDDINGMODEL=<huggingface-embedding-model>
   SERPER_SEARCH_URL=<serper-search-url>
   TEXT_GEN_MODEL=<llama-text-generation-model>
   ```

4. **Run the server**:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   Access the API docs at `http://localhost:8000/docs`.

### Frontend Setup

1. **Navigate to the frontend directory**:

   ```bash
   cd celebro/frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env` file in the `frontend` directory with the following content:

   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Run the frontend**:

   ```bash
   npm run dev
   ```

   Access the application at `http://localhost:5173`.

---

## **Folder Structure**

### Backend

```
backend/
├── core/
│   ├── config.py          # Configuration settings
├── models/
│   ├── user.py            # User model
│   ├── query.py           # Query model
├── services/
│   ├── auth_service.py    # Handles authentication
│   ├── search_service.py  # Integrates Serper and AI response generation
│   ├── chat_service.py    # Manages chat functionalities
├── main.py                # Entry point for FastAPI
├── requirements.txt       # Python dependencies
```

### Frontend

```
frontend/
├── src/
│   ├── App.tsx            # Main app file
├── public/
│   ├── index.html         # HTML template
├── package.json           # Frontend dependencies
```

---

## **Future Enhancements**

- **Response Personalization**: Users can choose the tone of the response.
- **Advanced Query Filters**: Allow users to filter queries by date or topic.
- **Model Tuning**: Support for fine-tuning Llama and HuggingFace models.
- **Deployment**: Host on AWS for scalability.

---

## **Contributing**

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Add feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

