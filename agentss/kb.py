from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import streamlit as st

from agents import function_tool

from dotenv import load_dotenv
import os

load_dotenv()  

@function_tool
def knowledge_base(question: str):
    """Use this tool to retrieve knowledge about the dental clinic in general
    to response to the question about dental related queries. Answer FAQs, services,
    prices, etc. about the dental clinic"""

    # print("> using retrieval tool")

    try:
        index_name = 'dclinic'

        # find API key in console at app.pinecone.io
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')


        model_name = 'text-embedding-ada-002'

        api_key = st.secrets['OPENAI_API_KEY']
        # api_key = os.getenv('OPENAI_API_KEY')

        embed = OpenAIEmbeddings(model=model_name,
                                 openai_api_key=api_key)

        docsearch = PineconeVectorStore(index_name=index_name, embedding=embed, pinecone_api_key=PINECONE_API_KEY)

        dd = docsearch.similarity_search(
            question,  # our search query
            k=3  # return 3 most relevant docs
        )
        ret = [d.page_content for d in dd]

        ## Using a reranker
        # co = cohere.Client("Yfl8ZfC4XhjbcHOhyBuSY3RANH1ra4ZNMkJci0eB")

        # rerank_docs = co.rerank(query=question,
        #                         documents=ret,
        #                         top_n=8,
        #                         model="rerank-english-v2.0")

        # print("retrieve")
        # print(ret)
        return ' '.join(ret)
        # print(rerank_docs)
        # return ' '.join([str(reranked) for reranked in rerank_docs])

    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred: {e}")
        print("error")
        return {"response": "error"}