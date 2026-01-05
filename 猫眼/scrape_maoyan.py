import re
import requests
import csv
from datetime import datetime

def scrape_maoyan_movies():
    """
    爬取猫眼电影排行数据
    """
    # 猫眼电影排行榜URL
    url = "https://maoyan.com/board"
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://maoyan.com/'
    }
    
    movies = []
    
    try:
        # 发送GET请求
        print("正在请求猫眼电影数据...")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            html_content = response.text
            
            # 使用正则表达式提取电影信息
            # 匹配模式：电影排名、名称、上映时间等信息
            
            # 电影排名和名称的正则表达式
            rank_pattern = r'<p class="p-rank">\n\s+<i class="board-index board-index-\d+">\n\s+(\d+)\n\s+</i>'
            name_pattern = r'<p class="p-name"><a href="[^"]*" title="([^"]*)"'
            
            # 获取所有电影名称
            names = re.findall(name_pattern, html_content)
            
            # 获取所有排名
            ranks = re.findall(rank_pattern, html_content)
            
            # 提取更详细的信息（使用多个正则表达式组合）
            # 电影块的正则表达式
            movie_pattern = r'<p class="p-rank">.*?<i class="board-index board-index-\d+">.*?(\d+).*?</i>.*?<p class="p-name"><a href="[^"]*" title="([^"]*)".*?<p class="p-score">.*?<i class="score">([^<]*)</i>.*?</p>'
            
            # 更精确的匹配方式 - 获取整个电影div块
            movie_blocks = re.findall(
                r'<div class="board-item-content">(.*?)</div>\s*</div>\s*</li>',
                html_content,
                re.DOTALL
            )
            
            print(f"找到 {len(movie_blocks)} 部电影")
            
            for idx, block in enumerate(movie_blocks[:10], 1):  # 获取前10部
                # 从块中提取排名
                rank_match = re.search(r'<i class="board-index board-index-\d+">.*?(\d+)', block, re.DOTALL)
                rank = rank_match.group(1) if rank_match else str(idx)
                
                # 从块中提取电影名称
                name_match = re.search(r'<p class="p-name"><a[^>]*title="([^"]*)"', block)
                name = name_match.group(1) if name_match else "未知"
                
                # 从块中提取评分
                score_match = re.search(r'<i class="score">([^<]*)</i>', block)
                score = score_match.group(1) if score_match else "N/A"
                
                # 从块中提取上映时间
                release_match = re.search(r'<p class="p-release">(\d{4}-\d{2}-\d{2})</p>', block)
                release_date = release_match.group(1) if release_match else "未知"
                
                movie_info = {
                    '排名': rank,
                    '电影名称': name,
                    '评分': score,
                    '上映时间': release_date
                }
                
                movies.append(movie_info)
                print(f"排名 {rank}: {name} - 评分: {score}")
            
            # 保存为CSV文件
            if movies:
                filename = 'maoyan_movies.csv'
                save_to_csv(movies, filename)
                print(f"\n数据已保存到 {filename}")
            
            return movies
        
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []

def save_to_csv(movies, filename):
    """
    将电影数据保存到CSV文件
    """
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            if movies:
                writer = csv.DictWriter(f, fieldnames=movies[0].keys())
                writer.writeheader()
                writer.writerows(movies)
        print(f"成功保存 {len(movies)} 部电影数据")
    except Exception as e:
        print(f"保存文件出错: {e}")

def save_to_txt(movies, filename):
    """
    将电影数据保存到文本文件
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("猫眼电影排行榜\n")
            f.write("=" * 60 + "\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for movie in movies:
                f.write(f"排名: {movie['排名']}\n")
                f.write(f"电影名称: {movie['电影名称']}\n")
                f.write(f"评分: {movie['评分']}\n")
                f.write(f"上映时间: {movie['上映时间']}\n")
                f.write("-" * 60 + "\n")
        
        print(f"成功保存为文本文件: {filename}")
    except Exception as e:
        print(f"保存文本文件出错: {e}")

if __name__ == "__main__":
    # 爬取数据
    movies = scrape_maoyan_movies()
    
    # 同时保存为TXT和CSV格式
    if movies:
        save_to_txt(movies, 'maoyan_movies.txt')
        save_to_csv(movies, 'maoyan_movies.csv')
        
        print("\n爬取完成！")
    else:
        print("\n未能获取数据")
