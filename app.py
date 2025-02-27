from flask import Flask, render_template
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)

CORS(app, origins=["https://elvis940.github.io/AI_Group-10_ExpertSystem_Assignment2/"])

# Enable CORS
CORS(app)

# Define the API route
@app.route("/api/data")
def get_data():
    return jsonify({"message": "CORS is working!"})

# Initialize Flask app
server = Flask(__name__)

# Serve the landing page
@server.route("/")
def landing_page():
    return render_template("index.html")

# Flask routes for additional pages
@server.route("/wildlife")
def wildlife():
    return render_template("wildlife.html")

@server.route("/Culture_places")
def Culture_places():
    return render_template("Culture_places.html")

@server.route("/adventure")
def adventure():
    return render_template("adventure.html")

@server.route("/Historical")
def Historical():
    return render_template("Historical.html")

@server.route("/Lakes")
def Lakes():
    return render_template("Lakes.html")

@server.route("/Food")
def Food():
    return render_template("Food.html")

# Initialize Dash app
app = dash.Dash(__name__, server=server, url_base_pathname="/dashboard/", external_stylesheets=[dbc.themes.CYBORG])
app.title = "Rwanda Tourism Planner"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            departure_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            destination TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Initialize the database when the app starts

# Data structures (experiences and destination_info)
experiences = {
    "Wildlife": {
        "destinations": {
            "Akagera National Park": ["safari", "bird watching", "game drives"],
            "Nyungwe Forest National Park": ["chimp trekking", "canopy walk", "birding"],
            "Volcanoes National Park": ["gorilla trekking", "hiking", "wildlife"],
            "Gishwati-Mukura National Park": ["forest walks", "primate tracking", "nature"],
            "Kigali's Natural History Museum": ["exhibits", "education", "history"],
            "Ibanda-Makera Forest": ["nature walks", "bird watching", "exploration"]
        }
    },
    "Cultural": {
        "destinations": {
            "Kigali Genocide Memorial": ["history", "education", "reflection"],
            "Ethnographic Museum (Huye)": ["artifacts", "culture", "history"],
            "King’s Palace Museum (Nyanza)": ["royalty", "traditions", "history"],
            "Rwanda Art Museum": ["art", "culture", "exhibits"],
            "Inema Arts Center (Kigali)": ["contemporary art", "workshops", "culture"],
            "Ntarama Church Memorial": ["history", "memorial", "reflection"]
        }
    },
    "Adventure": {
        "destinations": {
            "Mount Kigali": ["hiking", "views", "nature"],
            "Canopy Walkway (Nyungwe)": ["suspension bridge", "forest views", "adventure"],
            "Volcanoes National Park": ["gorilla trekking", "hiking", "climbing"],
            "Mount Bisoke": ["volcano hike", "crater lake", "adventure"],
            "Congo Nile Trail": ["cycling", "hiking", "scenic views"],
            "Lake Kivu": ["kayaking", "boat trips", "swimming"]
        }
    },
    "Rwanda’s Lakes": {
        "destinations": {
            "Lake Kivu": ["boating", "fishing", "relaxation"],
            "Lake Muhazi": ["fishing", "bird watching", "boat rides"],
            "Lake Ihema": ["boat tours", "wildlife", "fishing"],
            "Lake Rweru": ["scenic views", "fishing", "nature"],
            "Lake Burera": ["canoeing", "views", "relaxation"],
            "Lake Ruhondo": ["boat trips", "scenic beauty", "nature"]
        }
    },
    "Rwanda’s History": {
        "destinations": {
            "Kigali Genocide Memorial": ["history", "education", "memorial"],
            "Ntarama Church": ["history", "memorial", "reflection"],
            "Nyamata Church": ["history", "memorial", "education"],
            "King’s Palace (Nyanza)": ["royalty", "history", "culture"],
            "Murambi Memorial": ["history", "education", "memorial"],
            "Camp Kigali Memorial": ["history", "military", "memorial"]
        }
    },
    "Rwanda Food": {
        "destinations": {
            "Kigali City": ["restaurants", "local cuisine", "markets"],
            "Repub Lounge (Kigali)": ["dining", "cocktails", "atmosphere"],
            "Rubavu": ["lakefront dining", "fresh fish", "local food"],
            "Huye": ["traditional meals", "markets", "culture"],
            "Musanze": ["local cuisine", "fresh produce", "dining"],
            "Nyungwe (Nearby Villages)": ["village food", "traditional cooking", "culture"]
        }
    }
}

destination_info = {
    "Akagera National Park": ("Eastern Rwanda", "A savannah park with diverse wildlife including lions and rhinos. Expect thrilling game drives and bird watching."),
    "Nyungwe Forest National Park": ("Southwestern Rwanda", "A lush rainforest with chimpanzee trekking and a famous canopy walkway offering stunning views."),
    "Volcanoes National Park": ("Northern Rwanda", "Home to mountain gorillas and volcanic landscapes. Experience gorilla trekking and scenic hikes."),
    "Gishwati-Mukura National Park": ("Western Rwanda", "A regenerating forest with primate tracking and peaceful nature walks."),
    "Kigali's Natural History Museum": ("Kigali", "Learn about Rwanda’s biodiversity and geological history through engaging exhibits."),
    "Ibanda-Makera Forest": ("Southern Rwanda", "A hidden gem for nature walks and bird watching in a tranquil setting."),
    "Kigali Genocide Memorial": ("Kigali", "A poignant site to reflect on Rwanda’s history with educational exhibits."),
    "Ethnographic Museum (Huye)": ("Huye, Southern Rwanda", "Explore Rwanda’s cultural heritage with artifacts and traditional displays."),
    "King’s Palace Museum (Nyanza)": ("Nyanza, Southern Rwanda", "Step into royal history with a replica palace and cultural insights."),
    "Rwanda Art Museum": ("Kigali", "Admire Rwandan art in a historic setting, once a presidential palace."),
    "Inema Arts Center (Kigali)": ("Kigali", "Vibrant contemporary art and workshops showcasing local talent."),
    "Ntarama Church Memorial": ("Near Kigali", "A somber memorial of the genocide with a powerful historical narrative."),
    "Mount Kigali": ("Kigali", "Hike for panoramic city views and a refreshing nature escape."),
    "Canopy Walkway (Nyungwe)": ("Nyungwe Forest", "Walk a suspension bridge high above the forest for breathtaking views."),
    "Mount Bisoke": ("Northern Rwanda", "Climb a volcano to see a stunning crater lake and rugged terrain."),
    "Congo Nile Trail": ("Western Rwanda", "Cycle or hike along Lake Kivu with scenic villages and landscapes."),
    "Lake Kivu": ("Western Rwanda", "Enjoy boating and relaxation on one of Africa’s great lakes."),
    "Lake Muhazi": ("Eastern Rwanda", "A serene lake perfect for fishing and bird watching."),
    "Lake Ihema": ("Eastern Rwanda, Akagera", "Boat tours with hippos and crocodiles in a wildlife-rich setting."),
    "Lake Rweru": ("Northern Rwanda", "Quiet waters with scenic beauty and fishing opportunities."),
    "Lake Burera": ("Northern Rwanda", "Canoe among volcanic views and tranquil waters."),
    "Lake Ruhondo": ("Northern Rwanda", "A peaceful lake with boat trips and natural beauty."),
    "Nyamata Church": ("Near Kigali", "A genocide memorial site offering historical reflection."),
    "Murambi Memorial": ("Southern Rwanda", "A stark reminder of the genocide with preserved history."),
    "Camp Kigali Memorial": ("Kigali", "Honors Belgian peacekeepers with historical significance."),
    "Kigali City": ("Kigali", "Savor local cuisine and vibrant markets in the capital."),
    "Repub Lounge (Kigali)": ("Kigali", "Upscale dining with cocktails and a lively atmosphere."),
    "Rubavu": ("Western Rwanda, Lake Kivu", "Fresh fish and lakefront dining."),
    "Huye": ("Southern Rwanda", "Traditional meals with a cultural market vibe."),
    "Musanze": ("Northern Rwanda", "Fresh local dishes near volcanic landscapes."),
    "Nyungwe (Nearby Villages)": ("Southwestern Rwanda", "Authentic village food and traditions.")
}

# Dash layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Rwanda Tourism Planner", className="text-center my-4"), width=12)
    ]),
    dbc.Tabs([
        dbc.Tab(label="Recommendations", children=[
            dbc.Row([
                dbc.Col([
                    html.Label("Full Name:", className="form-label"),
                    dcc.Input(id="name", type="text", placeholder="Enter your full name", className="form-control mb-3"),
                    
                    html.Label("Email:", className="form-label"),
                    dcc.Input(id="email", type="email", placeholder="Enter your email", className="form-control mb-3"),
                    
                    html.Label("Age:", className="form-label"),
                    dcc.Input(id="age", type="number", placeholder="Enter your age", className="form-control mb-3"),
                    
                    html.Label("Departure Date:", className="form-label"),
                    dcc.DatePickerSingle(id="depart-date", className="mb-3"),
                    
                    html.Label("Return Date:", className="form-label"),
                    dcc.DatePickerSingle(id="return-date", className="mb-3"),
                    
                    html.Label("Select Experience Type:", className="form-label"),
                    dcc.Dropdown(id="experience", options=[{"label": k, "value": k} for k in experiences.keys()], placeholder="Select an experience", className="mb-3"),
                    
                    html.Div(id="activity-checklist", className="mb-3"),
                    
                    dbc.Button("Get Recommendation", id="recommend-button", color="primary", className="mb-3"),
                    
                    html.Div(id="recommendation-output", className="mb-3"),
                    
                    html.Div(id="booking-output")
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="score-plot", className="mb-3")
                ], width=6)
            ])
        ]),
        dbc.Tab(label="Direct Booking", children=[
            dbc.Row([
                dbc.Col([
                    html.Label("Full Name:", className="form-label"),
                    dcc.Input(id="direct-name", type="text", placeholder="Enter your full name", className="form-control mb-3"),
                    
                    html.Label("Email:", className="form-label"),
                    dcc.Input(id="direct-email", type="email", placeholder="Enter your email", className="form-control mb-3"),
                    
                    html.Label("Age:", className="form-label"),
                    dcc.Input(id="direct-age", type="number", placeholder="Enter your age", className="form-control mb-3"),
                    
                    html.Label("Departure Date:", className="form-label"),
                    dcc.DatePickerSingle(id="direct-depart-date", className="mb-3"),
                    
                    html.Label("Return Date:", className="form-label"),
                    dcc.DatePickerSingle(id="direct-return-date", className="mb-3"),
                    
                    html.Label("Select Destination:", className="form-label"),
                    dcc.Dropdown(id="direct-destination", options=[{"label": k, "value": k} for k in destination_info.keys()], placeholder="Select a destination", className="mb-3"),
                    
                    dbc.Button("Book Now", id="direct-book-button", color="success", className="mb-3"),
                    
                    html.Div(id="direct-booking-output")
                ], width=6)
            ])
        ])
    ])
], fluid=True)

# Callbacks
@app.callback(
    Output("activity-checklist", "children"),
    Input("experience", "value")
)
def update_activities(experience):
    if not experience:
        return []
    
    all_activities = set()
    for activities in experiences[experience]["destinations"].values():
        all_activities.update(activities)
    
    return [dbc.Checklist(
        id="activities",
        options=[{"label": act, "value": act} for act in all_activities],
        value=[],
        className="mb-3"
    )]

@app.callback(
    Output("recommendation-output", "children"),
    Output("score-plot", "figure"),
    Input("recommend-button", "n_clicks"),
    State("name", "value"),
    State("email", "value"),
    State("age", "value"),
    State("depart-date", "date"),
    State("return-date", "date"),
    State("experience", "value"),
    State("activities", "value")
)
def recommend_destination(n_clicks, name, email, age, depart_date, return_date, experience, selected_activities):
    if n_clicks == 0:
        return "", {}
    
    if not all([name, email, age, depart_date, return_date, experience, selected_activities]):
        return "Please fill in all fields and select at least one activity.", {}
    
    destinations = experiences[experience]["destinations"]
    best_match = None
    max_score = 0
    scores = {}
    
    for destination, activities in destinations.items():
        score = sum(1 for act in selected_activities if act in activities)
        weight = 1.0 + (0.3 if "National Park" in destination or "Memorial" in destination else 0) + \
                 (0.2 if "Kigali" in destination else 0)
        weighted_score = score * weight
        scores[destination] = weighted_score
        if weighted_score > max_score:
            max_score = weighted_score
            best_match = destination
    
    if best_match:
        location, desc = destination_info[best_match]
        match_count = sum(1 for act in selected_activities if act in destinations[best_match])
        recommendation_output = html.Div([
            html.H3(f"Recommended: {best_match}"),
            html.P(f"Location: {location}"),
            html.P(f"Experience: {desc}"),
            html.P(f"Matches: {match_count}/{len(selected_activities)}"),
            dbc.Button("Book Now", id="book-button", color="success", className="mt-3")
        ])
        
        # Create a bar plot
        df = pd.DataFrame({"Destination": list(scores.keys()), "Score": list(scores.values())})
        fig = px.bar(df, x="Destination", y="Score", title="Match Scores", color="Score", color_continuous_scale="Viridis")
        
        return recommendation_output, fig
    else:
        return "No suitable destination found.", {}

@app.callback(
    Output("booking-output", "children"),
    Input("book-button", "n_clicks"),
    State("name", "value"),
    State("email", "value"),
    State("age", "value"),
    State("depart-date", "date"),
    State("return-date", "date"),
    State("experience", "value"),
    State("activities", "value")
)
def create_booking(n_clicks, name, email, age, depart_date, return_date, experience, selected_activities):
    if n_clicks == 0:
        return ""
    
    if not all([name, email, age, depart_date, return_date, experience, selected_activities]):
        return "Please fill in all fields and select at least one activity."
    
    destinations = experiences[experience]["destinations"]
    best_match = None
    max_score = 0
    
    for destination, activities in destinations.items():
        score = sum(1 for act in selected_activities if act in activities)
        weight = 1.0 + (0.3 if "National Park" in destination or "Memorial" in destination else 0) + \
                 (0.2 if "Kigali" in destination else 0)
        weighted_score = score * weight
        if weighted_score > max_score:
            max_score = weighted_score
            best_match = destination
    
    if best_match:
        user_data = {
            "full_name": name,
            "email": email,
            "age": age,
            "departure_date": depart_date,
            "return_date": return_date,
            "destination": best_match,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Debug: Print user data
        print("User Data to be inserted:", user_data)
        
        # Save booking to database
        try:
            conn = sqlite3.connect("bookings.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (full_name, email, age, departure_date, return_date, destination, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_data["full_name"], user_data["email"], user_data["age"], user_data["departure_date"], user_data["return_date"], user_data["destination"], user_data["timestamp"]))
            conn.commit()
            conn.close()
            print("Booking successfully saved to the database.")
        except Exception as e:
            print("Error saving booking to the database:", e)
            return "An error occurred while saving your booking. Please try again."
        
        return html.Div([
            html.H3("Booking Confirmed"),
            html.P(f"Name: {user_data['full_name']}"),
            html.P(f"Email: {user_data['email']}"),
            html.P(f"Age: {user_data['age']}"),
            html.P(f"Departure: {user_data['departure_date']}"),
            html.P(f"Return: {user_data['return_date']}"),
            html.P(f"Destination: {user_data['destination']}"),
            html.P(f"Location: {destination_info[user_data['destination']][0]}"),
            html.P(f"Experience: {destination_info[user_data['destination']][1]}"),
            html.P(f"Timestamp: {user_data['timestamp']}")
        ])
    else:
        return "Booking failed. No suitable destination found."

@app.callback(
    Output("direct-booking-output", "children"),
    Input("direct-book-button", "n_clicks"),
    State("direct-name", "value"),
    State("direct-email", "value"),
    State("direct-age", "value"),
    State("direct-depart-date", "date"),
    State("direct-return-date", "date"),
    State("direct-destination", "value")
)
def direct_booking(n_clicks, name, email, age, depart_date, return_date, destination):
    if n_clicks == 0:
        return ""
    
    if not all([name, email, age, depart_date, return_date, destination]):
        return "Please fill in all fields to proceed with the booking."
    
    user_data = {
        "full_name": name,
        "email": email,
        "age": age,
        "departure_date": depart_date,
        "return_date": return_date,
        "destination": destination,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Debug: Print user data
    print("User Data to be inserted (Direct Booking):", user_data)
    
    # Save booking to database
    try:
        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (full_name, email, age, departure_date, return_date, destination, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_data["full_name"], user_data["email"], user_data["age"], user_data["departure_date"], user_data["return_date"], user_data["destination"], user_data["timestamp"]))
        conn.commit()
        conn.close()
        print("Direct Booking successfully saved to the database.")
    except Exception as e:
        print("Error saving direct booking to the database:", e)
        return "An error occurred while saving your booking. Please try again."
    
    return html.Div([
        html.H3("Booking Confirmed"),
        html.P(f"Name: {user_data['full_name']}"),
        html.P(f"Email: {user_data['email']}"),
        html.P(f"Age: {user_data['age']}"),
        html.P(f"Departure: {user_data['departure_date']}"),
        html.P(f"Return: {user_data['return_date']}"),
        html.P(f"Destination: {user_data['destination']}"),
        html.P(f"Location: {destination_info[user_data['destination']][0]}"),
        html.P(f"Experience: {destination_info[user_data['destination']][1]}"),
        html.P(f"Timestamp: {user_data['timestamp']}")
    ])

# Run the app
if __name__ == "__main__":
    app.run(debug=True)