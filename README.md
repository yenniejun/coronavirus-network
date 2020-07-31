# Coronavirus Network Analysis
This project looks at coronavirus news in several languages, performing topic modeling, and network analysis.

App can be found [here](https://coronavirus-network.herokuapp.com)

US News
* Over 60,000 news articles 
* Search terms: "coronavirus", "covid"
* News sources: 

Korean News
* Over 50,000 news articles
* Search terms: "코로나", "코비드"
* News sources: 조선일보, 중앙일보, 동아일보, 한겨레, 경향신문

# To run locally
First, clone the repo
```
git clone https://github.com/yenniejun/coronavirus-network.git
```

Next, install packages
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally, to run locally, open a terminal window
```
python3 app.py
```

# Push to Heroku
```
git status # view the changes
git add .  # add all the changes
git commit -m 'a description of the changes'
git push heroku master
```

# Tools used
* [Dash](https://dash.plotly.com/deployment) and PlotLy
* NetworkX
* Heroku

