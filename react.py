# react.py
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from tools import general_chat, search_products_by_embedding, get_promotion_by_category, get_social_recommendations, verify_recommendation_consistency

load_dotenv()

# We can keep the standard ReAct prompt or customize it for our recommendation system
react_prompt = hub.pull("hwchase17/react")

# Define our tools
tools = [
    search_products_by_embedding,
    get_promotion_by_category,
    get_social_recommendations,
    general_chat,
    verify_recommendation_consistency
]

llm = ChatOpenAI(model="gpt-4")

react_agent_runnable = create_react_agent(llm, tools, react_prompt)