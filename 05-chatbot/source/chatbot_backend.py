import os
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain_aws import ChatBedrockConverse

# Shared AI connection
_bedrock_llm = None

def get_bedrock_client():
    """Create AWS Bedrock AI connection"""
    global _bedrock_llm
    if _bedrock_llm is None:
        model_id = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')
        _bedrock_llm = ChatBedrockConverse(
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            model=model_id,
            temperature=0.1,
            max_tokens=1000
        )
    return _bedrock_llm

def create_chat_memory():
    """Create conversation memory"""
    return ConversationSummaryBufferMemory(
        llm=get_bedrock_client(), 
        max_token_limit=2000
    )

def get_ai_response(user_input, chat_memory):
    """Get AI response with memory"""
    conversation_chain = ConversationChain(
        llm=get_bedrock_client(), 
        memory=chat_memory, 
        verbose=True
    )
    return conversation_chain.invoke(user_input)['response']



