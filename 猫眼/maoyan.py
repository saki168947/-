from flask import Flask, render_template, jsonify, send_file
import re
import requests
import csv
import json
import os
from datetime import datetime
from io import StringIO, BytesIO
import jieba
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 存储爬取的电影数据
movies_data = []

def scrape_maoyan_movies():
    """
    爬取猫眼电影排行数据 (使用移动端接口)
    """
    global movies_data
    movies_data = []
    
    # 使用移动端地址，可以一次性获取100条数据且反爬较松
    url = "https://m.maoyan.com/asgard/board/4"
    
    # 模拟移动端 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://m.maoyan.com/asgard/board/4',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            html_content = response.text
            
            # 提取嵌入在页面中的 JSON 数据
            # 查找 var AppData = {...}; 模式
            json_match = re.search(r'var AppData = ({.*?});', html_content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                try:
                    data = json.loads(json_str)
                    # 提取电影列表
                    movies_list = data.get('data', {}).get('movies', [])
                    
                    for idx, movie in enumerate(movies_list, 1):
                        # 提取字段
                        rank = str(idx)
                        name = movie.get('nm', '未知')
                        score = str(movie.get('sc', '暂无评分'))
                        release_date = movie.get('rt', '未知')
                        movie_id = movie.get('id')
                        # 构建链接
                        movie_link = f"https://maoyan.com/films/{movie_id}" if movie_id else "#"
                        # 图片链接
                        image_url = movie.get('img', '')
                        # 替换图片尺寸，获取更高清的图 (可选)
                        if image_url:
                            image_url = image_url.replace('w.h', '128.180') # 尝试调整尺寸，或者直接用原图
                        
                        movie_info = {
                            '排名': rank,
                            '电影名称': name,
                            '评分': score,
                            '上映时间': release_date,
                            '链接': movie_link,
                            '图片': image_url
                        }
                        movies_data.append(movie_info)
                        
                    return True, f"成功爬取 {len(movies_data)} 部电影"
                    
                except json.JSONDecodeError as e:
                    return False, f"JSON解析失败: {e}"
            else:
                return False, "未找到电影数据 (AppData)"
        else:
            return False, f"请求失败，状态码: {response.status_code}"
            
    except Exception as e:
        return False, f"爬取过程中出错: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """
    API端点：执行爬虫
    """
    success, message = scrape_maoyan_movies()
    
    return jsonify({
        'success': success,
        'message': message,
        'data': movies_data,
        'count': len(movies_data)
    })

@app.route('/api/data', methods=['GET'])
def api_get_data():
    """
    API端点：获取当前爬取的数据
    """
    return jsonify({
        'data': movies_data,
        'count': len(movies_data)
    })

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """
    导出为CSV文件
    """
    try:
        if not movies_data:
            return jsonify({'success': False, 'message': '没有数据可导出'}), 400
        
        # 创建CSV内容
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['排名', '电影名称', '评分', '上映时间'])
        writer.writeheader()
        writer.writerows(movies_data)
        
        # 转换为字节流
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8-sig'))
        bytes_output.seek(0)
        
        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='maoyan_movies.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500

@app.route('/api/export/txt', methods=['POST'])
def export_txt():
    """
    导出为TXT文件
    """
    try:
        if not movies_data:
            return jsonify({'success': False, 'message': '没有数据可导出'}), 400
        
        # 创建TXT内容
        output = StringIO()
        output.write("猫眼电影排行榜\n")
        output.write("=" * 60 + "\n")
        output.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("=" * 60 + "\n\n")
        
        for movie in movies_data:
            output.write(f"排名: {movie['排名']}\n")
            output.write(f"电影名称: {movie['电影名称']}\n")
            output.write(f"评分: {movie['评分']}\n")
            output.write(f"上映时间: {movie['上映时间']}\n")
            output.write("-" * 60 + "\n")
        
        # 转换为字节流
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        return send_file(
            bytes_output,
            mimetype='text/plain',
            as_attachment=True,
            download_name='maoyan_movies.txt'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取统计数据
    """
    if not movies_data:
        return jsonify({'success': False, 'message': '没有数据'}), 400
    
    # 评分分布
    scores = []
    for m in movies_data:
        try:
            scores.append(float(m['评分']))
        except:
            pass
            
    score_dist = {'9.5-10.0': 0, '9.0-9.5': 0, '8.5-9.0': 0, '8.0-8.5': 0, '<8.0': 0}
    for s in scores:
        if s >= 9.5: score_dist['9.5-10.0'] += 1
        elif s >= 9.0: score_dist['9.0-9.5'] += 1
        elif s >= 8.5: score_dist['8.5-9.0'] += 1
        elif s >= 8.0: score_dist['8.0-8.5'] += 1
        else: score_dist['<8.0'] += 1
        
    # 年份分布
    years = {}
    for m in movies_data:
        date_str = m['上映时间']
        # 尝试提取年份 (假设格式包含 YYYY)
        match = re.search(r'\d{4}', date_str)
        if match:
            year = match.group(0)
            years[year] = years.get(year, 0) + 1
            
    # 排序年份
    sorted_years = dict(sorted(years.items()))
    
    return jsonify({
        'success': True,
        'score_distribution': score_dist,
        'year_distribution': sorted_years
    })

@app.route('/api/wordcloud', methods=['GET'])
def get_wordcloud():
    """
    生成词云图
    """
    if not movies_data:
        return jsonify({'success': False, 'message': '没有数据'}), 400
        
    text = " ".join([m['电影名称'] for m in movies_data])
    
    # 使用jieba分词
    words = jieba.cut(text)
    processed_text = " ".join(words)
    
    # 设置字体路径 (Windows常见字体)
    font_path = "C:/Windows/Fonts/msyh.ttc" # 微软雅黑
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simhei.ttf" # 黑体
        
    try:
        wc = WordCloud(
            font_path=font_path,
            background_color='white',
            width=800,
            height=600,
            max_words=100
        ).generate(processed_text)
        
        # 保存到内存
        img_io = BytesIO()
        wc.to_image().save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成词云失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
