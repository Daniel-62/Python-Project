import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.messagebox
import webbrowser
import random
import requests
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "api.mubi.com",
    "Referer": "https://mubi.com/",
    "Origin": "https://mubi.com",
    "ANONYMOUS_USER_ID": "73390b23-1c05-43d6-a209-91bbf0348ae5",
    "CLIENT": "web",
    "Client-Accept-Audio-Codecs": "aac",
    "Client-Accept-Video-Codecs": "vp9,h264",
    "Client-Country": "GB",
}

def change_anonymous_user_id(headers, new_digit):
    if not (0 <= new_digit <= 9):
        raise ValueError("new_digit must be a single digit between 0 and 9.")
    anonymous_id = headers["ANONYMOUS_USER_ID"]
    updated_id = str(new_digit) + anonymous_id[1:]
    headers["ANONYMOUS_USER_ID"] = updated_id
    return headers

new_digit = random.randint(0, 9)
headers = change_anonymous_user_id(headers, new_digit)

def mubi_get_movies():
    movies_dict = {
        "title": [],
        "genre": [],
        "short description": [],
        "year": [],
        "duration": [],
        "trailer_url": [],
    }

    url = "https://api.mubi.com/v3/browse/films?sort=popularity_quality_score"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        total_movies = response.json()["meta"]["total_pages"]
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {}
    

    for page in tqdm(range(1, 50)):  # change 50 with total_movies
        url_page = f"https://api.mubi.com/v3/browse/films?sort=popularity_quality_score&page={page}"

        response_total = requests.get(url_page, headers=headers, verify=False)

        website_films = response_total.json()["films"]

        for item in website_films:
            movies_dict["title"].append(item["original_title"])
            movies_dict["genre"].append(", ".join(item.get("genres", [])))
            movies_dict["short description"].append(item["short_synopsis"])
            movies_dict["year"].append(item["year"])
            movies_dict["duration"].append(item["duration"])
            movies_dict["trailer_url"].append(item["trailer_url"])

    return movies_dict

def selectgenre(movies_dict):
    unique_genres = set()
    
    for genre_str in movies_dict["genre"]:
        genres = [genre.strip() for genre in genre_str.split(",")]
        unique_genres.update(genres)
    return sorted(unique_genres)

def open_trailer(event, trailer_url):
    if trailer_url:
        webbrowser.open(trailer_url)

def display_movie_details(movie_details):
    # frame for movie details
    details_frame = tk.Frame(app, bg="black", bd=2, relief=tk.SUNKEN)
    details_frame.place(relx=0.1, rely=0.4, relwidth=0.8, relheight=0.6)

    details_text = tk.Text(details_frame, wrap=tk.WORD, bg="white", fg="black", padx=10, pady=10, font=("Arial", 10), cursor="arrow")
    details_text.pack(expand=True, fill=tk.BOTH)

    # add the movie details
    details_text.insert(tk.END, f"Title: {movie_details['title']}\n")
    details_text.insert(tk.END, f"Genres: {movie_details['genre']}\n")
    details_text.insert(tk.END, f"Year: {movie_details['year']}\n")
    details_text.insert(tk.END, f"Duration: {movie_details['duration']} minutes\n\n")
    details_text.insert(tk.END, f"Description:\n{movie_details['short description']}\n\n")

    #insert the clickable link
    trailer_url = movie_details['trailer_url']
    if trailer_url and trailer_url != "N/A":
        details_text.insert(tk.END, "Trailer: ", "normal")
        details_text.insert(tk.END, trailer_url, "link")

        details_text.tag_configure("link", foreground="royalblue", underline=True)
        details_text.tag_bind("link", "<Button-1>", lambda event: open_trailer(event, trailer_url))
    else:
        details_text.insert(tk.END,"Trailer: No trailer for this movie.\n", "normal")

    details_text.config(state=tk.DISABLED)

def genre_filter(app, genres):
    filter_label = tk.Label(app, text="Select Genre:")
    filter_label.pack(pady=10)
    selected_genre = tk.StringVar()
    genre_dropdown = ttk.Combobox(app, textvariable=selected_genre, values=genres, state="readonly")
    genre_dropdown.pack(pady=10)
    return selected_genre


def pick_random_movie(movies_dict, genre):
    genre_movies = [
        {
            "title": movies_dict["title"][i],
            "genre": movies_dict["genre"][i],
            "short description": movies_dict["short description"][i],
            "year": movies_dict["year"][i],
            "duration": movies_dict["duration"][i],
            "trailer_url": movies_dict["trailer_url"][i],
        }
        for i in range(len(movies_dict["title"]))
        if genre in movies_dict["genre"][i]
    ]
    
    if genre_movies:
        return random.choice(genre_movies)
    return None

def pick_movie():
    random_movie = pick_random_movie(movies_dict, selected_genre.get())
    if random_movie:
        display_movie_details(random_movie)
    else:
        tkinter.messagebox.showinfo("No Movie Found", "No movie found for the selected genre.")


app = ttk.Window(themename="darkly")
app.title("Movie Picker")
app.geometry("800x400")

movies_dict = mubi_get_movies()

unique_genres = selectgenre(movies_dict)
selected_genre = genre_filter(app, unique_genres)

pick_button = ttk.Button(app, text="Pick Random Movie", bootstyle=PRIMARY, command=lambda: pick_movie())
pick_button.pack(pady=20)

app.mainloop()
