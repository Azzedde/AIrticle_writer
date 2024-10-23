import streamlit as st
import utils
import pyperclip
import datetime as time

# Streamlit App Layout
st.set_page_config(page_title="AI-Powered Article Generator", layout="centered")
st.title("✍️ AIrticle Writer📄")
st.write("Please enter a request for an article, and we will generate it for you. The process will take approximately **2 minutes**.")

# User input
request = st.text_input("Enter the topic or article request:")

if request:
    st.write("Generating your article... Please wait.")

    # Step 1: Generate search query
    with st.spinner('Step 1: Creating search queries...'):
        search_queries = utils.gather_chain.invoke({"main_idea": request})
        st.success('Step 1 completed!')
        st.write(f"Search query: {search_queries}")

    # Clear previous step
    st.empty()
    bag_of_ideas = []
    link_file = f'articles_{time.datetime.now()}.txt'
    # Step 2: Generate bag of ideas
    with st.spinner('Step 2: Generating ideas...'):
        bag_of_ideas = utils.create_bag_of_ideas(search_queries, link_file)
        st.success('Step 2 completed!')
        # show the list of ideas as a list of strings code
        st.code(bag_of_ideas, language="shell")

    # Clear previous step
    st.empty()

    # Step 3: Generate outline
    with st.spinner('Step 3: Creating outline...'):
        outline = utils.outline_article_chain.invoke({"bag_of_ideas": bag_of_ideas})
        st.success('Step 3 completed!')
        st.write("Outline:")
        for title, text in outline['sections'].items():
            st.write(f"**{title}:** {text}")

    # Clear previous step
    st.empty()

    # Step 4: Expand the sections
    draft=""
    with st.spinner('Step 4: Expanding sections...'):
        for title, text in outline['sections'].items():
            section=f"{title}\n{text}"
            rag_chain = utils.init_rag_chain(link_file)
            expanded_section = rag_chain.invoke(section)
            draft += expanded_section
        st.success('Step 4 completed!')
    print(draft)
            
    with st.spinner('Article draft is ready we are enhancing it now !'):
        enhanced_article = utils.enhance_article_chain.invoke({"draft": draft})
        st.success("Your article is ready!")
        
        a=st.markdown(enhanced_article, unsafe_allow_html=True)
        if st.button('Copy'):
            pyperclip.copy(a)
            st.success('Text copied successfully!')  # Displaying final article as markdown
