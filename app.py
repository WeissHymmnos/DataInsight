import matplotlib
matplotlib.use('Agg')  # 在导入 pyplot 之前设置非交互式后端

from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('mysql+pymysql://root:@localhost/real_estate')

# 加载和处理数据
def analyze_real_estate():
    # 数据文件
    df = pd.read_csv('data/us_house_Sales_data.csv')
    
    # 数据预处理
    df['Price'] = pd.to_numeric(df['Price'].replace(r'[\$,]', '', regex=True), errors='coerce')
    df = df.dropna(subset=['Price', 'City', 'Area (Sqft)'])
    
    # 计算关键统计数据
    avg_price = np.mean(df['Price'])
    price_by_city = df.groupby('City')['Price'].mean().sort_values(ascending=False)
    
    # 生成可视化图
    plt.figure(figsize=(12, 6))
    price_by_city.head(10).plot(kind='bar')
    plt.title('Top 10 Cities by Average Listing Price')
    plt.xlabel('City')
    plt.ylabel('Average Price (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/price_by_city.png')
    plt.close()
    
    # 保存到 MySQL
    df.to_sql('properties', con=engine, if_exists='replace', index=False)
    
    return avg_price, price_by_city.head(10).to_dict()

@app.route('/')
def index():
    avg_price, price_by_city = analyze_real_estate()
    return render_template('index.html', avg_price=avg_price, price_by_city=price_by_city)

if __name__ == '__main__':
    app.run(debug=True)
