import os
import boto3
import tempfile
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from app.models.document import Document  # Assuming this is your ORM model

# Load environment variables from .env file
load_dotenv()

# Fetch the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("AI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Ensure your .env file has the AI_API_KEY set.")
else:
    print(f"Loaded OpenAI API key: {OPENAI_API_KEY[:4]}...")  # Hides most of the key for security

class NLPService:

    @staticmethod
    def index_documents(db: Session):
        print("Starting the document indexing process...")

        # Retrieve all documents from the database
        documents = db.query(Document).all()
        print(f"Retrieved {len(documents)} documents from the database.")

        # Initialize S3 client
        s3_client = boto3.client('s3')
        bucket_name = 'aiplanet7'

        all_chunks = []

        # Load each document's content from S3
        for doc in documents:
            print(f"Processing document: {doc.title}")
            file_key_found = False

            try:
                # List all objects in the S3 bucket to find the matching key
                response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in response:
                    for item in response['Contents']:
                        if item['Key'].endswith(doc.title):
                            file_key = item['Key']
                            file_key_found = True
                            break

                if file_key_found:
                    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                    file_content = response['Body'].read()
                    print(f"Loaded content for: {doc.title}")
                    file_extension = os.path.splitext(file_key)[1].lower()

                    # Save content to a temporary file for loading
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                        temp_file.write(file_content)
                        temp_file_path = temp_file.name

                    # Choose loader based on file type
                    if file_extension == '.pdf':
                        loader = PyPDFLoader(temp_file_path)
                    elif file_extension == '.csv':
                        loader = CSVLoader(temp_file_path)
                    elif file_extension == '.txt':
                        loader = TextLoader(temp_file_path)
                    else:
                        print(f"Unsupported file type for {doc.title}")
                        continue

                    # Load and chunk the document
                    loaded_docs = loader.load()
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
                    chunks = text_splitter.split_documents(loaded_docs)
                    
                    # Collect all document chunks
                    all_chunks.extend(chunks)

                    # Clean up temporary file after loading
                    os.remove(temp_file_path)

            except Exception as e:
                print(f"Error loading document {doc.title}: {e}")
                continue

        # Check if all_chunks is not empty before indexing
        if all_chunks:
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            # Create FAISS vector store and index the document embeddings
            vector_store = FAISS.from_documents(all_chunks, embeddings)
            vector_store.save_local("faiss_index")
            print("FAISS index created successfully.")
        else:
            print("No document texts found to index.")

    @staticmethod
    def query_documents(query: str):
        # Load the vector store and initialize the LLM
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        llm = OpenAI(api_key=OPENAI_API_KEY)

        # Set up the RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())

        # Get the answer from the chain
        answer = qa_chain.run(query)
        return answer