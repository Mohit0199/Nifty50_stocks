import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

external_stylesheets = [
    {
        "href": "https://cdn.jsdelivr.net/npm/bootswatch@5.0.0-alpha2/dist/spacelab/bootstrap.min.css",
        "rel": "stylesheet",
        "integrity": "sha384-dZQ/D1fIe9SP9LH3snDLM/iAhOA1NVPpHCBfR5eJDIkNT+4UwGqX+8I0UD+OCQQ4",
        "crossorigin": "anonymous",
    }
]

desc = pd.read_csv('Nifty50_Description.csv')
company_list = desc['company_Name'].to_list()
opts = [{'label': i, 'value': i} for i in company_list]

quarters = pd.read_csv('Nifty50_Quarters.csv')
quarter_df = {name : group.drop('company_Name', axis=1) for name, group in quarters.groupby('company_Name')}

profitloss = pd.read_csv('Nifty50_ProfitLoss.csv')
pl_df = {name: group.drop('company_Name', axis=1) for name, group in profitloss.groupby('company_Name')}

shareholders = pd.read_csv('Nifty50_Shareholders.csv')
shareholder_df = {name: group.drop('company_Name', axis=1) for name, group in shareholders.groupby('company_Name')}

price = pd.read_csv('Nifty50_Price.csv')
price_df = {name : group for name, group in price.groupby('Company_Name')}

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Nifty 50", style={'color': '#fff', 'text-align': 'center', 'fontSize':'50'}),
    html.P('Welcome to the Stock Dashboard! This dashboard provides information about Nifty 50 stocks. Explore the performance of Nifty50 stocks from March 2022 to March 2023.',
           style={'color': '#fff','font-family': 'Arial', 'font-size': '18px'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Markdown('''
                       Select a company from the dropdown below:
                        '''),
                    dcc.Dropdown(id='dropdown', options=opts, value=None, style={'background-color': '#f8f9fa'}),
                ], className='card-body',style={'background-color': '#ecf0f1', 'border': '1px solid #dee2e6'})
            ], className='card')
        ], className='col-md-12', style={'margin-bottom': '20px'})
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                dcc.Markdown(id='company-description',
                             style={'font-family': 'Arial', 'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'}),
            ], className='card-body', style={'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
        ], className='col-md-8'),
        html.Div([
            html.Div([
                dcc.Markdown(id='financial-metrics',
                             style={'font-family': 'Arial', 'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
            ], className='card-body', style={'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
        ], className='col-md-4', style={'margin-bottom': '20px'})
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div(id='output-table-div', children=[])
            ], className='card-body', style={'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
        ], className='col-md-4', style={'margin-bottom': '20px'})
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div(id='profitloss-table-div', children=[])
            ], className='card-body', style={'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
        ], className='col-md-4', style={'margin-bottom': '20px'})
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div(id='shareholder-table-div', children=[])
            ], className='card-body', style={'background-color': '#ecf0f1', 'border': '1px solid #bdc3c7'})
        ], className='col-md-4', style={'margin-bottom': '20px'})
    ], className='row'),

    html.Div([
    dcc.Graph(id='stock-price-plot'),
    ], className='row'),

    html.Div([
        dcc.Graph(id='candlestick-chart'),
    ], className='row'),

], className='container')


app.title = "Nifty 50 Dashboard"


@app.callback(
    [Output('company-description', 'children'), Output('financial-metrics', 'children')],
    [Input('dropdown', 'value')]
)
def update_card(selected_company):
    if selected_company is None:
        return 'Please select a company', ''

    else:
        company_info = desc[desc['company_Name'] == selected_company].squeeze()
        selected_company_content = f"""
            **{selected_company}:**  
            {company_info['Description']}
        """
        
        metrics_content = f"""
            **Face Value:** {company_info['Face_Value']}  
            **Stock P/E:** {company_info['Stock_PE']}  
            **ROE%:** {company_info['ROE(%)']}  
            **ROCE%:** {company_info['ROCE(%)']}  
            **Market Cap:** {company_info['Market_Capital(Cr.)']}  
            **Dividend Yield%:** {company_info['Dividend_Yield(%)']}
        """
        return selected_company_content, metrics_content


@app.callback(
    Output('output-table-div', 'children'),
    [Input('dropdown', 'value')])
def display_quarterly_data(selected_company):
    if selected_company is None:
        return []

    else:
        selected_dataframe = quarter_df[selected_company]
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in selected_dataframe.columns],
            data=selected_dataframe.to_dict('records'),
            style_header={'backgroundColor': '#383c3d', 'color':'#edf3f5'},
            style_data={'backgroundColor': '#ecf0f1'},
            style_cell={'fontSize':16, 'font-family':'Arial'},
            style_table={'maxHeight': '400px', 'overflowY': 'scroll'}
        )
        return [
            html.H2("Quarterly Results", id='table-title', style={'font-family': 'Arial'}),
            dcc.Markdown("""Consolidated Figures in Rs. Crores""", style={'font-family': 'Arial'}),
            table]


@app.callback(
    Output('profitloss-table-div', 'children'),
    [Input('dropdown', 'value')])
def display_pl_data(selected_company):
    if selected_company is None:
        return []

    else:
        selected_dataframe = pl_df[selected_company]
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in selected_dataframe.columns],
            data=selected_dataframe.to_dict('records'),
            style_header={'backgroundColor': '#383c3d', 'color':'#edf3f5'},
            style_data={'backgroundColor': '#ecf0f1'},
            style_cell={'fontSize':16, 'font-family':'Arial'},
            style_table={'maxHeight': '400px', 'overflowY': 'scroll'}
        )
        return [
            html.H2("Profit & Loss", id='table-title', style={'font-family': 'Arial'}),
            dcc.Markdown("""For year march 2023  
                        Consolidated Figures in Rs. Crores""",
                        style={'font-family': 'Arial'}),
            table]
    

@app.callback(
    Output('shareholder-table-div', 'children'),
    [Input('dropdown', 'value')])
def display_pl_data(selected_company):
    if selected_company is None:
        return []

    else:
        selected_dataframe = shareholder_df[selected_company]
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in selected_dataframe.columns],
            data=selected_dataframe.to_dict('records'),
            style_header={'backgroundColor': '#383c3d', 'color':'#edf3f5'},
            style_data={'backgroundColor': '#ecf0f1'},
            style_cell={'fontSize':16, 'font-family':'Arial'},
            style_table={'maxHeight': '400px', 'overflowY': 'scroll'}
        )
        return [
            html.H2("Shareholding Pattern", id='table-title', style={'font-family': 'Arial'}),
            dcc.Markdown("""Numbers in percentages""",
                        style={'font-family': 'Arial'}),
            table]


@app.callback(
    Output('stock-price-plot', 'figure'),
    [Input('dropdown', 'value')]
)
def update_stock_price_plot(selected_company):
    if selected_company is None:
        return go.Figure()

    else:
        selected_dataframe = price_df[selected_company]
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=selected_dataframe['Date'], y=selected_dataframe['Close'], mode='lines', name='Close'))
        fig.update_layout(
            title=f"Stock Prices for {selected_company}",
            xaxis_title='Date',
            yaxis_title='Stock Price (Close)',
            template="plotly_dark"
        )
        return fig


@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('dropdown', 'value')]
)
def update_candlestick_chart(selected_company):
    if selected_company is None:
        return go.Figure()

    else:
        selected_dataframe = price_df[selected_company]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=[f"Candlestick Chart for {selected_company}", "Volume"])

        fig.add_trace(go.Candlestick(x=selected_dataframe['Date'],
                                     open=selected_dataframe['Open'],
                                     high=selected_dataframe['High'],
                                     low=selected_dataframe['Low'],
                                     close=selected_dataframe['Close'],
                                     increasing_line_color='green', decreasing_line_color='red',
                                     increasing_fillcolor='green', decreasing_fillcolor='red',
                                     line=dict(width=2),
                                     name='Candlestick'),
                      row=1, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")

        fig.add_trace(go.Bar(x=selected_dataframe['Date'],
                             y=selected_dataframe['Volume'],
                             marker_color='rgba(0, 0, 255, 0.5)',
                             name='Volume'),
                      row=2, col=1)

        return fig


if __name__ == "__main__":
    app.run_server(debug=True)