import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import textwrap

def fetch_theme_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def parse_theme_data(soup):
    themes = []
    theme_cards = soup.find_all('div', class_='shared-item_cards-grid-image_card_component__content')
    
    for card in theme_cards:
        theme_name = card.find('h3', class_='shared-item_cards-item_name_component__root').text.strip() if card.find('h3', class_='shared-item_cards-item_name_component__root') else np.nan
        author = card.find('a', class_='shared-item_cards-author_category_component__link').text.strip()
        price = card.find('div', class_='shared-item_cards-price_component__root').text.strip()
        rating_count = card.find('span', class_='shared-stars_rating_component__starRatingCount').text.strip()
        sales_count = card.find('div', class_='shared-item_cards-sales_component__root').text.strip()
        
        themes.append({
            'Theme Names': theme_name, 
            'Author': author, 
            'Price': price, 
            'Rating Count': rating_count, 
            'Sales Count': sales_count
        })
    
    return pd.DataFrame(themes)

def clean_data(df):
    # Clean Price Column
    df['Price'] = df['Price'].replace({'\$': '', ',': ''}, regex=True).astype(float).fillna(0).astype(int)

    # Clean Rating Count
    df['Rating Count'] = df['Rating Count'].replace(r'[()]', '', regex=True).str.replace('K', '').astype(float)
    df['Rating Count'] *= 1000  
    df['Rating Count'] = df['Rating Count'].astype(int)

    # Clean Sales Count
    df['Sales Count'] = df['Sales Count'].replace({'K': '', 'Sales': ''}, regex=True).astype(int)
    
    return df

def plot_highest_rated_authors(df, filename='Highly-Rated-Authors.png'):
    high_rate_theme = df.groupby('Author')['Rating Count'].sum().sort_values(ascending=False).head()
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=high_rate_theme.index, y=high_rate_theme.values, palette='viridis')
    plt.title('Highly Rated Authors', size=20)
    plt.xlabel('Theme Authors', size=15)
    plt.ylabel('Total Ratings', size=15)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filename)  
    plt.close()  

def plot_highest_sales_themes(df, filename='Top-Selling-Themes.png'):
    top_sales_theme = df.sort_values(by='Sales Count', ascending=False).head()
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Theme Names', y='Sales Count', data=top_sales_theme, palette='Blues_d')
    wrapped_labels = top_sales_theme['Theme Names'].apply(lambda x: '\n'.join(textwrap.wrap(x, width=10)))
    plt.xticks(ticks=range(len(top_sales_theme)), labels=wrapped_labels, rotation=45, ha='right')
    plt.title('Top Selling Themes', size=20)
    plt.xlabel('Theme Names', size=15)
    plt.ylabel('Sales Count', size=15)
    plt.tight_layout()
    plt.savefig(filename) 
    plt.close()  

def main():
    url = 'https://themeforest.net/top-sellers'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    
    # Fetch and parse data
    soup = fetch_theme_data(url, headers)
    if soup:
        df = parse_theme_data(soup)
        df = clean_data(df)

        # Analyze and plot, saving results as images
        plot_highest_rated_authors(df, 'Highly-Rated-Authors.png')  # Save as image
        plot_highest_sales_themes(df, 'Top-Selling-Themes.png')  # Save as image

        # Optional: print out dataframe info
        print(df.info())
    else:
        print("Failed to retrieve data.")

if __name__ == '__main__':
    main()
