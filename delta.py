import dash
from dash import dcc
from dash import html
from energies import energies
from population import population
from deces import deces
from brevet import brevet

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,  title="Delta", suppress_callback_exceptions=True) # , external_stylesheets=external_stylesheets)
server = app.server
pop = population.WorldPopulationStats(app)
nrg = energies.Energies(app)
dec = deces.Deces(app)
brev = brevet.BrevetStats(app)
main_layout = html.Div([
    html.Div(className = "row",
             children=[ 
                 dcc.Location(id='url', refresh=False),
                 html.Div(className="two columns",
                          children = [
                              html.Center(html.H2("Δelta δata")),
                              dcc.Link(html.Button("Prix d'énergies", style={'width':"100%"}), href='/energies'),
                              html.Br(),
                              dcc.Link(html.Button('Natalité vs revenus', style={'width':"100%"}), href='/population'),
                              html.Br(),
                              dcc.Link(html.Button('Décès journaliers', style={'width':"100%"}), href='/deces'),
                              dcc.Link(html.Button('Réussite au brevet', style={'width':"100%"}), href='/brevet'), 
                              html.Br(),
                              html.Br(),
                              html.Br(),
                              html.Center(html.A('Code source', href='https://github.com/oricou/delta')),
                          ]),
                 html.Div(id='page_content', className="ten columns"),
            ]),
])


home_page = html.Div([
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    dcc.Markdown("Choisissez le jeu de données dans l'index à gauche."),
])

to_be_done_page = html.Div([
    dcc.Markdown("404 -- Désolé cette page n'est pas disponible."),
])

app.layout = main_layout

# "complete" layout (not sure that I need that)
app.validation_layout = html.Div([
    main_layout,
    to_be_done_page,
    pop.main_layout,
])

# Update the index
@app.callback(dash.dependencies.Output('page_content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/energies':
        return nrg.main_layout
    elif pathname == '/population':
        return pop.main_layout
    elif pathname == '/deces':
        return dec.main_layout
    elif pathname == '/brevet':
        return brevet.main_layout
    else:
        return home_page


if __name__ == '__main__':
    app.run_server(debug=True)
