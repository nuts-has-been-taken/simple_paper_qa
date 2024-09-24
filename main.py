from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from tools import retriever, paper_search
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_chat(prompt:str, model="gpt-4o-mini"):
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

# 從文檔建立 embedding 進行問答
def paper_qa(file_name):
    if not file_name.endswith('.txt'):
        file_name += '.txt'
    print(f"---讀取論文 {file_name} 並且建立索引---")
    chunks = retriever.split_doc(file_name)
    embeddings = retriever.get_embeddings(chunks)
    query = input("\n輸入你要問的問題，如果要離開請輸入exit : ")
    while query != "exit":
        relative_doc = retriever.search_similar_chunk(query, chunks, embeddings)
        qa_prompt = f"這是從論文 {file_name} 中擷取的資訊:\n{relative_doc}\n回答用戶的問題:{query}"
        res = gpt_chat(qa_prompt)
        print(f"{res}\n")
        # 回到迴圈
        query = input("\n輸入你要問的問題，如果要離開請輸入exit : ")
    print("")
    return

# 讀取 user input
user_input = input("請輸入你要查找的論文，如果要離開請輸入exit : ")

while user_input != "exit":

    # 先搜尋檔案庫有沒有
    db_documents = retriever.list_files_in_documents()
    check_prompt = f"資料庫中有以下論文檔案:\n{db_documents}\n用戶想要查找的論文是:{user_input}\n如果沒有這個論文請輸出 no，如果有這個論文請輸出論文檔案名稱，只輸入檔案名稱不要任何路徑"
    response = gpt_chat(check_prompt)
    if response != "no":
        # 資料庫已存在論文
        print(f"---檔案庫找到相關論文---")
        paper_qa(response)
    else:
        # 從 arxiv 搜尋論文
        paper_info = paper_search.fetch_arxiv_papers(user_input)
        print(f"從 arxiv 上找到這篇論文\n{json.dumps(paper_info, indent=4)}\n")
        user_input = input("這是你想要查的嗎 (yes/no) :")
        if user_input == "yes":
            # 下載論文到檔案庫
            print("----下載論文中----")
            paper_url = paper_info['pdf_url']
            paper_name = paper_info['title']
            paper_search.download_pdf(paper_url, f"./documents/{paper_name}.pdf")
            paper_search.convert_pdf_to_txt(f"./documents/{paper_name}.pdf", f"./documents/{paper_name}.txt")
            os.remove(f"./documents/{paper_name}.pdf")
            paper_qa(paper_name)
        else:
            print("\n請重新切換關鍵字來搜尋\n")
    
    # 重新回圈
    user_input = input("請輸入你要查找的論文，如果要離開請輸入exit : ")

# done
print("---------exit---------")