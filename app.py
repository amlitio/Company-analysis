import os
import streamlit as st
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import openai
import asyncio

openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = st.secrets["OPENAI_API_KEY"]
cache = {}

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def generate(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"
    async with ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        financial_data = {}
        for row in soup.find_all('tr'):
            try:
                label = row.find('td').text
                value = row.find('td', attrs={'class': 'Fz(s)'}).text
                financial_data[label] = value
            except AttributeError:
                continue
        prompt = f"""
        Perform a comprehensive business analysis on the company with ticker symbol {ticker} based on the following financial data: {financial_data}.
        Analyze the company's revenue growth over the past five years.
        Compute the Return on Equity (ROE) and Gross Margin for the latest fiscal year.
        Calculate the company's Debt-to-Equity ratio.
        Present the company's stock performance over the last twelve months.
        Provide the market capitalization of the company and its dividend yield.
        Analyze the company's operating expenses.
        Evaluate the company's cash flow from operating activities and cash flow from investing activities.
        Compare the company's revenue growth and profit margins with its top competitors.
        Explore the company's expansion into renewable energy projects and its recent geographical market entries.
        Recommend specific strategic measures for the company to enhance its performance.
        """
        response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=500)
        return {'ticker': ticker, 'financial_data': financial_data, 'analysis': response.choices[0].text.strip()}

def run_async_function(func):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    return loop.run_until_complete(func)

ticker = st.text_input('Enter ticker symbol:')
if ticker:
    if ticker in cache:
        result = cache[ticker]
    else:
        result = run_async_function(generate(ticker))
        cache[ticker] = result
    st.write(result)
