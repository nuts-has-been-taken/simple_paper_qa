import arxiv
import requests
import fitz

def fetch_arxiv_papers(query, max_results=1):
    # 使用 arxiv 庫來搜索指定主題的論文
    search = arxiv.Search(
        query=query,
        max_results=max_results,
    )
    
    papers = []
    for result in search.results():
        paper_info = {
            "title": result.title.replace(":", ""),
            "authors": result.authors[0].name,
            "summary": result.summary,
            "pdf_url": result.pdf_url
        }
        papers.append(paper_info)
    
    # 先設定回傳一個就好
    return papers[0]

def download_pdf(url, output_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF 已下載到 {output_path}")
    else:
        print(f"無法下載 PDF：{response.status_code}")

def convert_pdf_to_txt(pdf_path, txt_output_path):
    # 打開 PDF
    doc = fitz.open(pdf_path)
    text = ""
    
    # 循環遍歷每一頁
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # 獲取頁面的文字內容
    
    # 將文字內容寫入 txt 檔案
    with open(txt_output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text)
    
    print(f"PDF 已轉換為文字並存到 {txt_output_path}")