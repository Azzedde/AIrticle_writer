import os
import re
import ast
import concurrent.futures
import bs4
import requests
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Define tools
def get_main_text(url):
    # Fetch the content of the webpage
    response = requests.get(url)
    
    # If the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        
        # Find the <main> tag
        main_content = soup.find('main')
        
        # If a <main> tag is found, extract its text
        if main_content:
            return main_content.get_text(separator='\n', strip=True)
        else:
            return ""
    else:
        return ""
@tool
def gather_articles(search_query: str, api_key: str, link_file:str) -> list:
    """A tool to gather articles from the web based on a search query"""
    now = datetime.now()
    search = GoogleSerperAPIWrapper(k=5)
    results = search.results(search_query, api_key = api_key)
    article_links = []
    article_texts = []
    with open(link_file, "w") as file:

        for article in results['organic']:
            text = get_main_text(article['link'])
            if text != '':
                article_links.append(article['link'])
                article_texts.append(text)
                # append the article link and text to the end of the file
                file.write(f"Link: {article['link']}\n")
                file.write(f"Text: {text}\n")
                file.write("\n")
    return article_links, article_texts



# Define the LLM:
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL_NAME)

# Define prompts
gather_template_prompt = ChatPromptTemplate.from_template("You will receive the main idea of an article, your task is to generate a list of 5 search queries in order to gather articles that fall in the same context as the main idea given. The search queries should be diverse and different form each other. Your output should be a json list.\n Main idea: {main_idea}\n JSON list of search queries: ")
summary_template_prompt = ChatPromptTemplate.from_template("You will receive the text of an article. Summarize it by keeping only the most important ideas in the form of bullet points. Each idea should be a direct, informative and factual sentence, not mentioning the author. Your output should be only a detailed list of bullet points highlighting key points from the text. Don't use titles and complexe bullet points, but instead simple bullet points\nArticle text: {article_text}\n Summary in the form of a list of bullet points: ")
outline_template_prompt = ChatPromptTemplate.from_template(
    """You will receive a bag of ideas, which is a large list of concepts and thoughts. Your task is to create an outline of an article in markdown format based on the context and themes of the provided ideas. Group similar ideas into sections, avoid repetition, and ensure the outline flows logically. The final output should be a concise, well-structured outline, avoiding redundancy.
Follow this example format:
# Title of the Article
## Introduction
    -idea1
    -idea2
    ...
## Section1
    -idea3
    -idea4
    ...
## Section2
    -idea5
    -idea6
    ...
...
## Conclusion
    -idea7
    -idea8
    ...
Bag of ideas: {bag_of_ideas}\nOutline in markdown format: """
)

expanded_section_prompt = ChatPromptTemplate.from_template(
"""You will receive a section title and a list of main ideas that you need to expand in paragraphs only. Your task is to create a detailed expansion of the section in markdown format. You can use only paragraphs. Don't make a conclusion. Use your knowledge and the additional context presented.

Section Text {section_text}
Additional Context: {context}

Detailed section in markdown format without a conclusion:
"""
)

enhance_template = ChatPromptTemplate.from_template(
"""You will receive a draft of an article that you need to enhance and improve its writing.
Enhancement list:
- Reduce repetition
- Reduce redundancy
- Direct, professional and human tone
- Avoid saying blend and obvious things
- Don't over explain things
- Add bullet points lists when listing items that don't follow a specific order or hierarchy
- Add numbered lists when listing items that follow a specific order or hierarchy
- Make the titles have one capital letter at the beginning only

Draft Article: {draft}

Revised and enhanced version of the article:
"""
)

# Define output parsers
def parse_search_queries(ai_message: AIMessage) -> str:
    """Parse the python list of search_queries from the AI message"""
        # Regex to extract text between ``` ignoring 'python'
    pattern = r"```(?:json)?([\s\S]*?)```"
    match = re.search(pattern, ai_message.content)

    if match:
        extracted_text = match.group(1)
        list = ast.literal_eval(extracted_text)

    return list

def parse_article_ideas(ai_message: AIMessage) -> str:
    """Parse the bullet points list of ideas summarized of an article from the AI message"""
        # Regex to extract text between ``` ignoring 'python'
    bullet_points_list = [line.strip('- ').strip() for line in ai_message.content.splitlines() if line.strip()]


    return bullet_points_list


def parse_markdown(ai_message: AIMessage) -> dict:
    # Remove the first and last triple backticks ```markdown and ```
    markdown_text = ai_message.content.strip('```').strip()

    # Find the main title (text after #)
    title_match = re.search(r'^# (.+)', markdown_text)
    title = title_match.group(1).strip() if title_match else None

    # Find all sections (starting with ##) and their content
    sections = {}
    section_matches = re.split(r'^## ', markdown_text, flags=re.MULTILINE)

    # Process sections and extract their content
    for section in section_matches[1:]:  # skip the content before the first ##
        # Split section header and the rest of the content
        section_header, *section_content = section.split('\n', 1)
        section_header = section_header.strip()
        section_content = section_content[0].strip() if section_content else ''
        
        # Store the section content
        sections[section_header] = section_content
    
    # Construct the final dictionary
    result = {
        'title': title,
        'sections': sections
    }

    return result


# Define chains

gather_chain = gather_template_prompt | llm | parse_search_queries

summary_article_chain = summary_template_prompt | llm | parse_article_ideas

outline_article_chain = outline_template_prompt | llm | parse_markdown

def init_rag_chain(file_link):
    # Load, chunk and index the contents of the blog.
    loader = TextLoader(file_link)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY))

    # Retrieve and generate using the relevant snippets of the blog.
    retriever = vectorstore.as_retriever()
    expand_rag_chain = (
    {"context": retriever | format_docs, "section_text": RunnablePassthrough()}
    | expanded_section_prompt
    | llm
    | StrOutputParser()
    )
    return expand_rag_chain

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

enhance_article_chain = enhance_template | llm | StrOutputParser()

# Optimization code for the double loops of the gather_articles function


def process_query(query, link_file):
    # Process a single query
    article_links, article_texts = gather_articles.invoke({
        "search_query": query, 
        "api_key": SERPER_API_KEY, 
        "link_file": link_file
    })
    
    summary_list = []
    for article in article_texts:
        bullet_points_article_summary = summary_article_chain.invoke({"article_text": article})
        summary_list.extend(bullet_points_article_summary)
    
    return summary_list

def create_bag_of_ideas(search_queries, link_file):
    bag_of_ideas = []
    
    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of arguments for each query, passing the link_file along
        futures = [executor.submit(process_query, query, link_file) for query in search_queries]
        
        # Collect the results as they are completed
        for future in concurrent.futures.as_completed(futures):
            bag_of_ideas.extend(future.result())
    
    return bag_of_ideas

def AIrticle_writer(user_request):
    # start time
    start_time = datetime.now()
    # Step1: create search queries:
    search_queries = gather_chain.invoke({"main_idea": user_request})
    print("Step1: create search queries finished")
    # return search queries and continue execution
    bag_of_ideas = []
    link_file = f'articles_{datetime.now()}.txt'
    # Step2: create the bag_of_ideas
    bag_of_ideas = create_bag_of_ideas(search_queries, link_file)
    print("bag_of_ideas", bag_of_ideas)
    
    print("Step2: create the bag_of_ideas finished")
    # Step3: create the outline
    outline = outline_article_chain.invoke({"bag_of_ideas": bag_of_ideas})
    print("outline", outline)
    print("Step3: create the outline finished")
    # Step4: expand the sections
    if outline['sections'] is None:
        return "There was an error in the outline creation"
    draft = ""
    for title, text in outline['sections'].items():
        section=f"{title}\n{text}"
        rag_chain = init_rag_chain(link_file)
        expanded_section = rag_chain.invoke(section)
        draft += expanded_section
    
    print("Step4: expand the sections finished")
    # Step5: enhance the article
    enhanced_article = enhance_article_chain.invoke({"draft": draft})
    print("Step5: enhance the article finished")
    
    # end time
    end_time = datetime.now()
    print(f"Time taken: {end_time - start_time}")
    return enhanced_article

