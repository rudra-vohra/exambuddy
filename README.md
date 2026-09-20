# The ExamBuddy: Multimodal Course Study Companion

The ExamBuddy is an academic study assistant designed to support students during exam preparation. The system answers questions strictly from course materials uploaded by instructors and students. Every response includes verified page-level citations, allowing learners to inspect the original course context, view rendered PDF pages, and review handwritten derivations.

---

## Key Capabilities

- **Strict Source Grounding**: Every factual statement links directly to an exact document name and page number.
- **Multimodal Document Support**: Processes diverse academic materials including digital PDF lecture notes, slide decks, Markdown summaries, and photographed handwritten pages.
- **Vision-Enabled OCR**: Transcribes handwritten equations, diagrams, and scanned notes using Gemini Vision models and PyMuPDF rendering.
- **Verified Page Previews**: Selecting any citation opens an inspection drawer displaying the cited excerpt, full page text, and a direct visual rendering of the source page.
- **Out-of-Corpus Guardrail**: When a query addresses topics outside the ingested course materials, the assistant issues a standard refusal response to maintain academic integrity.
- **Multi-Document Synthesis**: Answers complex questions that require combining evidence across multiple documents, such as lecture slides and handwritten derivations.
- **Persistent Session State**: Chat history and drafted questions remain available while navigating between tabs during the active study session.

---

## System Architecture

```
                       +-----------------------------+
                       |      Web User Interface     |
                       |    React + Vite + Tailwind  |
                       +--------------+--------------+
                                      |
                                      | HTTP REST API
                                      v
                       +-----------------------------+
                       |       FastAPI Backend       |
                       |    (Asynchronous Service)   |
                       +-------+-------------+-------+
                               |             |
           +-------------------+             +-------------------+
           |                                                     |
           v                                                     v
+-----------------------+                             +-----------------------+
|  Qdrant Vector Store  |                             |   MongoDB Database    |
|   (Port 6333)         |                             |    (Port 27017)       |
| - High-Dim Vectors    |                             | - Document Catalog    |
| - Similarity Search   |                             | - Chat Session Logs   |
| - Chunk Metadata      |                             | - Benchmark History   |
+-----------------------+                             +-----------------------+
           ^                                                     ^
           |                                                     |
+----------+------------+                             +----------+------------+
|  Multimodal Ingestion |                             |   Answer Generator    |
| - PyMuPDF Extraction  |                             | - Gemini LLM          |
| - Gemini Vision OCR   |                             | - Structured Output   |
| - Text Splitter       |                             | - Citation Parser     |
+-----------------------+                             +-----------------------+
```

---

## Technology Stack

### Backend
- **Python 3.11+**: Primary application runtime.
- **FastAPI**: Asynchronous web framework providing REST endpoints.
- **Uvicorn**: High-performance ASGI web server.
- **LangChain**: Document loaders, recursive text chunking, and embedding orchestration.
- **PyMuPDF (`pymupdf`)**: PDF page extraction, text inspection, and high-resolution page rendering.
- **Qdrant Client**: Vector database connectivity and similarity search.
- **Motor**: Asynchronous MongoDB driver for session storage and document cataloging.
- **Google Generative AI**:
  - `gemini-embedding-2`: High-dimensional semantic embeddings.
  - `gemini-3.5-flash-lite`: Multimodal transcription and grounded answer generation.

### Frontend
- **React 19**: User interface library.
- **Vite**: Build tool and local development server.
- **Tailwind CSS**: Utility styling framework.
- **Lucide React**: Clean interface iconography.
- **Outfit & Inter Fonts**: Display typography.

### Infrastructure & Storage
- **Docker Compose**: Container orchestration for database services.
- **Qdrant Vector Database**: Vector storage on port `6333`.
- **MongoDB 7.0**: Document and metadata storage on port `27017`.

---

## Directory Structure

```
itgeeks_rag/
|-- backend/
|   |-- main.py                    # FastAPI entrypoint and lifespan management
|   |-- config.py                  # Pydantic environment configuration
|   |-- schemas.py                 # Request and response data contracts
|   |-- routes/
|   |   |-- chat.py                # Retrieval and question answering route
|   |   |-- documents.py           # Ingestion, catalog, and preview routes
|   |   `-- evaluate.py            # Automated benchmark evaluation routes
|   |-- services/
|   |   |-- database.py            # MongoDB connection and persistence logic
|   |   |-- generator.py           # Grounded response synthesis service
|   |   |-- ingestion.py           # Document chunking and vector indexing service
|   |   |-- parser.py              # Multimodal extraction and OCR transcription
|   |   `-- retriever.py           # Vector search and query caching service
|   |-- tests/                     # Pytest automated test suite
|   `-- evaluation/                # Benchmark dataset and evaluation runner
|-- corpus/                        # Document repository organized by format
|   |-- pdf/                       # Lecture PDFs
|   |-- slides/                    # Slide presentations
|   |-- markdown/                  # Study guides and cheat sheets
|   |-- handwritten/               # Photographed handwritten notes
|   `-- uploads/                   # Dynamically uploaded student documents
|-- frontend/
|   |-- src/
|   |   |-- App.jsx                # Main layout and lifted session state
|   |   |-- index.css              # Global styles and font definitions
|   |   |-- components/
|   |   |   |-- Navbar.jsx         # Header navigation and service status
|   |   |   |-- ChatView.jsx       # Interactive study assistant chat interface
|   |   |   |-- DocumentsView.jsx  # Course material library and uploader
|   |   |   |-- ContextDrawer.jsx  # Provenance inspector and visual page viewer
|   |   |   `-- BenchmarkView.jsx  # Evaluation metrics dashboard
|   |   |-- package.json           # Frontend dependency manifest
|   |   `-- vite.config.js         # Vite bundler configuration
|   `-- index.html                 # HTML entry template
|-- docker-compose.yml      # Container configuration for Qdrant and MongoDB
`-- scripts/                       # Automation scripts for indexing and validation
```

---

## How the Pipeline Works

### 1. Document Ingestion
1. Academic files arrive through the web upload interface or the corpus directory.
2. The parser examines each page. Pages containing digital text undergo direct text extraction.
3. Pages with sparse text, equations, or handwriting trigger the multimodal vision extractor, rendering the page into a high-resolution image and transcribing all content via Gemini Vision.
4. Extracted pages are split into chunks of `1000` characters with `400` character overlap to preserve conceptual continuity across boundaries.
5. Chunks receive metadata including source filename, page number, and OCR indicators.
6. The chunks are converted into vectors using `gemini-embedding-2` and stored in the Qdrant vector collection.
7. Document metadata is registered in MongoDB.

### 2. Retrieval & Query Processing
1. A student submits an academic question in the chat interface.
2. The retriever queries the in-memory cache to resolve repeated or similar queries instantly.
3. For new queries, the retriever embeds the question and conducts similarity search in Qdrant, gathering the top relevant excerpts.
4. The excerpts are assembled into a structured prompt containing document sources, page numbers, and exact excerpts.

### 3. Grounded Synthesis
1. The language model receives the excerpts and the student query with strict academic instructions.
2. The model synthesizes the answer using evidence present in the provided excerpts.
3. All source references are returned in a structured citations array containing the document title, verified page number, and supporting text excerpt.
4. When evidence is absent from the materials, the model returns a standardized refusal message.
5. The backend stores the chat interaction in MongoDB and delivers the response to the user interface.

### 4. Interactive Provenance Inspection
1. The student reads the answer and views the verified citation badges below the message.
2. Clicking any badge opens the Context Drawer on the right side of the screen.
3. The drawer displays the cited sentence, the full page text, and a high-resolution visual rendering of the actual source page.

---

## Setup & Installation

### Prerequisites
- **Python 3.11 or higher**
- **Node.js 18 or higher** with `npm`
- **Docker Desktop** (for Qdrant and MongoDB)
- **Google Gemini API Key**

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/itgeeks_rag.git
cd itgeeks_rag
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_itgeeks
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=itgeeks_rag
OCR_MODEL=gemini-3.5-flash-lite
GENERATION_MODEL=gemini-3.5-flash-lite
EMBEDDING_MODEL=models/gemini-embedding-2
CHUNK_SIZE=1000
CHUNK_OVERLAP=400
MIN_CHARS_THRESHOLD=20
DPI_SCALE=2.0
BATCH_SIZE=20
DELAY_SECONDS=3
TOP_K=6
```

### 3. Start Database Containers
Launch the Qdrant vector database and MongoDB instances using Docker Compose:

```bash
docker compose up -d
```

Verify that both containers are active:
- Qdrant: `http://localhost:6333/dashboard`
- MongoDB: `localhost:27017`

### 4. Setup Python Environment
Create and activate a virtual environment, then install dependencies:

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 5. Setup Frontend
Install Node dependencies:

```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Start the Backend Server
Run the FastAPI application with automatic reload:

```bash
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Interactive documentation is accessible at `http://localhost:8000/docs`.

### Start the Frontend Client
In a separate terminal, launch the Vite development server:

```bash
npm run dev --prefix frontend -- --host 0.0.0.0 --port 5173
```

Open your browser and navigate to `http://localhost:5173`.

---

## Ingesting Course Materials

You can add course materials through two simple approaches:

### Method A: Web Interface Upload
1. Navigate to the **Course Materials** tab in the web application.
2. Click **Select Document (.pdf, .md, .txt, .png, .jpg)**.
3. Choose your file. The system automatically extracts text, runs OCR if handwriting or diagrams are detected, vectorizes the chunks, and adds the document to the library.
4. A confirmation badge appears upon completion and clears automatically.

### Method B: Ingesting Corpus Files via Script
Place your course files into the `corpus/` subdirectories (`pdf/`, `slides/`, `markdown/`, `handwritten/`), then run:

```bash
.\.venv\Scripts\python.exe scripts/index_all.py
```

---

## Testing & Quality Assurance

### Automated Unit Tests
Execute the pytest suite covering parser extraction, vector retrieval, and refusal logic:

```bash
.\.venv\Scripts\pytest.exe -v
```

### Benchmark Evaluation Suite
Run the evaluation runner to measure grounding fidelity, multi-document synthesis, and refusal performance across test questions:

```bash
.\.venv\Scripts\python.exe backend/evaluation/run_eval.py
```

Evaluation metrics are displayed on the **Benchmark Evaluation** tab in the web application, showing accuracy and citation verification statistics.

---

## API Reference Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | `GET` | Health status of Qdrant, MongoDB, and vector counts |
| `/api/chat` | `POST` | Ask a question and receive a grounded answer with citations |
| `/api/chat/history/{session_id}` | `GET` | Retrieve stored session history |
| `/api/documents` | `GET` | List all ingested course documents with page and chunk counts |
| `/api/documents/upload` | `POST` | Upload and vectorize an academic document |
| `/api/documents/page-preview` | `GET` | Retrieve page text and high-resolution rendered image |
| `/api/evaluate/run` | `POST` | Trigger benchmark evaluation across test questions |
| `/api/evaluate/latest` | `GET` | View the most recent evaluation summary and metrics |

---

## Summary of Core Strengths

The ExamBuddy offers reliable exam revision support by combining multimodal parsing, strict grounding, and interactive citation verification. Students retain full control to examine evidence directly on the original document page, ensuring confidence during exam study sessions.
