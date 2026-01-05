from collections import Counter
import re
import jieba
from wordcloud import WordCloud
import base64
from io import BytesIO
import os

class DoubanAnalysis:
    def __init__(self, storage):
        self.storage = storage

    def get_rating_statistics(self):
        """Calculate rating distribution statistics."""
        comments = self.storage.get_comments()
        if not comments:
            return {}

        ratings = [c['star'] for c in comments]
        rating_counts = Counter(ratings)
        
        # Defined order for display
        rating_order = ["力荐", "推荐", "还行", "较差", "很差", "未评分"]
        sorted_ratings = {k: rating_counts.get(k, 0) for k in rating_order if k in rating_counts or rating_counts.get(k, 0) > 0}
        
        # Add any others that might exist
        for k, v in rating_counts.items():
            if k not in sorted_ratings:
                sorted_ratings[k] = v
                
        return sorted_ratings

    def get_word_frequency(self, top_n=10):
        """Calculate word frequency statistics."""
        comments = self.storage.get_comments()
        if not comments:
            return []

        text = "".join([c['content'] for c in comments])
        # Remove non-Chinese characters for cleaner stats
        text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
        
        words = jieba.cut(text)
        # Simple stop words list
        stop_words = {'的', '了', '是', '我', '在', '也', '都', '就', '有', '和', '人', '看', '不', '去', '一个', '很', '这一', '这', '那', '你', '吗', '啊', '吧', '呢', '电影', '片子'}
        filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]
        
        word_counts = Counter(filtered_words)
        return word_counts.most_common(top_n)

    def generate_wordcloud_base64(self):
        """Generate wordcloud image as base64 string."""
        comments = self.storage.get_comments()
        if not comments:
            return ""
        
        text = " ".join([c['content'] for c in comments])
        # Add intro text as well for better cloud
        text += " " + self.storage.get_info().get('intro', '')
        
        words = jieba.cut(text)
        processed_text = " ".join(words)
        
        font_path = "C:/Windows/Fonts/msyh.ttc"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/simhei.ttf"
            
        wc = WordCloud(
            font_path=font_path,
            background_color='black',
            colormap='Pastel1', # Bright colors for dark background
            width=800,
            height=400,
            max_words=150
        ).generate(processed_text)
        
        img_io = BytesIO()
        wc.to_image().save(img_io, 'PNG')
        img_io.seek(0)
        return base64.b64encode(img_io.getvalue()).decode('utf-8')
