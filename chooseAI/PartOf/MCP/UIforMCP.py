import requests
from bs4 import BeautifulSoup
from askgemma import ask_gemma  

class MCPWebSearch:
    def __init__(self):
        pass

    def fetch_site_text(self, url: str) -> str:

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            print(f"🌐 Loading: {url}")
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            

            text_parts = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'article']):
                text = tag.get_text(strip=True)
                if text and len(text) > 20:  
                    text_parts.append(text)
            
            full_text = " ".join(text_parts)

            if len(full_text) > 8000:
                full_text = full_text[:8000] + "..."
                
            print(f"✅ წამოღებული ტექსტი: {len(full_text)} სიმბოლო")
            return full_text.strip()
            
        except Exception as e:
            print(f"❌ [WARN] ვერ წამოიღო საიტის კონტენტი: {e}")
            return ""  

    def ask(self, question: str, url: str = None) -> str:
        """უსვამს კითხვას Gemma-ს, კონტექსტით თუ არის ხელმისაწვდომი"""
        context = ""

        if url:
            print(f"🔍 searching on website...")
            context = self.fetch_site_text(url)

        if context and len(context.strip()) > 50:
            print(f"📄 answer from the context ({len(context)} char)")
            return ask_gemma(question, context=context)
        else:
            print("💭 answers on its own")
            return ask_gemma(question)


# ======== გამოყენების მაგალითი ========
if __name__ == "__main__":
    
    mcp = MCPWebSearch()

    while True:
        print("\n" + "="*50)
        q = input("❓ Question: ").strip()
        
        if q.lower() in ['exit', 'quit',]:
            print("👋 Bye!")
            break
            
        if not q:
            continue
            
        site = input("🌐 website (chosen): ").strip() or None

        print("\n🤔 Loading...")
        answer = mcp.ask(q, site)
        print("\n📌 Answer:")
        print("-" * 50)
        print(answer)
        print("-" * 50)