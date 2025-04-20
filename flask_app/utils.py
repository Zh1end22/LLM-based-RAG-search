import os
import requests
import json
import re
import time
import openai
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import uuid

# Load API keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "5e9eac672a1a8102fc751d0220d3eb97ed01dfa5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY" , "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")

# Initialize LangChain memory at the module level
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def search_articles(query):
    """
    Searches for articles related to the query using the Serper API.
    Returns a list of the top 5 articles with title and link.
    """
    if not SERPER_API_KEY:
        raise ValueError("Serper API key is missing.")
    
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json',
    }
    payload = json.dumps({"q": query})
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            print("Response Data:", data)
            articles = data.get("organic", [])
            
            if articles:
                print(f"Found {len(articles)} articles")
            else:
                print("No articles found.")
                return []
            
            top_articles = articles[:5]  # Changed from top_links to top_articles
            article_list = [{"title": article.get("title", "No title"), "link": article["link"]} for article in top_articles]  # Updated to return title and link
            print("Top 5 articles to be sent to fetch_article_content:")  # Updated print message
            for i, article in enumerate(article_list):  # Updated to print title and link
                print(f"{i+1}. {article['title']} - {article['link']}")
                
            return article_list  # Return list of dictionaries
        else:
            print(f"Error: Received status code {response.status_code} from Serper API")
            return []
    except Exception as e:
        print(f"Error occurred while searching articles: {e}")
        return []

import requests
from bs4 import BeautifulSoup
import time
from requests.exceptions import RequestException

def fetch_article_content(url: str) -> str:
    """
    Given a URL, scrape the web page using BeautifulSoup and return clean, useful content
    consisting of headings and paragraphs only.
    """
    print(f"Fetching content from: {url}")  # Debug URL being processed
    content = ""
    
    # Headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Ensure url is a string and valid
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                print(f"Invalid URL format: {url}")
                return f"Invalid URL: {url}"
            
            # Send HTTP GET request
            response = requests.get(url, headers=headers, timeout=120)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract headings (h1, h2, h3)
            headings = []
            for h_tag in ['h1', 'h2', 'h3']:
                elements = soup.find_all(h_tag)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 1:
                        headings.append(f"{h_tag.upper()}: {text}")
            
            # Extract paragraphs
            paragraphs = []
            p_elements = soup.find_all('p')
            for p in p_elements:
                text = p.get_text(strip=True)
                if text and len(text) > 5:
                    paragraphs.append(text)
            
            # Check if content was found
            if headings or paragraphs:
                content = "\n\n".join(headings) + "\n\n" + "\n\n".join(paragraphs)
                content = clean_content(content)  # Assumed to be your existing function
                
                # Truncate if too long
                if len(content) > 100000:
                    content = content[:100000] + "... [content truncated due to length]"
                
                print(f"\nScraped Content from {url}:\n{content[:50000]}...\n{'='*50}\n")
                return content
            
            print(f"No content found on attempt {attempt+1}, retrying...")
            time.sleep(5)
            
        except RequestException as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                print(f"Failed to scrape page after {max_retries} attempts")
                return f"Failed to scrape page: {str(e)}"
        except Exception as e:
            print(f"Unexpected error on attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                print(f"Failed to scrape page after {max_retries} attempts")
                return f"Failed to scrape page: {str(e)}"
            time.sleep(5)
    
    return "No content found after all retries."


def clean_content(text: str) -> str:
    """
    Clean the extracted content by removing extra whitespace, ads, etc.
    """
    if not text:
        return ""
    
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\s+', ' ', text)
    
    patterns_to_remove = [
        r'accept cookies',
        r'cookie policy',
        r'privacy policy',
        r'terms of service',
        r'advertisement',
        r'subscribe to our newsletter',
        r'sign up for our newsletter',
        r'subscribe now',
        r'sign up now',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(rf'(?i){pattern}.*?(\n|$)', '', text)
    
    return text.strip()

def get_conversation_history():
    """
    Formats the conversation history for the prompt.
    Returns formatted conversation history as a string.
    """
    messages = memory.chat_memory.messages
    if not messages:
        return "No previous conversation."
    
    history = []
    for message in messages:
        if isinstance(message, HumanMessage):
            history.append(f"Human: {message.content}")
        elif isinstance(message, AIMessage):
            history.append(f"AI: {message.content}")
    
    formatted_history = "\n".join(history)
    print(f"\nCurrent Conversation History:\n{formatted_history}\n{'-'*50}\n")
    return formatted_history

def summarize_with_openai(query: str, content: str) -> str:
    """
    Sends the query, conversation history, and content to Open AI API to generate a summarized response.
    If no Open AI API key is provided, returns a generic response with conversation history for testing.
    """
    # Get conversation history
    history_text = get_conversation_history()
    
    try:
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is missing.")
        
        # Initialize the OpenAI client with the API key
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = (
            f"Conversation History:\n{history_text}\n\n"
            f"Current Query: {query}\n\n"
            f"Content: {content}\n\n"
            "Please provide a concise summary of the key points from the content in response to the user's query, "
            "taking into account the conversation history. Keep the summary under 200 words and focus on the most relevant information."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes information concisely and accurately, considering past conversation context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.2,
        )
        
        summary = response.choices[0].message.content.strip()
        # Save the query and response to memory
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(summary)
        
        print(f"\nOpenAI Summary:\n{summary}\n{'='*50}\n")
        print(f"Memory after adding new interaction:\n{get_conversation_history()}\n{'-'*50}\n")
        return summary
    
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        # Generic response for testing when no API key is provided
        generic_summary = (
            f"[Generic Response for Testing]: Based on the query '{query}' and content, key points include general information about the topic. "
            f"For example, if the query is about '{query}', it might highlight relevant aspects based on the content. "
            f"(Conversation History: {history_text[:100]}...)"
        )
        # Save the query and generic response to memory
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(generic_summary)
        
        print(f"\nGeneric Response (OpenAI API issue):\n{generic_summary}\n{'='*50}\n")
        print(f"Memory after adding new interaction:\n{get_conversation_history()}\n{'-'*50}\n")
        return generic_summary

def generate_answer(content: str, query: str) -> str:
    """
    Generates an answer from the concatenated content and sends it to OpenAI for summarization.
    """
    if not content:
        return "Sorry, I couldn't find any relevant information on that topic."
    
    summarized_response = summarize_with_openai(query, content)
    return summarized_response

def process_articles(links, query):
    all_content = []
    failed_links = []
    processing_messages = []  # Add this line
    
    if all(isinstance(item, dict) for item in links):
        links = [item.get("link", "") for item in links]
        print(f"Converted links to URLs: {links}")
    
    for link in links:
        print(f"Processing link: {link}")
        processing_messages.append(f"Processing link: {link}")  # Add this line
        content = fetch_article_content(link)
        if content and not content.startswith("Failed"):
            all_content.append(content)
        else:
            failed_links.append(link)
    
    combined_content = "\n\n".join(all_content)
    
    if not combined_content:
        no_content_response = "No valid content was scraped from the provided links."
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(no_content_response + f" Links attempted: {', '.join(links)}")
        print(f"Memory after no content response:\n{get_conversation_history()}\n{'-'*50}\n")
        return {"answer": no_content_response + f" Links attempted: {', '.join(links)}", "processing_messages": processing_messages}  # Modify this line
    
    answer = generate_answer(combined_content, query)
    if failed_links:
        answer += f"\n\nNote: Failed to scrape content from: {', '.join(failed_links)}"
    return {"answer": answer, "processing_messages": processing_messages}  # Modify this line

def process_query(query):
    print(f"\nProcessing query: {query}")
    articles = search_articles(query)
    if articles:
        links = [article["link"] for article in articles]
        print(f"\nRetrieved {len(links)} links for processing: {links}")
        result = process_articles(links, query)  # Modify this line
        answer = result["answer"]  # Add this line
        processing_messages = result["processing_messages"]  # Add this line
        print(f"\nFinal Summarized Answer for '{query}':\n{answer}")
        return {"articles": articles, "answer": answer, "processing_messages": processing_messages}  # Modify this line
    else:
        no_links_response = "Sorry, I couldn't find any relevant articles on that topic."
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(no_links_response)
        print(f"Memory after no links response:\n{get_conversation_history()}\n{'-'*50}\n")
        print(f"\nFinal Answer for '{query}':\n{no_links_response}")
        return {"articles": [], "answer": no_links_response, "processing_messages": []}  # Modify this line
    
def get_memory_content():
    """
    Returns the content of the conversation memory.
    Useful for debugging or displaying conversation history.
    """
    return get_conversation_history()

def clear_memory():
    """
    Clears the conversation memory.
    Useful for starting a new conversation.
    """
    memory.clear()
    print("Conversation history has been cleared.")
    return "Conversation history has been cleared."

# Simple test if run directly
if __name__ == "__main__":
    while True:
        # Get query from user input
        query = input("Enter your query (or 'exit' to quit, 'clear' to clear memory): ")
        if query.lower() == 'exit':
            break
        elif query.lower() == 'clear':
            clear_memory()
            continue
        
        result = process_query(query)
        print("\nFinal result:", result)
        
        # Display conversation history
        print("\nConversation History:")
        print(get_memory_content())