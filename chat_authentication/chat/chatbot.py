import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


load_dotenv()



#  contextualize_q_system_prompt = """Given a chat history and the latest user question \
#  which might reference context in the chat history, formulate a standalone question \
#  which can be understood without the chat history. Do NOT answer the question, \
#  just reformulate it if needed and otherwise return it as is."""
#  contextualize_q_prompt = ChatPromptTemplate.from_messages(
#      [
#          ("system", contextualize_q_system_prompt),
#          MessagesPlaceholder("chat_history"),
#          ("human", "{input}"),
#      ]
#  )
#  history_aware_retriever = create_history_aware_retriever(
#      llm, retriever, contextualize_q_prompt
#  )
#  

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, streaming=True)


# Incorporate the retriever into a question-answering chain.
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

#question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
#rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# now initialize the conversation chain
chain = qa_prompt | llm

### Statefully manage chat history ###
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)
