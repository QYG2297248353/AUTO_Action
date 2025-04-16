import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time

def get_total_pages(soup):
    """从分页器获取总页数"""
    last_page = soup.select_one('.page.last')
    if last_page:
        last_page_url = last_page['href']
        return int(last_page_url.split('page=')[-1])
    # 如果没有最后一页链接，尝试从数字页码获取
    pages = soup.select('.page_selector a.page')
    return max([int(p.text) for p in pages if p.text.isdigit()]) if pages else 1

def scrape_page(url):
    """抓取单个页面数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def extract_videos(soup):
    """从页面解析视频数据"""
    videos = []
    for video_div in soup.select('div.video'):
        try:
            video_id = video_div.select_one('.id').text.strip()
            title = video_div.select_one('.title').text.strip()
            relative_url = video_div.find('a')['href']
            full_url = urljoin(base_url, relative_url)
            
            img_tag = video_div.find('img')
            image_url = img_tag['src'] if img_tag else None

            videos.append({
                "id": video_id,
                "title": title,
                "url": full_url,
                "image_url": image_url,
                "actors": extract_actors(title)
            })
        except Exception as e:
            print(f"Error parsing video: {str(e)}")
    return videos

def scrape_all_pages():
    base_url = "https://www.javlibrary.com/cn/vl_mostwanted.php"
    
    # 获取第一页确定总页数
    soup = scrape_page(base_url)
    if not soup:
        return {"videos": []}
    
    total_pages = get_total_pages(soup)
    print(f"发现 {total_pages} 个分页")
    
    all_videos = extract_videos(soup)  # 第一页数据
    
    # 遍历剩余分页
    for page in range(2, total_pages + 1):
        page_url = f"{base_url}?&mode=2&page={page}"
        print(f"正在抓取第 {page}/{total_pages} 页: {page_url}")
        
        page_soup = scrape_page(page_url)
        if page_soup:
            all_videos.extend(extract_videos(page_soup))
        
        time.sleep(1.5)  # 遵守爬虫礼仪
    
    return {"videos": all_videos}

# 原有extract_actors函数保持不变

if __name__ == "__main__":
    data = scrape_all_pages()
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"共抓取 {len(data['videos'])} 条视频数据")
