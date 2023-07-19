
import os
from quart import Quart, request, jsonify, render_template
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import openai

app = Quart(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
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

@app.route('/analyze', methods=['POST'])
async def analyze():
    # api_key = request.headers.get('X-Api-Key')
    # if not api_key:
    #     return jsonify({'error': 'Unauthorized'}), 401
    ticker = (await request.form)['ticker']
    if not ticker:
        return jsonify({'error': 'Missing ticker'}), 400
    if ticker in cache:
        return cache[ticker]
    try:
        response = await generate(ticker)
        cache[ticker] = response
        return response
    except Exception as e:
        return jsonify({'error': 'Data fetch failed'}), 500

@app.route('/')
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

