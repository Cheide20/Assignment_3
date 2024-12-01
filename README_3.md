The Market Sentiment Monitoring Agent is a Streamlit application designed to deliver in-depth insights into financial market sentiment. By combining data from stock performance, news articles, social media, and financial reports, the tool enables users to track, analyze, and visualize sentiment trends for specific stock tickers through an intuitive interface.

The application retrieves historical stock prices via the Yahoo Finance API and displays closing price trends in dynamic line charts. For sentiment analysis, it gathers recent news articles related to the selected stock tickers and utilizes OpenAI's GPT model to evaluate them. The analysis provides a sentiment category (Positive, Negative, or Neutral), a sentiment score between -1 and +1, and key highlights extracted from the content. Additionally, mock data for social media and financial reports are included to complement the analysis, with plans to integrate real-time data in the future.

The application aggregates sentiment results from all data sources to perform an overall analysis. Users can visualize sentiment distribution with bar charts and access the average sentiment score for selected tickers. It also generates actionable insights based on sentiment trends, offering recommendations such as whether market sentiment is skewed positively, negatively, or remains neutral, assisting users in making better financial decisions.

The interface is interactive and allows users to dynamically add or update stock tickers. Enhanced functionality is provided through a chatbot, powered by an external API, that responds to queries about stock data and sentiment analysis. Moreover, a continuous monitoring feature operates in the background, regularly fetching and analyzing sentiment data to ensure users always have access to the latest insights.