from flask import Blueprint, flash, redirect, request, render_template, url_for, current_app
import requests
import re
from sql.db import DB
from flask_login import login_required, current_user
addviewfav = Blueprint('addviewfav', __name__)

"""
    UCID:   mk2246
    Date:   04/23/2023
    Desc:   The add function is to add api data to the database. It takes the arguments from the jinja template
            and inserts the data to the IS601_User_Artists and IS601_User_Tracks tables. Duplicate records are
            checked against the database and error message is displayed if an existing record is added again.
            A success or failure message shown to the user. The api is called using the erquests library and
            based on the search criteria provided by the user, either artist or track is displayed with the
            ability to view or add the corresponding item.
"""

@addviewfav.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == "POST":
        if request.args.get("type") == "artists":
            spotifyid = request.args.get("url")
            spotifyid = spotifyid[spotifyid.rfind(':')+1:]
            spotifyurl = request.args.get("url")
            artistImageUrl = request.args.get("img")
            artistName = request.args.get("name")
            genre=""
            artisturl = "https://spotify81.p.rapidapi.com/artists"

            querystring = {"ids":spotifyid}

            headers = {
                "X-RapidAPI-Key": current_app.api_key,
                "X-RapidAPI-Host": current_app.api_host
            }

            response = requests.request("GET", artisturl, headers=headers, params=querystring)
            if request.form.get('addtouser'):
                userid=request.form.get('userdropdown')
            if request.form.get('add'):
                userid=current_user.get_id()
                print(userid, type(userid))
            if response:
                output = response.json()
                genres = output["artists"][0]["genres"]
                for g in genres:
                    genre = genre+","+g
                genre = genre[1:]
            try:
                result = DB.selectOne("select spotifyid from IS601_User_Artists where spotifyid=%s and userid=%s",spotifyid,userid)
                if result.row:
                    flash("Artist already present in favourites","danger")
                    return redirect(url_for("search.searchSpotify"))
                else:
                    try:
                        result = DB.insertOne("""insert into IS601_User_Artists(userid, spotifyid, customartist, name
                                                , genre, spotifyUrl, imageUrl, is_active) values(%s,%s,0,%s,%s,%s,%s,1)
                                                """, userid,spotifyid,artistName,genre,spotifyurl,artistImageUrl)
                        if result.status:
                            flash("Artist added to favourites","success")
                    except Exception as e:
                        print("1st",e)
                        e = "An error occurred when adding artist to favourites. Try again."
                        flash(str(e), "danger")
            except Exception as e:
                print("2nd",e)
                e = "An error occurred when adding artist to favourites. Try again."
                flash(str(e), "danger")
                
        else:
            spotifyid = request.args.get("spotifyId")
            artistName = request.args.get("artistName")
            trackName = request.args.get("trackName")
            albumUrl = request.args.get("albumUrl")
            albumName = request.args.get("albumName")
            duration = request.args.get("duration")
            if request.form.get('addtouser'):
                userid=request.form.get('userdropdown')
            if request.form.get('add'):
                userid=current_user.get_id()
            try:
                result = DB.selectOne("select spotifyid from IS601_User_Tracks where spotifyid=%s and userid=%s",spotifyid,userid)
                if result.row:
                    flash("Track already present in favourites","danger")
                    return redirect(url_for("search.searchSpotify"))
                else:
                    try:
                        result = DB.insertOne("""insert into IS601_User_Tracks(userid, spotifyid, customtrack, name
                                                , artistname, albumurl, albumname, duration, is_active) values(%s,%s,0,%s,%s,%s,%s,%s,1)
                                                """, userid,spotifyid,trackName,artistName,albumUrl,albumName,duration)
                        if result.status:
                            flash("Track added to favourites","success")
                    except Exception as e:
                        e = "An error occurred when adding track to favourites. Try again."
                        flash(str(e), "danger")
            except Exception as e:
                e = "An error occurred when adding track to favourites. Try again."
                flash(str(e), "danger")

    return redirect(url_for("search.searchSpotify"))

"""
    UCID:   mk2246
    Date:   04/23/2023
    Desc:   The addcustomartist function is to add custom data to the database. It takes the arguments from the jinja template
            and inserts the data to the IS601_User_Artists table. Duplicate records are checked against the database and error
            message is displayed if an existing record is added again. A success or failure message shown to the user.
"""

@addviewfav.route('/addcustomartists', methods=['GET','POST'])
@login_required
def addcustomartist():
    data = {}
    if request.method == "POST":
        artistName = request.form.get("artist_name", None)
        genre = request.form.get("genre", None)
        data["artist_name"] = artistName
        data["genre"] = genre
        if not artistName:
            flash("Enter an artist name", "danger")
        elif not genre:
            flash("Enter genre(s) for the artist", "danger")
        
        userid=current_user.get_id()
        if artistName and genre:
            try:
                result = DB.selectOne("""select userid,name, genre from IS601_User_Artists where userid=%s and lower(name) = %s
                                        and lower(genre) = %s and is_active=1""",userid,artistName.lower(),genre.lower())
                if result.row:
                    flash("Artist already present in favourites","danger")
                else:
                    try:
                        result = DB.insertOne("""insert into IS601_User_Artists(userid, spotifyid, customartist, name, genre, is_active)
                                            values(%s,99,1,%s,%s,1)""",userid,artistName,genre)
                        if result.status:
                            flash("Artist added successfully","success")
                    except Exception as e:
                        e = "An error occurred adding artist to favourites. Try again."
                        flash(str(e), "danger")

            except Exception as e:
                e = "An error occurred adding artist to favourites. Try again."
                flash(str(e), "danger")
    
    return redirect(url_for("search.searchSpotify"))

"""
    UCID:   mk2246
    Date:   04/23/2023
    Desc:   The addcustomtrack function is to add custom data to the database. It takes the arguments from the jinja template
            and inserts the data to the IS601_User_Tracks table. Duplicate records are checked against the database and error
            message is displayed if an existing record is added again.  A success or failure message shown to the user.
"""

@addviewfav.route('/addcustomtracks', methods=['GET','POST'])
@login_required
def addcustomtrack():
    data = {}
    if request.method == "POST":
        trackName = request.form.get("track_name", None)
        duration = request.form.get("duration", None)
        albumName = request.form.get("album_name", None)
        artistName = request.form.get("artist_name", None)
        
        if not trackName:
            flash("Enter a track name", "danger")
        elif not duration:
            flash("Enter duration of the track", "danger")
        elif not artistName:
            flash("Enter an artist name for the track", "danger")
        elif not re.match('^[0-9]*:[0-9]{2}:[0-9]{2}$', duration):
            flash("Invalid duration format. Example - 0:04:55","danger")
            durationFlag = False
        else:
            durationFlag = True
        data["track_name"] = trackName
        data["duration"] = duration
        data["album_name"] = albumName
        data["artist_name"] = artistName
        userid=current_user.get_id()
        if trackName and duration and artistName and durationFlag:
            try:
                result = DB.selectOne("""select userid, customtrack, name, artistname, albumname, duration from IS601_User_Tracks
                                        where userid=%s and lower(name)=%s and lower(artistname)=%s and albumname=%s and 
                                        lower(duration)=%s and is_active=1""",userid,trackName.lower()
                                        ,artistName.lower(),albumName.lower(),duration.lower())
                if result.row:
                    flash("Track already present in favourites","danger")
                    return redirect(url_for("search.searchSpotify"))
                else:
                    try:
                        result = DB.insertOne("""insert into IS601_User_Tracks(userid, customtrack, name, artistname, albumname, duration
                                            , is_active) values(%s,1,%s,%s,%s,%s,1)""",userid,trackName,artistName,albumName
                                            ,duration)
                        if result.status:
                            flash("Track added successfully","success")
                    except Exception as e:
                        e = "An error occurred adding track to favourites. Try again."
                        flash(str(e), "danger")
            except Exception as e:
                e = "An error occurred adding track to favourites. Try again."
                flash(str(e), "danger")
    
    return redirect(url_for("search.searchSpotify"))