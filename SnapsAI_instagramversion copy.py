import os
import sqlite3  
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.documents import Document
from PIL import Image
import io
import base64
import requests
import facebook
from facebook import GraphAPI

class EnvironmentSetup:
    @staticmethod
    def load_env(env_path: str):
        load_dotenv(env_path)
        print("Environment variables set successfully.")

class ImageProcessor:
    @staticmethod
    def resize_image(image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
        image.thumbnail(max_size)
        return image

    @staticmethod
    def convert_to_format(image: Image.Image, format: str) -> Image.Image:
        if image.format.lower() != format.lower():
            new_image = Image.new("RGB", image.size, (255, 255, 255))
            new_image.paste(image, mask=image.split()[3] if len(image.split()) > 3 else None)
            return new_image
        return image

    @staticmethod
    def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
        if filter_name == "grayscale":
            return image.convert("L")
        return image

    @staticmethod
    def encode_image(image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

class InstagramAPI:
    def __init__(self, access_token: str):
        self.graph = GraphAPI(access_token)

    def get_user_id(self, username: str) -> str:
        try:
            response = self.graph.request(f'/{username}')
            return response['id']
        except facebook.GraphAPIError as e:
            print(f"Facebook Graph API Error: {e.message}")
            # API 응답의 전체 내용 출력
            if hasattr(e, 'result'):
                print(f"Full API Response: {e.result}")
            return None

    def get_recent_posts(self, user_id: str, limit: int = 10) -> List[dict]:
        try:
            response = self.graph.request(f'/{user_id}/media', {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp',
                'limit': limit
            })
            return response['data']
        except Exception as e:
            print(f"Error getting recent posts: {e}")
            return []

    def download_image(self, url: str) -> Optional[Image.Image]:
        try:
            response = requests.get(url)
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

class RAGChain:
    def __init__(self, vectorstore: Chroma):
        self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        self.llm = ChatOpenAI(model="gpt-4-0613", temperature=0.7)
        self.prompt = self._create_prompt()
        self.rag_chain = self._create_rag_chain()

    @staticmethod
    def _format_docs(docs: List[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are an expert in social media content creation and platform-specific formatting. Use the following context and given parameters to convert the input post to the target platform format.

Input Post: {input_post}
Source Platform: {source_platform}
Target Platform: {target_platform}
Image Included: {image_included}

Context (Style guides and platform-specific information):
{context}

Convert the input post to the target platform format, ensuring it adheres to the platform's best practices and limitations. Maintain the core message and adapt any platform-specific features (e.g., hashtags, mentions, character limits). If an image is included, provide suggestions for image placement or formatting.

Converted Post:
"""
        prompt_template = PromptTemplate(input_variables=['context', 'input_post', 'source_platform', 'target_platform', 'image_included'], template=template)
        return ChatPromptTemplate(
            input_variables=['context', 'input_post', 'source_platform', 'target_platform', 'image_included'],
            messages=[HumanMessagePromptTemplate(prompt=prompt_template)]
        )

    def _create_rag_chain(self):
        return (
            {"context": self.retriever | self._format_docs, "input_post": RunnablePassthrough(), "source_platform": RunnablePassthrough(), "target_platform": RunnablePassthrough(), "image_included": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def convert_post(self, input_post: str, source_platform: str, target_platform: str, image_included: bool) -> str:
        return "".join(self.rag_chain.stream({
            "input_post": input_post,
            "source_platform": source_platform,
            "target_platform": target_platform,
            "image_included": "Yes" if image_included else "No"
        }))

class SocialMediaConverter:
    def __init__(self, db_dir: str, env_path: str):
        EnvironmentSetup.load_env(env_path)
        self.documents = self.load_documents(db_dir)
        print(f"Loaded {len(self.documents)} documents")
        if not self.documents:
            raise ValueError(f"No documents found in {db_dir}")
        self.splits = self.split_documents(self.documents)
        print(f"Created {len(self.splits)} splits")
        self.vectorstore = self.create_vectorstore(self.splits)
        self.rag_chain = RAGChain(self.vectorstore)
        self.conversion_history = []
        self.image_processor = ImageProcessor()
        
        instagram_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        if not instagram_access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN not found in .env file")
        self.instagram_api = InstagramAPI(instagram_access_token)

    @staticmethod
    def load_documents(db_dir: str) -> List[Document]:
        print(f"Attempting to load documents from {db_dir}")
        loader = DirectoryLoader(
            db_dir,
            glob="**/*.pdf",
            loader_cls=PyMuPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents")
        for doc in documents:
            print(f"Document source: {doc.metadata.get('source')}")
        return documents

    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=50, add_start_index=True
        )
        return text_splitter.split_documents(documents)

    @staticmethod
    def create_vectorstore(documents: List[Document]) -> Chroma:
        return Chroma.from_documents(documents=documents, embedding=OpenAIEmbeddings())


    def get_instagram_posts(self, username: str, limit: int = 5) -> List[dict]:
        user_id = self.instagram_api.get_user_id(username)
        if user_id:
            return self.instagram_api.get_recent_posts(user_id, limit)
        return []

    def convert_instagram_post(self, post: dict, target_platform: str) -> Tuple[str, Optional[Image.Image]]:
        input_post = post.get('caption', '')
        image_url = post.get('media_url')
        
        original_image = None
        if image_url:
            original_image = self.instagram_api.download_image(image_url)

        converted_post = self.rag_chain.convert_post(input_post, "Instagram", target_platform, bool(original_image))
        
        processed_image = None
        if original_image:
            processed_image = self.process_image(original_image, target_platform)
        
        self.conversion_history.append((input_post, "Instagram", target_platform, converted_post, image_url))
        return converted_post, processed_image

    def process_image(self, image: Image.Image, target_platform: str) -> Image.Image:
        if target_platform == "Facebook":
            image = self.image_processor.resize_image(image, (2048, 2048))
            image = self.image_processor.convert_to_format(image, "PNG")
        elif target_platform == "LinkedIn":
            image = self.image_processor.resize_image(image, (1200, 627))
            image = self.image_processor.convert_to_format(image, "PNG")
        # Add more platform-specific image processing as needed
        return image

    def save_conversion_history(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            for input_post, source, target, converted_post, image_url in self.conversion_history:
                f.write(f"Source ({source}): {input_post}\n")
                f.write(f"Target ({target}): {converted_post}\n")
                if image_url:
                    f.write(f"Image: {image_url}\n")
                f.write("\n")
        print(f"변환 내역이 {filename}에 저장되었습니다.")

    def upload_to_database(self, db_name: str):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversions
                          (id INTEGER PRIMARY KEY, input_post TEXT, source_platform TEXT, 
                           target_platform TEXT, converted_post TEXT, image_url TEXT)''')
        for input_post, source, target, converted_post, image_url in self.conversion_history:
            cursor.execute("INSERT INTO conversions (input_post, source_platform, target_platform, converted_post, image_url) VALUES (?, ?, ?, ?, ?)",
                           (input_post, source, target, converted_post, image_url))
        conn.commit()
        conn.close()
        print(f"변환 내역이 {db_name} 데이터베이스에 업로드되었습니다.")

if __name__ == "__main__":
    db_dir = r"C:\Users\james\Desktop\Snaps\social_media_guidelines"
    env_path = '.env'  # Assuming .env is in the same directory as the script
    
    converter = SocialMediaConverter(db_dir, env_path)
    
    instagram_username = input("Instagram 사용자 이름을 입력하세요: ")
    posts = converter.get_instagram_posts(instagram_username)
    
    if not posts:
        print("게시물을 가져올 수 없습니다.")
    else:
        for post in posts:
            print(f"\nInstagram 게시물:\n{post.get('caption', '(캡션 없음)')}")
            
            target_platform = input("대상 플랫폼을 입력하세요 (Facebook, Naver blog, LinkedIn, Thread): ")
            
            converted_post, processed_image = converter.convert_instagram_post(post, target_platform)
            
            print("\n변환된 게시물:")
            print(converted_post)
            
            if processed_image:
                print("\n이미지가 처리되었습니다.")
                processed_image.show()  # 처리된 이미지 표시
            
            print("\n" + "="*50 + "\n")

    # 변환 내역 저장 및 데이터베이스 업로드
    converter.save_conversion_history("conversion_history.txt")
    converter.upload_to_database("conversions.db")