# AIrticle Writer 📄✍️

## Overview
**AIrticle Writer** is an AI-powered Streamlit app that generates an almost-ready-to-post article about any topic based on the main ideas provided by the user. Simply input your request for an article, and the system will perform a multi-step process to generate, enhance, and optimize the content, ready for posting. 

This app leverages a robust backend built using **LangChain**, which enables the process of scraping resources, generating ideas, creating an outline, expanding sections, and finally enhancing the article with a human-like tone. The article generation is done without using agents, ensuring better optimization of time and memory.

## Features
- **Streamlined Article Creation**: Enter your topic, and the app takes care of the rest. The system gathers content, summarizes ideas, structures the outline, and writes detailed sections.
- **Human-like Content Generation**: The LangChain-based backend ensures that the generated content is non-redundant, human-like, and well-structured.
- **Content Enhancement**: After creating the initial drafts, the app enhances the article by removing redundancy, adding professional tone and clarity, and creating lists where needed.
- **Scalable & Efficient**: The app uses pure Python for routing, ensuring an efficient, low-memory solution for generating and processing large amounts of text.

## How It Works
The app performs the following steps to generate the article:
![image](https://github.com/user-attachments/assets/94aab32f-1ca8-4605-9dc2-52e9260184eb)

1. **Scraping Resources**: The system gathers relevant articles from external knowledge sources based on search queries generated from the user's request.
2. **Summarizing**: Raw content is summarized into key ideas.
3. **Generating Bag of Ideas**: A diverse list of ideas is compiled from the scraped articles.
4. **Creating an Outline**: The bag of ideas is organized into a logical and coherent article outline in Markdown format.
5. **Generating Content**: For each section in the outline, the app expands the ideas into well-formed paragraphs.
6. **Article Improvement**: The article goes through a final stage of improvement, including adjusting tone, adding lists, and removing redundancy.
7. **Generating and Gathering Pictures (Upcoming)**: We are working on adding a feature that will generate or retrieve images relevant to the content, ensuring a more visually appealing final article.

## App Layout
Upon opening the app, you'll be prompted to enter a topic or article request. Once entered, the app will:
- Generate search queries.
- Create a list of ideas.
- Organize these ideas into an article outline.
- Expand the outline into a fully fleshed article.
- Finally, enhance the article, making it ready for publishing.

## Backend Components
The backend is built using **LangChain**, which provides all the necessary utilities for:
- Generating search queries based on user input.
- Summarizing the content of articles.
- Structuring the article outline.
- Expanding each section of the outline.
- Enhancing the final draft.

**Backend Overview**:
- **GoogleSerperAPIWrapper**: Scrapes articles based on search queries.
- **ChatOpenAI**: Manages the LLM interactions for generating and improving the article.
- **Chroma Vectorstore**: Used to index and retrieve relevant documents.
- **Prompt Templates**: Define the structure and flow for generating content (search queries, summaries, outlines, etc.).

## Conception of the Solution
The design of this system is inspired by the way many writers approach their articles: 
1. **Gather Information**: First, you gather external sources of knowledge.
2. **Create an Outline**: Next, you organize ideas into a coherent structure.
3. **Write and Expand**: You expand each idea into detailed sections.
4. **Enhance**: Finally, you polish the article to make it concise and professional.

The figure (shown above) reflects this process, starting with gathering information, then creating outlines and drafts, followed by article enhancement. The final result is an almost ready-to-post article. We are working on the **Generating and Gathering Pictures** feature, which is not yet available. Feel free to collaborate on this feature by submitting a pull request!

## Collaboration
The last component—**Generating and Gathering Pictures**—is under development. The idea behind this component is to either generate or retrieve relevant images to accompany sections of the article during its generation. If you'd like to contribute, feel free to make a pull request! I have already opened a feature request for this functionality, and your collaboration is welcome.

## Get Started
To run the app locally:
1. Clone this repository:
    ```bash
    git clone <repo-url>
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file that contains the following variables:
```
OPENAI_MODEL_NAME = <the model name>
OPENAI_API_KEY= <your api key>
SERPER_API_KEY= <your api key>
```

4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Dependencies
The project requires the following dependencies (listed in `pyproject.toml`):
- numpy
- pandas
- beautifulsoup4==4.12.3
- langchain==0.3.4
- langchain_chroma==0.1.4
- langchain_community==0.3.3
- langchain_core==0.3.12
- langchain_openai==0.2.3
- langchain_text_splitters==0.3.0
- pyperclip==1.9.0
- python-dotenv==1.0.1
- Requests==2.32.3
- streamlit==1.38.0

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
