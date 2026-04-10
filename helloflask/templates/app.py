from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello,Babson! Welcome to Flask!'

@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    if name is None:
        name = 'World'
    name=name.capitalize()
    return render_template('hello.html', name=name)

@app.route('/square/<int:n>')
def square(n):
    return f'{n} squared is {n ** 2}'

@app.route('/stock/mergers')
def stock_mergers():
    import requests
    from datetime import datetime, timedelta

    today = datetime.now().strftime('%Y-%m-%d')
    thirty_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    # SEC EDGAR EFTS API: SC TO-T = third-party tender offers, S-4 = merger registrations
    url = (
        'https://efts.sec.gov/LATEST/search-index?q=%22%22'
        '&forms=SC+TO-T,S-4'
        f'&dateRange=custom&startdt={thirty_days_ago}&enddt={today}'
    )
    headers = {'User-Agent': 'Flask OIM3640 App admin@example.com'}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f'<h2>Error fetching data from SEC EDGAR: {e}</h2>'

    hits = data.get('hits', {}).get('hits', [])
    if not hits:
        return '<h2>No merger or acquisition filings found in the last 90 days.</h2>'

    seen = set()
    rows = []
    for hit in hits:
        src = hit.get('_source', {})
        # EDGAR returns display_names as a list of strings like "Company Name (TICKER)"
        display_names = src.get('display_names', [])
        if display_names and isinstance(display_names[0], str):
            company = display_names[0]
            ticker = ''
        elif display_names and isinstance(display_names[0], dict):
            company = display_names[0].get('name', 'Unknown')
            ticker = display_names[0].get('ticker', '')
        else:
            company = src.get('entity_name', 'Unknown')
            ticker = ''
        form_type = src.get('form_type', '')
        file_date = src.get('file_date', '')
        label = f'{company} ({ticker})' if ticker else company
        company = company.split('(')[0].strip()  # use name without ticker for dedup
        if company not in seen:
            seen.add(company)
            rows.append(f'<li><b>{label}</b> &mdash; {form_type} filed on {file_date}</li>')

    return (
        '<h2>Merger &amp; Acquisition Filings (Last 90 Days) &mdash; Source: SEC EDGAR</h2>'
        '<ul>' + ''.join(rows) + '</ul>'
    )

@app.route('/stock/<symbol>')
def stock(symbol):
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info['last_price']
    return f'The current price of {symbol.upper()} is ${price:.2f}'


if __name__ == '__main__':
    app.run(debug=True)