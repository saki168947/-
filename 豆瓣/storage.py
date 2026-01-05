import csv
import json
import os
from io import StringIO, BytesIO

class DoubanStorage:
    def __init__(self):
        # Initialize in-memory storage
        self.data = {
            'info': {},
            'comments': []
        }

    def save_data(self, info, comments):
        """Update the in-memory data storage."""
        self.data['info'] = info
        self.data['comments'] = comments

    def get_data(self):
        """Retrieve all stored data."""
        return self.data
    
    def get_comments(self):
        """Retrieve only the comments list."""
        return self.data.get('comments', [])
    
    def get_info(self):
        """Retrieve only the movie info."""
        return self.data.get('info', {})

    def clear_data(self):
        """Reset the storage."""
        self.data = {
            'info': {},
            'comments': []
        }

    def generate_csv_stream(self):
        """Generate a CSV file stream from the stored data."""
        if not self.data['comments']:
            return None
            
        output = StringIO()
        writer = csv.writer(output)
        
        # Write Info
        writer.writerow(['电影名称', self.data['info'].get('title', '')])
        writer.writerow(['评分', self.data['info'].get('rating', '')])
        writer.writerow(['简介', self.data['info'].get('intro', '')])
        writer.writerow([])
        
        # Write Comments
        writer.writerow(['评论用户', '评论内容', '评分', '评论时间'])
        for c in self.data['comments']:
            writer.writerow([
                c.get('user', ''), 
                c.get('content', ''), 
                c.get('star', ''), 
                c.get('date', '')
            ])
            
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8-sig'))
        bytes_output.seek(0)
        
        return bytes_output

    def save_to_json_file(self, filename='douban_data.json'):
        """Save current data to a local JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
