import dash
import dash_html_components as html


app = dash.Dash(__name__, external_stylesheets=['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])


app.layout = html.Div([

    html.I(id='submit-button', n_clicks=0, className='fa fa-send'),
])


if __name__ == "__main__":
    app.run_server()
