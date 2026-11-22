# UniAssist AI --- Setup and Run Guide

This guide explains how to set up and run the UniAssist AI backend
locally.

UniAssist AI is a university helpdesk assistant for Zambia University
College of Technology (ZUT). It uses retrieval-augmented generation
(RAG): university information is collected and indexed, relevant
information is retrieved for a question, and Gemini generates a grounded
response.

## 1. Project structure

The backend is expected to have a structure similar to this:

``` text
UniAssist-AI/
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── api/
    │   ├── core/
    │   ├── ingestion/
    │   ├── embeddings/
    │   ├── vectorstore/
    │   ├── rag/
    │   └── schemas/
    ├── scripts/
    ├── storage/
    ├── .env
    └── requirements.txt
```

Your actual project may contain additional files. Keep the existing
folder and module names used by your code.

## 2. Prerequisites

Install:

-   Python 3.10 or a compatible version required by your installed
    packages.
-   Git (optional, if you are cloning the project).
-   A Gemini API key.
-   A terminal such as PowerShell or the VS Code terminal.

Check that Python is installed:

``` powershell
py --version
```

If the `py` command is unavailable, install Python and enable the Python
Launcher during installation.

## 3. Get the project

If the project is already on your computer, open its folder in VS Code.

If you are cloning it from GitHub, run:

``` powershell
git clone YOUR_REPOSITORY_URL
cd UniAssist-AI
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL.

## 4. Open the backend directory

From the project root:

``` powershell
cd backend
```

Run the remaining backend commands from this directory. This is
important because the application imports modules using the `app`
package.

Check that Python can find the application package:

``` powershell
py -c "import app; print('App package found')"
```

If this fails, check that you are inside `backend` and that the relevant
application folders contain `__init__.py` files where your project
expects them.

## 5. Create a virtual environment

Create the environment:

``` powershell
py -m venv .venv
```

Activate it in PowerShell:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

``` cmd
.venv\Scripts\activate.bat
```

When the environment is active, the terminal usually displays `(.venv)`.

## 6. Install dependencies

If the project has a `requirements.txt` file, install its dependencies:

``` powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, create one from the packages
actually imported by your project. The project uses FastAPI, Uvicorn,
Sentence Transformers, ChromaDB, and a Gemini client; package names and
versions should match the imports in your code.

Do not install a second or different Gemini SDK just because its name
looks similar. Check which SDK `generator.py` imports and install the
matching package.

## 7. Configure the Gemini API key

Create a `.env` file in the `backend` directory if your application
loads environment variables from there.

Add your API key using the environment-variable name expected by your
code. For example, if `generator.py` reads `GEMINI_API_KEY`:

``` env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the example value with your own key.

Important:

-   Never commit `.env` to GitHub.
-   Add `.env` to `.gitignore`.
-   Do not place the API key in frontend JavaScript or HTML.
-   If your code uses a different variable name, use that exact name
    instead.

## 8. Prepare the university knowledge base

UniAssist AI needs its knowledge base before it can answer questions
reliably.

The ingestion workflow collects and processes university information,
including website pages and PDF content, then creates chunks,
embeddings, and a ChromaDB collection.

If the source data has not yet been collected, run the ingestion scripts
in the order defined by your project. Use the actual script names in
your `scripts` directory.

The general workflow is:

1.  Crawl or collect the approved ZUT website pages.
2.  Extract text from PDFs and other supported sources.
3.  Clean and normalize the extracted text.
4.  Split the text into chunks.
5.  Generate embeddings with the configured Sentence Transformers model.
6.  Store the chunks and embeddings in the persistent ChromaDB
    collection.

Do not delete the existing `storage` directory or reset the ChromaDB
collection unless you intentionally want to rebuild the knowledge base.

If the knowledge base has already been created and the stored collection
is available, you can skip ingestion and proceed to testing.

## 9. Test retrieval

Run the RAG test from the `backend` directory:

``` powershell
py -m scripts.test_rag
```

Run scripts as Python modules (`py -m ...`) from the backend directory.
Avoid running a package script directly by file path if it causes
imports such as `app` to fail.

Check that the test:

-   Finds relevant ZUT information.
-   Returns useful chunks for the question.
-   Does not return unrelated information as the top result.
-   Can retrieve information from the application form and relevant
    website pages.

## 10. Start the FastAPI server

From the `backend` directory, run:

``` powershell
py -m uvicorn app.main:app --reload
```

The local API should be available at:

``` text
http://127.0.0.1:8000
```

Open the interactive API documentation at:

``` text
http://127.0.0.1:8000/docs
```

Keep this terminal open while using the frontend. Stop the server with
`Ctrl+C`.

## 11. Connect the frontend

The current frontend is plain HTML, CSS, and JavaScript.

In `chatbot.js`, the API URL is configured as:

``` javascript
const API_URL = "http://127.0.0.1:8000/api/chat";
```

Make sure:

-   The FastAPI server is running.
-   The frontend sends a `POST` request to `/api/chat`.
-   The request body contains a JSON `question` field.
-   The frontend reads and displays `data.answer`.
-   FastAPI CORS settings allow the origin from which the frontend is
    served.

If the frontend is opened directly as a local file and requests are
blocked by browser restrictions, serve the frontend using a local
development server instead. Keep the API URL pointed at the FastAPI
backend.

## 12. Ask a test question

Try a question whose answer is present in the indexed ZUT information,
for example:

``` text
Where is ZUT located?
```

Then try:

``` text
What undergraduate degree programmes does ZUT offer?
```

Check the answer for accuracy. During development, inspect the backend
response and logs to verify retrieval and source selection. The
student-facing interface should display the answer naturally rather than
exposing internal retrieval details.

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

You are probably running the command from the wrong directory.

Move into `backend`:

``` powershell
cd backend
```

Then run the script as a module:

``` powershell
py -m scripts.test_rag
```

### Gemini API errors

Check that:

-   The API key is valid.
-   The `.env` file is in the location loaded by the application.
-   The environment-variable name matches the one used in
    `generator.py`.
-   The required Gemini SDK is installed.
-   The model name configured in the generator is available to your API
    key.

### ChromaDB collection is empty

Check that ingestion completed successfully and that the application is
using the same persistent storage path when indexing and querying.

Do not create a new collection name in one part of the application while
the retriever queries a different collection.

### Frontend cannot reach the backend

Check that Uvicorn is running at `127.0.0.1:8000`, that `API_URL` is
correct, and that CORS allows the frontend origin.

### Port 8000 is already in use

Run the backend on another port:

``` powershell
py -m uvicorn app.main:app --reload --port 8001
```

If you do this, update the frontend `API_URL` to use port `8001`.

## 14. Normal daily startup

Once the environment and knowledge base are ready, the usual workflow
is:

**Terminal 1 --- Backend**

this was used when there was some error
#py -m uvicorn app.main:app --host 127.0.0.1 --port 8765
py -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --log-level info
uvicorn app.main:app --reload

``` powershell
cd path\to\UniAssist-AI\backend
.\.venv\Scripts\Activate.ps1
py -m uvicorn app.main:app --reload
```

**Frontend**

Open the frontend through your local development server, then use the
chat launcher to ask ZUT-related questions.

You do not need to rebuild the knowledge base every time you start the
server. Re-run ingestion only when you add or update source information.

## 15. Before sharing or deploying

-   Keep API keys and `.env` files private.
-   Keep generated vector-store data out of Git if it is large or
    environment-specific.
-   Configure production CORS with the actual frontend domain rather
    than allowing every origin.
-   Use a production server configuration instead of relying on
    `--reload`.
-   Make sure the deployed backend has access to its persistent
    vector-store data, or rebuild the collection during deployment.
-   Review answers against official university information before making
    the assistant publicly available.
