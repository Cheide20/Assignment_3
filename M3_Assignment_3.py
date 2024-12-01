import streamlit as st
import yfinance as yf
import openai
import requests
import uuid
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

# Configuration
API_URL = ""
OPENAI_API_KEY = ""  # Replace with your OpenAI API key
openai.api_key = OPENAI_API_KEY
# Streamlit App Title
st.title("Market Sentiment Monitoring Agent")

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'stock_data' not in st.session_state:
    st.session_state['stock_data'] = {}
if 'sentiment_scores' not in st.session_state:
    st.session_state['sentiment_scores'] = []
if 'sentiment_history' not in st.session_state:
    st.session_state['sentiment_history'] = []

# Helper function to fetch stock data from Yahoo Finance
def fetch_stock_data(ticker, days=5000):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data

# Helper function to fetch news from Yahoo Finance
def fetch_news(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news
    return news

# Helper function to fetch social media data (placeholder)
def fetch_social_media_data(ticker):
    # Mock data: Replace with actual API calls to fetch social media posts
    social_media_posts = [
        f"Everyone is optimistic about {ticker} after their latest earnings!",
        f"{ticker} stock is overhyped in my opinion.",
        f"{ticker} has shown solid growth; I’m bullish on this company."
    ]
    return social_media_posts

# Helper function to fetch financial reports (placeholder)
def fetch_financial_reports(ticker):
    # Mock data: Replace with scraping or API calls to fetch financial reports
    financial_reports = [
        f"{ticker} reports record-breaking revenue growth in Q3.",
        f"{ticker}'s gross margins are under pressure despite increased sales.",
        f"{ticker}'s long-term guidance remains unchanged amid market uncertainty."
    ]
    return financial_reports

# Helper function to perform sentiment analysis with score and highlights
def analyze_sentiment_with_score(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Perform sentiment analysis on the following text. Provide the sentiment (Positive, Negative, Neutral), a sentiment score between -1 (negative) to +1 (positive), and a key highlight of the text."},
                {"role": "user", "content": text}
            ]
        )
        analysis = response['choices'][0]['message']['content']

        # Parse response (assuming structured format)
        lines = analysis.split("\n")
        sentiment = lines[0].split(":")[1].strip() if "Sentiment" in lines[0] else "Neutral"
        score = float(lines[1].split(":")[1].strip()) if "Score" in lines[1] else 0.0
        highlight = lines[2].split(":")[1].strip() if "Highlight" in lines[2] else "No highlight available"

        # Ensure sentiment is one of the expected categories
        if sentiment not in ["Positive", "Negative", "Neutral"]:
            sentiment = "Neutral"

        return sentiment, score, highlight

    except Exception as e:
        st.error(f"Error during sentiment analysis: {e}")
        return "Error", 0.0, "Error extracting highlight"

# Stock Data Section
st.header("Stock Data")
tickers = st.text_input("Enter stock ticker symbols separated by commas (e.g., AAPL, MSFT, NVDA):", "AAPL, MSFT, NVDA")

if st.button("Fetch Stock Data"):
    try:
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")[:5]]  # Limit to 5 tickers
        all_data = {}  # To store data for each ticker

        for ticker in ticker_list:
            data = fetch_stock_data(ticker)
            all_data[ticker] = data['Close']

        # Combine all stock data into a single DataFrame
        combined_data = pd.DataFrame(all_data)

        # Plot the combined data
        st.line_chart(combined_data)
        st.write(f"Showing stock data for: {', '.join(ticker_list)}")
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")

#---------------------------------------------------------------------------------
# Initialize session state for tickers if not already done
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = "AAPL, MSFT"  # Default tickers

# Input for stock tickers at the start of the page
st.header("Stock Selection")
tickers_input = st.text_input(
    "Enter stock ticker symbols separated by commas (e.g., AAPL, MSFT):",
    st.session_state['tickers']
)

if st.button("Set Selected Stocks"):
    st.session_state['tickers'] = tickers_input  # Save selected tickers to session state
    st.success(f"Selected stocks updated to: {tickers_input}")

# Market Sentiment Analysis Section
st.header("Market Sentiment Analysis with Scores and Highlights")

if st.button("Analyze Sentiment for Recent News"):
    try:
        # Use the selected tickers from session state
        ticker_list = [ticker.strip().upper() for ticker in st.session_state['tickers'].split(",")[:5]]  # Limit to 5 tickers
        all_sentiment_results = {}
        overall_sentiments = []
        overall_scores = []

        for ticker in ticker_list:
            news = fetch_news(ticker)
            if not news:
                st.warning(f"No recent news found for {ticker}.")
            else:
                st.write(f"### Recent News and Sentiment Analysis for {ticker}:")
                sentiment_results = []

                for article in news[:25]:  # Analyze up to 25 recent articles per ticker
                    title = article['title']
                    link = article['link']
                    sentiment, score, highlight = analyze_sentiment_with_score(title)
                    sentiment_results.append((sentiment, score, highlight))
                    overall_sentiments.append(sentiment)
                    overall_scores.append(score)
                    st.write(f"- [{title}]({link})")
                    st.write(f"  Sentiment: {sentiment}, Score: {score}")
                    st.write(f"  Highlight: {highlight}")
                    st.write("---")

                # Store sentiment results for the ticker
                all_sentiment_results[ticker] = sentiment_results

        # Display sentiment distribution for all tickers
        for ticker, results in all_sentiment_results.items():
            sentiments = [r[0] for r in results]
            sentiment_counts = {s: sentiments.count(s) for s in set(sentiments)}
            fig, ax = plt.subplots()
            ax.bar(sentiment_counts.keys(), sentiment_counts.values(), color="skyblue")
            ax.set_title(f"Sentiment Distribution for {ticker}")
            ax.set_xlabel("Sentiment")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

        # Overall Sentiment Distribution Plot
        st.write("### Overall Sentiment Distribution for All Tickers:")
        overall_sentiment_counts = {s: overall_sentiments.count(s) for s in set(overall_sentiments)}
        fig, ax = plt.subplots()
        ax.bar(overall_sentiment_counts.keys(), overall_sentiment_counts.values(), color="lightcoral")
        ax.set_title("Overall Sentiment Distribution")
        ax.set_xlabel("Sentiment")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Overall Average Sentiment Score
        overall_avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        st.write(f"### Overall Average Sentiment Score: {overall_avg_score:.2f}")

    except Exception as e:
        st.error(f"Error fetching or analyzing news: {e}")

#---------------------------------------------------------

# Overall Sentiment Analysis Section
st.header("Overall Sentiment Analysis (News, Social Media, Financial Reports)")

if st.button("Analyze Overall Sentiment"):
    try:
        ticker_list = [ticker.strip().upper() for ticker in st.session_state['tickers'].split(",")[:5]]  # Limit to 5 tickers
        overall_sentiments = []
        overall_scores = []

        for ticker in ticker_list:
            st.subheader(f"Sentiment Analysis for {ticker}")

            # **1. Analyze News Sentiment**
            st.write("### News Sentiment")
            news = fetch_news(ticker)
            if news:
                for article in news[:10]:  # Limit to 10 articles per ticker
                    title = article['title']
                    sentiment, score, highlight = analyze_sentiment_with_score(title)
                    overall_sentiments.append(sentiment)
                    overall_scores.append(score)
                    st.write(f"**News Title**: {title}")
                    st.write(f"**Sentiment**: {sentiment}, **Score**: {score}")
                    st.write(f"**Highlight**: {highlight}")
                    st.write("---")
            else:
                st.warning(f"No news articles found for {ticker}.")

            # **2. Analyze Social Media Sentiment**
            st.write("### Social Media Sentiment")
            social_media_posts = fetch_social_media_data(ticker)
            for post in social_media_posts:
                sentiment, score, highlight = analyze_sentiment_with_score(post)
                overall_sentiments.append(sentiment)
                overall_scores.append(score)
                st.write(f"**Post**: {post}")
                st.write(f"**Sentiment**: {sentiment}, **Score**: {score}")
                st.write(f"**Highlight**: {highlight}")
                st.write("---")

            # **3. Analyze Financial Reports Sentiment**
            st.write("### Financial Reports Sentiment")
            financial_reports = fetch_financial_reports(ticker)
            for report in financial_reports:
                sentiment, score, highlight = analyze_sentiment_with_score(report)
                overall_sentiments.append(sentiment)
                overall_scores.append(score)
                st.write(f"**Report**: {report}")
                st.write(f"**Sentiment**: {sentiment}, **Score**: {score}")
                st.write(f"**Highlight**: {highlight}")
                st.write("---")

        # **Overall Sentiment Distribution**
        st.subheader("Overall Sentiment Distribution")
        overall_sentiment_counts = {s: overall_sentiments.count(s) for s in set(overall_sentiments)}
        fig, ax = plt.subplots()
        ax.bar(overall_sentiment_counts.keys(), overall_sentiment_counts.values(), color="green")
        ax.set_title("Overall Sentiment Distribution")
        ax.set_xlabel("Sentiment")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # **Overall Average Sentiment Score**
        overall_avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        st.write(f"### Overall Average Sentiment Score: {overall_avg_score:.2f}")

    except Exception as e:
        st.error(f"Error analyzing overall sentiment: {e}")



# --------------------------------------------------------------------

# Chatbot Section
st.header("Ask questions (e.g what is the ticker of a firm?)")
if 'chat_id' not in st.session_state:
    st.session_state['chat_id'] = str(uuid.uuid4())

# Display the conversation using st.chat_message
for message in st.session_state['messages']:
    if message['role'] == 'user':
        with st.chat_message("user"):
            st.write(message['content'])
    else:
        with st.chat_message("assistant"):
            st.write(message['content'])

# Accept user input using st.chat_input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message to session state
    st.session_state['messages'].append({'role': 'user', 'content': user_input})

    # Display user's message
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare payload for API request (if using external API)
    payload = {
        "question": user_input,
        "chatId": st.session_state['chat_id'],
    }

    # Function to send the request
    def query(payload):
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    # Send the request and get the response
    try:
        data = query(payload)
        bot_reply = data.get('text', 'No response from the bot.')
        st.session_state['messages'].append({'role': 'assistant', 'content': bot_reply})

        # Display bot's message
        with st.chat_message("assistant"):
            st.write(bot_reply)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        