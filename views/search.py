from flask import Blueprint, flash, redirect, request, render_template, url_for, current_app
import requests
from sql.db import DB
from flask_login import login_required, current_user
from datetime import timedelta
search = Blueprint('search', __name__)

@search.route('/search', methods=['GET','POST'])
@login_required
def searchSpotify():
    data=[]
    searchFor = ""
    entities = []
    users=[]
    if request.method == "POST":
        searchUrl = "https://spotify81.p.rapidapi.com/search"
        searchString = request.form.get('search')
        searchFor = request.form.get('artists') if request.form.get('artists') else request.form.get('tracks')
        if not searchString:
            flash("Enter a search query","danger")
        elif not searchFor:
            flash("Choose either Artists or Tracks","danger")
        querystring = {"q":searchString,"type":searchFor,"offset":"0","limit":"20","numberOfTopResults":"5"}
        headers = {
            "X-RapidAPI-Key": current_app.api_key,
            "X-RapidAPI-Host": current_app.api_host
        }

        response = requests.request("GET", searchUrl, headers=headers, params=querystring)
        output = response.json()
        if request.form.get('artists'):
            results = output["artists"]["items"]
            for r in results:
                spotifyUrl = r["data"]["uri"]
                artistName = r["data"]["profile"]["name"]
                image = r["data"]["visuals"]["avatarImage"]
                if image:
                    imageUrl = image["sources"][0]["url"]
                else:
                    imageUrl = "No Image"
                searchProfile = {"image":imageUrl,"artistName":artistName,"spotifyUrl":spotifyUrl}
                data.append(searchProfile)
        elif request.form.get('tracks'):
            results = output["tracks"]
            for r in results:
                spotifyUrl = r["data"]["uri"]
                spotifyId = r["data"]["id"]
                trackName = r["data"]["name"]
                albumName = r["data"]["albumOfTrack"]["name"]
                shortenedAlbumName = None
                if len(albumName) >=12:
                    shortenedAlbumName = albumName[:12]+'...'
                albumUrl = r["data"]["albumOfTrack"]["uri"]
                artistUrl = r["data"]["artists"]["items"][0]["uri"]
                artistName = r["data"]["artists"]["items"][0]["profile"]["name"]
                millisecondduration = str(timedelta(milliseconds=int(r["data"]["duration"]["totalMilliseconds"])))
                duration = millisecondduration[:millisecondduration.rfind('.')]
                searchTrack = {"spotifyUrl":spotifyUrl,"spotifyId":spotifyId,"trackName":trackName,"albumName":albumName,
                                "shortenedAlbumName":shortenedAlbumName,"albumUrl":albumUrl, "artistUrl":artistUrl,
                                "artistName":artistName,"duration":duration}
                data.append(searchTrack)
    else:
        try:
            result = DB.selectAll("""select e.name from IS601_User_Entities ue join IS601_Entities e on e.id = ue.entity_id
                                    and e.is_active = 1 where ue.user_id = %s and ue.is_active=1""", current_user.get_id())
            if result.status:
                entities=result.rows
            if not entities:
                flash("No associations available for the user. \
                        Contact system administrator to add associations.", "danger")
        except Exception as e:
            e = "Error retrieving user associations. Try again."
            flash(e, "danger")
    try:
        result = DB.selectAll("select u.id, u.username from IS601_Users u")
        if result.status:
            users=result.rows
    except Exception as e:
        flash("Error retrieving users.", "danger")
    return render_template("search.html", args=data, type=searchFor, rows=entities, users=users)