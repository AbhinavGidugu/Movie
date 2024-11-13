from flask import Flask, render_template, request, url_for, redirect, session,flash
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session handling

movies = pd.read_csv("final_data.csv")
alt_movies = pd.read_csv("data_sorted.csv")
similarity = pd.read_csv("top_100_similar_movies.csv")

def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017") 
    db = client['minorProject']
    return db['movies'], db['users']

movies_collection, user_collection = connect_to_mongodb()

def search_movies(query):
    query = query.lower().replace(" ", "")
    results = movies[movies['searchTitle'].str.contains(query, na=False)] 
    ans = []

    if not results.empty:
        movie_index = movies[movies['originalTitle'] == results.iloc[0]['originalTitle']].index[0]
        similar_movies = similarity.iloc[movie_index].values.tolist() 
        for i in similar_movies[1:11]:
            movie_data = movies.iloc[i]
            movie_doc = movies_collection.find_one({"originalTitle": movie_data.originalTitle})
            poster_image = movie_doc.get('poster_image_base64', None) if movie_doc else None
            ans.append({'title': movie_data.originalTitle, 'poster': poster_image})
    else:
        top_movies = alt_movies.head(10)
        for _, movie_data in top_movies.iterrows():
            movie_doc = movies_collection.find_one({"originalTitle": movie_data.originalTitle})
            poster_image = movie_doc.get('poster_image_base64', None) if movie_doc else None
            ans.append({'title': movie_data.originalTitle, 'poster': poster_image})
    
    return ans

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/first")
def first():
    return render_template("first.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.args.get("query")
    results = search_movies(query)
    return render_template("result.html", movies=results)

@app.route("/login",methods=["GET", "POST"])
def login():
    return render_template("login.html", flag=0)

@app.route("/check", methods=["GET","POST"])    
def check():
    name = request.form.get("name")
    password = request.form.get("password")
    user_doc = user_collection.find_one({"Username": name})
    error=None
    if not password:
        error="Incorrect Password"
        return render_template("login.html",error=error)
    
    if user_doc:
        actual_password = user_doc.get('password')
        if password == actual_password:
            session['current_user'] = name  # Store user in session
            return redirect(url_for('first'))
        else:
            error="Incorrect Password"
            return render_template("login.html", error=error)
    
    return render_template("login.html", flag=1)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        confirm_password = request.form.get("re-password")
        error=None
        user_doc = user_collection.find_one({"Username": name})

        if user_doc:
            error="Username already exists"
            return render_template("signup.html", error=error)
        
        if password == confirm_password:
            document = {"Username": name, "password": password, "Watchlist": [], "History": []}
            user_collection.insert_one(document)
            return render_template("login.html", flag=0)
        else:
            error="Re-enter password"
            return render_template("signup.html", error=error)
    return render_template("signup.html", flag=0)

@app.route("/watchlist")
def watchlist():
    current_user = session.get('current_user')
    user_doc = user_collection.find_one({"Username": current_user})
    watchlist = user_doc.get('Watchlist', [])
    myList = []

    for ele in watchlist:
        movie_doc = movies_collection.find_one({'originalTitle': ele})
        if movie_doc:
            myList.append(movie_doc)

    return render_template("watchlist.html", List=myList)

@app.route("/history")
def history():
    current_user = session.get('current_user')
    user_doc = user_collection.find_one({"Username": current_user})
    history = user_doc.get('History', [])
    myList = []

    for ele in history:
        movie_doc = movies_collection.find_one({'originalTitle': ele})
        if movie_doc:
            myList.append(movie_doc)

    return render_template("history.html", List=myList)

@app.route("/movies/<movie_name>")
def cinema(movie_name):
    movie_doc = movies_collection.find_one({"originalTitle": movie_name})
    current_user = session.get('current_user') 
    user_doc = user_collection.find_one({"Username": current_user})
    watchlist=user_doc.get('Watchlist')
    history=user_doc.get('History')
    in_watchlist = movie_name in watchlist
    in_history = movie_name in history

    if movie_doc:
        actors = movie_doc.get('actors', '')
        if isinstance(actors, str) and actors:
            actors = actors.split(",")[:3]
            actors = ', '.join(actors)

        else:
            actors="Not available"
        
        movie_details = {
            'title': movie_doc.get('originalTitle'),
            'genre': movie_doc.get('genres', 'Unknown'),
            'rating': movie_doc.get('Rating', 'N/A'),
            'director': movie_doc.get('director', 'Unknown'),
            'actors': actors,
            'description': movie_doc.get('description', 'No description available'),
            'poster': movie_doc.get('poster_image_base64', None) 
        }
    else:
        movie_details = {
            'title': movie_name,
            'description': 'No information available',
            'poster': None
        }

    return render_template("movie.html", movie=movie_details,in_watchlist=in_watchlist,in_history=in_history)

@app.route("/addToWatchList/<movie_id>")
def addToWatchList(movie_id):
    current_user = session.get('current_user')  # Get the currently logged-in user

    if not current_user:
        flash('Please log in to add movies to your watchlist.')
        return redirect(url_for('login'))

    movie_title = movie_id  # Get the movie title passed as parameter
    if not movie_title:
        flash('No movie selected.')
        return redirect(url_for('home'))

    # Find the current user's document in the database
    user_doc = user_collection.find_one({"Username": current_user})

    if user_doc:
        watchlist = user_doc.get('Watchlist', [])  # Get the user's current watchlist or an empty list

        if movie_title not in watchlist:
            watchlist.append(movie_title)  # Add the movie to the watchlist if not already present

            # Update the user's watchlist in the database
            user_collection.update_one(
                {"Username": current_user},  # Filter by the username
                {"$set": {"Watchlist": watchlist}}  # Update the watchlist field
            )
            flash(f'{movie_title} added to your watchlist!')
        else:
            flash(f'{movie_title} is already in your watchlist.')

    else:
        flash('User not found.')
    
    return redirect(url_for('cinema',movie_name=movie_id))

@app.route("/addToHistory/<movie_id>")
def addToHistory(movie_id):
    current_user = session.get('current_user')  # Get the currently logged-in user
    if not current_user:
        flash('Please log in to see History.')
        return redirect(url_for('login'))

    movie_title = movie_id  # Get the movie title passed as parameter
    if not movie_title:
        flash('No movie selected.')
        return redirect(url_for('home'))

    # Find the current user's document in the database
    user_doc = user_collection.find_one({"Username": current_user})

    if user_doc:
        history = user_doc.get('History', [])  # Get the user's current watchlist or an empty list

        if movie_title not in history:
            history.append(movie_title)  # Add the movie to the watchlist if not already present

            # Update the user's watchlist in the database
            user_collection.update_one(
                {"Username": current_user},  # Filter by the username
                {"$set": {"History": history}}  # Update the watchlist field
            )
            flash(f'{movie_title} added to History!')
        else:
            flash(f'You have already seen {movie_title}')

    else:
        flash('User not found.')
    
    return redirect(url_for('cinema',movie_name=movie_id))

@app.route('/removeFromWatch/<movie_id>')
def removeFromWatch(movie_id):
    current_user = session.get('current_user')

    if not current_user:
        flash('Please log in to modify your watchlist.')
        return redirect(url_for('login'))

    # Find the user's document in the database
    user_doc = user_collection.find_one({"Username": current_user})

    if user_doc:
        watchlist = user_doc.get('Watchlist', [])  # Retrieve the watchlist or an empty list
        if movie_id in watchlist:
            watchlist.remove(movie_id)  # Remove the movie from the watchlist

            # Update the user's watchlist in the database
            user_collection.update_one(
                {"Username": current_user},
                {"$set": {"Watchlist": watchlist}}
            )
            flash(f'{movie_id} removed from your watchlist.')
        else:
            flash(f'{movie_id} is not in your watchlist.')
    else:
        flash('User not found.')

    return redirect(url_for('watchlist'))


if __name__ == '__main__':
    app.run(debug=True)
