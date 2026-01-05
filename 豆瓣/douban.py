from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import csv
import os
from io import StringIO, BytesIO
import jieba
from wordcloud import WordCloud
import base64
import random
import time

app = Flask(__name__)
app.secret_key = 'douban_secret_key'  # Required for session

from collections import Counter
import re
from storage import DoubanStorage
from analysis import DoubanAnalysis

# Initialize storage manager
storage = DoubanStorage()
# Initialize analysis manager
analyzer = DoubanAnalysis(storage)

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://movie.douban.com/'
    }

import concurrent.futures

def fetch_comment_page(base_url, start, session):
    """
    Helper function to fetch a single page of comments.
    """
    try:
        comments_url = f"{base_url}comments?status=P&start={start}"
        response = session.get(comments_url, headers=get_headers(), timeout=10)
        
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        comment_items = soup.select('.comment-item')
        
        page_comments = []
        for item in comment_items:
            # User info
            user_tag = item.select_one('.comment-info a')
            user = user_tag.text.strip() if user_tag else "未知用户"
            user_link = user_tag.get('href') if user_tag else "#"
            
            # Content
            content_tag = item.select_one('.short')
            content = content_tag.text.strip() if content_tag else ""
            
            # Date
            date_tag = item.select_one('.comment-time')
            date = date_tag.get('title') if date_tag else (date_tag.text.strip() if date_tag else "未知日期")
            
            # Rating
            star_span = item.select_one('.rating')
            star = star_span.get('title') if star_span else "未评分"
            
            if content:
                page_comments.append({
                    'user': user,
                    'content': content,
                    'date': date,
                    'star': star,
                    'link': user_link
                })
        return page_comments
    except Exception as e:
        print(f"Error fetching page {start}: {e}")
        return []

def crawl_douban(url):
    try:
        # 1. Fetch Main Page Info
        session = requests.Session()
        response = session.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code != 200:
            return False, f"请求失败，状态码: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Info
        title_tag = soup.select_one('h1 span[property="v:itemreviewed"]')
        title = title_tag.text.strip() if title_tag else "未知电影"
        
        rating_tag = soup.select_one('strong.ll.rating_num')
        rating = rating_tag.text.strip() if rating_tag else "暂无评分"
        
        intro_tag = soup.select_one('span[property="v:summary"]')
        intro = intro_tag.text.strip().replace('\n', '').replace(' ', '') if intro_tag else "暂无简介"
        
        # 2. Multi-threaded Comment Crawling
        # Determine base URL for comments
        if '?' in url:
            base_url = url.split('?')[0]
        else:
            base_url = url
        
        if not base_url.endswith('/'):
            base_url += '/'
            
        # We will fetch 5 pages (0, 20, 40, 60, 80) -> ~100 comments
        offsets = [0, 20, 40, 60, 80]
        
        all_comments = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_offset = {executor.submit(fetch_comment_page, base_url, offset, session): offset for offset in offsets}
            for future in concurrent.futures.as_completed(future_to_offset):
                try:
                    data = future.result()
                    all_comments.extend(data)
                except Exception as exc:
                    print(f"Generated an exception: {exc}")

        # If strict crawling failed or returned nothing (e.g. login block), try fallback to main page hot comments if needed
        # But we will trust the threaded result first. 
        if not all_comments:
             # Fallback: scrape from the main response we already have
            comment_items = soup.select('#hot-comments .comment-item')
            for item in comment_items:
                user_tag = item.select_one('.comment-info a')
                user = user_tag.text.strip() if user_tag else "未知用户"
                content_tag = item.select_one('.short')
                content = content_tag.text.strip() if content_tag else ""
                date_tag = item.select_one('.comment-time')
                date = date_tag.get('title') if date_tag else "未知日期"
                star_span = item.select_one('.rating')
                star = star_span.get('title') if star_span else "未评分"
                if content:
                    all_comments.append({'user': user, 'content': content, 'date': date, 'star': star, 'link': '#'})

        # Update storage
        info = {
            'title': title,
            'rating': rating,
            'intro': intro,
            'comments_count': len(all_comments)
        }
        storage.save_data(info, all_comments)
        
        return True, f"爬取成功! 共获取 {len(all_comments)} 条评论"
        
    except Exception as e:
        return False, f"爬取错误: {str(e)}"

# Analysis functions moved to analysis.py

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/crawler')
def crawler_page():
    return render_template('crawler.html') # Keeping this for reference, but dashboard is now the main one

@app.route('/stream')
def stream_page():
    return render_template('comments_stream.html', data=storage.get_data())

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/login', methods=['POST'])
def login():
    # Dummy login - accept any credentials or check specific ones
    # In a real scenario, you would validate against a database
    # Here we just set a session variable
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    # Login check removed for universal crawler access
    # if not session.get('logged_in'):
    #     return jsonify({'success': False, 'message': '未登录'}), 401
        
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL不能为空'})
        
    success, msg = crawl_douban(url)
    
    if success:
        wc_base64 = analyzer.generate_wordcloud_base64()
        rating_stats = analyzer.get_rating_statistics()
        word_stats = analyzer.get_word_frequency()
        
        return jsonify({
            'success': True,
            'data': storage.get_info(),
            'comments': storage.get_comments(), # Return comments for frontend
            'wordcloud': wc_base64,
            'rating_stats': rating_stats,
            'word_stats': word_stats
        })
    else:
        return jsonify({'success': False, 'message': msg})

@app.route('/download/csv')
def download_csv():
    if not session.get('logged_in'):
        return "未登录", 400
        
    bytes_output = storage.generate_csv_stream()
    if not bytes_output:
        return "无数据", 400
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='douban_data.csv'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
