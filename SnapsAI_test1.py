import requests
from typing import List, Dict, Any
import random
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document
from typing import List, Dict, Any
import os

# Load environment variables
load_dotenv()
class InstagramAPI:
    BASE_URL = "https://graph.instagram.com"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_user_media(self, limit: int = 10) -> List[Dict[str, Any]]:
        endpoint = f"{self.BASE_URL}/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_url,thumbnail_url}",
            "access_token": self.access_token,
            "limit": limit
        }
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            raise Exception(f"Error fetching user media: {str(e)}")

    def format_posts(self, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted_posts = []
        for item in media_items:
            media_urls = []
            if item.get("media_type") == "CAROUSEL_ALBUM" and "children" in item:
                for child in item["children"]["data"]:
                    media_url = child.get("media_url") or child.get("thumbnail_url")
                    if media_url:
                        media_urls.append(self.ensure_https(media_url))
            else:
                media_url = item.get("media_url") or item.get("thumbnail_url")
                if media_url:
                    media_urls.append(self.ensure_https(media_url))

            formatted_post = {
                "id": item.get("id"),
                "media_urls": media_urls,
                "caption": item.get("caption", "No caption"),
                "media_type": item.get("media_type"),
                "permalink": item.get("permalink"),
                "timestamp": item.get("timestamp")
            }
            formatted_posts.append(formatted_post)
        return formatted_posts

    @staticmethod
    def ensure_https(url: str) -> str:
        if url and not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url
    
    def get_user_statistics(self, limit: int = 30) -> Dict[str, Any]:
        media_items = self.get_user_media(limit)
        
        post_types = {'IMAGE': 0, 'VIDEO': 0, 'CAROUSEL_ALBUM': 0}
        hashtags = {}
        posting_hours = {i: 0 for i in range(24)}

        for item in media_items:
            post_types[item.get('media_type', 'IMAGE')] += 1
            
            caption = item.get('caption', '')
            if caption:
                for tag in caption.split('#')[1:]:
                    tag = tag.strip().lower()
                    hashtags[tag] = hashtags.get(tag, 0) + 1
            
            timestamp = item.get('timestamp')
            if timestamp:
                hour = int(timestamp.split('T')[1].split(':')[0])
                posting_hours[hour] += 1

        popular_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_posting_hours = sorted(posting_hours.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_posts': len(media_items),
            'post_types': post_types,
            'popular_hashtags': popular_hashtags,
            'peak_posting_hours': peak_posting_hours
        }

def convert_post(caption: str, target_platform: str, has_image: bool) -> str:
    converted_post = caption

    if target_platform == "Twitter":
        converted_post = f"Check out my latest Instagram post! 📸\n\n{caption[:200]}..." if len(caption) > 200 else caption
        converted_post += "\n\n#Instagram #Social"
    elif target_platform == "LinkedIn":
        converted_post = f"I just shared a new post on Instagram! Here's a sneak peek:\n\n{caption}\n\nFollow me on Instagram for more updates!"
        converted_post += "\n\n#SocialMedia #Professional #Instagram"
    elif target_platform == "Facebook":
        converted_post = f"New Instagram Post Alert! 🚨\n\n{caption}\n\nHead over to my Instagram profile to see the full post and more content!"
    elif target_platform == "Thread":
        converted_post = f"Continuing from my recent Instagram post...\n\n{caption[:100]}...\n\nThoughts?"
    elif target_platform == "YouTube Community":
        converted_post = f"📸 Instagram Update 📸\n\n{caption[:150]}...\n\nCheck out my Instagram for the full post and more behind-the-scenes content!"

    if has_image:
        converted_post += "\n\n[Image from Instagram]"

    return converted_post







# Load environment variables
load_dotenv()

# Assuming the InstagramAPI class and convert_post function are defined as in the previous code

class RAGConverter:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-2024-08-06",
            openai_api_key=openai_api_key
        )
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    def create_vector_store(self, text: str):
        document = Document(page_content=text)
        texts = self.text_splitter.split_documents([document])
        return Chroma.from_documents(texts, self.embeddings)

    def generate_enhanced_post(self, original_post: str, target_platform: str, has_image: bool) -> str:
        vector_store = self.create_vector_store(original_post)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )

        prompt_template = """
        You are a social media expert. Your task is to convert an Instagram post to a {target_platform} post.
        Use the following rules:
        1. Maintain the core message and tone of the original post.
        2. Adapt the content to fit the style and conventions of {target_platform}.
        3. Include relevant hashtags for {target_platform}.
        4. Keep the post within the character limit of {target_platform} if applicable.
        5. If the original post has an image, mention it in the converted post.

        Original Instagram post: {original_post}
        Has image: {has_image}

        Convert this post for {target_platform}:

        Answer in korean. 
        """

        prompt = PromptTemplate(
            input_variables=["target_platform", "original_post", "has_image"],
            template=prompt_template
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        enhanced_post = chain.run(
            target_platform=target_platform,
            original_post=original_post,
            has_image=has_image
        )

        return enhanced_post

def main():
    # Initialize Instagram API
    instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not instagram_access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN not found in .env file")
    
    instagram_api = InstagramAPI(instagram_access_token)

    # Fetch recent Instagram posts
    media_items = instagram_api.get_user_media(limit=5)
    formatted_posts = instagram_api.format_posts(media_items)

    # Initialize RAG Converter
    rag_converter = RAGConverter()

    # Convert posts using RAG
    for post in formatted_posts:
        caption = post["caption"]
        has_image = len(post["media_urls"]) > 0

        target_platforms = ["Twitter", "LinkedIn", "Facebook", "Thread", "YouTube Community"]

        for platform in target_platforms:
            # Use the original convert_post function
            basic_converted_post = convert_post(caption, platform, has_image)

            # Use the RAG-enhanced conversion
            rag_converted_post = rag_converter.generate_enhanced_post(caption, platform, has_image)

            print(f"Original Post: {caption[:100]}...")
            print(f"Basic Converted Post for {platform}: {basic_converted_post[:100]}...")
            print(f"RAG Converted Post for {platform}: {rag_converted_post[:100]}...")
            print("-" * 50)

if __name__ == "__main__":
    main()