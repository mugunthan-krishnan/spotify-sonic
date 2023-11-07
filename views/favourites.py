from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user

from sql.db import DB
favourites = Blueprint('favourites', __name__, url_prefix="/favourites")

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The artists function is used to display the artists favourited. The results are listed as a table.
            The filter fields are Artist Name, Genre, Record Type, Sort Column, Order and Limit are used to
            filter results. The user is displayed success and error messages on query failure and
            query success.
"""

@favourites.route('/artists', methods=['GET', 'POST'])
@login_required
def artists():
    rows=[]
    filter = {}
    filter["userid"] = current_user.get_id()
    allowed_columns = ["artist_name","genre","record_type"]
    type="artists"

    query=f"""select id, imageUrl as image, name as Artist_Name, genre as Genre, spotifyUrl as Spotify_Profile
            , case when customartist=1 then 'Custom' else 'API' end as record_type from IS601_User_Artists
            where userid = {filter['userid']}"""

    artistName = request.args.get('artist_name')
    genre = request.args.get('genre')
    rtype = request.args.get('rtype')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    
    filter["artist_name"] = artistName
    filter["genre"] = genre
    filter["rtype"] = rtype
    
    if artistName:
        query += f" and name like '%%{filter['artist_name']}%%'"
    if genre:
        query += f" and genre like '%%{filter['genre']}%%'"
    if filter["rtype"] == "api":
        query += f" and customartist=0"
    elif filter["rtype"] == "custom":
        query += f" and customartist=1"
    
    if column and order:
        filter["column"] = column
        filter["order"] = order
        if column in allowed_columns and order in ["asc", "desc"]:
            query += f" order by {filter['column']} {filter['order']}"
    if not limit.isnumeric() or int(limit) < 1 or int(limit) > 100:
        flash("Limit filter must be a number between 1 and 100","danger")
    else:
        limit = int(limit)
    if limit and int(limit) > 0 and int(limit) <= 100:
        filter["limit"] = limit
        query += f" limit {filter['limit']}"
    try:
        result = DB.selectAll(query, filter)
        if result.status:
            rows = result.rows

    except Exception as e:
        print(e)
        e = "Artist records could not be retrieved due to an error. Try Again!"
        flash(str(e), "danger")

    allowed_columns = [("artist_name", "Artist Name"), ("genre", "Genre"), ("record_type", "Record Type")]
    rtypecols=[("api", "API"),("custom","Custom")]
    count=len(rows)
    return render_template("favartists.html", rows=rows, allowed_columns=allowed_columns, rtypecols=rtypecols, type=type, count=count)

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The tracks function is used to display the tracks favourited. The results are listed as a table.
            The filter fields are Track Name, Artist Name, Album Name, Record Type, Sort Column, Order and Limit
            are used to filter results. The user is displayed success and error messages on query failure and
            query success.
"""

@favourites.route('/tracks', methods=['GET', 'POST'])
@login_required
def tracks():
    rows=[]
    filter = {}
    filter["userid"] = current_user.get_id()
    allowed_columns = ["track_name","artist_name","album_name","duration","record_type"]
    type="tracks"

    query=f"""select id, name as Track_Name, artistname as Artist_Name, albumname as Album_Name, albumurl, duration
            , case when customtrack=1 then 'Custom' else 'API' end as record_type from IS601_User_Tracks
            where userid = {filter['userid']}"""

    trackName = request.args.get('track_name')
    artistName = request.args.get('artist_name')
    albumName = request.args.get('album_name')
    rtype = request.args.get('rtype')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    
    filter["track_name"] = trackName
    filter["artist_name"] = artistName
    filter["album_name"] = albumName
    filter["rtype"] = rtype
    
    if trackName:
        query += f" and name like '%%{filter['track_name']}%%'"
    if artistName:
        query += f" and artistname like '%%{filter['artist_name']}%%'"
    if albumName:
        query += f" and albumname like '%%{filter['album_name']}%%'"
    if filter["rtype"] == "api":
        query += f" and customartist=0"
    elif filter["rtype"] == "custom":
        query += f" and customartist=1"
    
    if column and order:
        filter["column"] = column
        filter["order"] = order
        if column in allowed_columns and order in ["asc", "desc"]:
            query += f" order by {filter['column']} {filter['order']}"
    if not limit.isnumeric() or int(limit) < 1 or int(limit) > 100:
        flash("Limit filter must be a number between 1 and 100","danger")
    else:
        limit = int(limit)
    if limit and int(limit) > 0 and int(limit) <= 100:
        filter["limit"] = limit
        query += f" limit {filter['limit']}"
    try:
        result = DB.selectAll(query, filter)
        if result.status:
            rows = result.rows

    except Exception as e:
        print(e)
        e = "Artist records could not be retrieved due to an error. Try Again!"
        flash(str(e), "danger")

    allowed_columns = [("track_name","Track"),("artist_name","Artist"),("album_name","Album"),("duration","Duration")
                        ,("record_type","Record Type")]
    rtypecols=[("api", "API"),("custom","Custom")]
    count=len(rows)
    return render_template("favtracks.html", rows=rows, allowed_columns=allowed_columns, rtypecols=rtypecols, type=type, count=count)

"""
    UCID:   mk2246
    Date:   05/04/2023
    Desc:   The delete favourites function is used to delete all favourites associated
            to the user. Data is deleted from IS601_User_Artists or IS601_User_Tracks tables
            based on the selection. The user is displayed success and error messages on query
            failure and query success.
"""

@favourites.route('/delete', methods=['GET','POST'])
@login_required
def deletefavourites():
    if request.method == "POST":
        clearall = request.form.get('clearall')
        type=request.args.get("type")
        if type == "artists":
            query = "delete from IS601_User_Artists ua where ua.userid = %s"
        else:
            query="delete from IS601_User_Tracks ut where ut.userid = %s"
        if clearall and type:
            try:
                clearresult=DB.update(query, current_user.get_id())
                if clearresult.status:
                    flash("Removed all favorites.","success")
            except Exception as e:
                print(e)
                flash("Error removing favorites.","danger")
    if type == "artists":
        return redirect(url_for("favourites.artists"))
    else:
        return redirect(url_for("favourites.tracks"))

@favourites.route('/listartistsfavsummary', methods=['GET','POST'])
@login_required
def listartistsfavourites():
    rows=[]
    filter = {}
    allowed_columns = ["artist_name","Number_of_users"]

    query=f"""select ua.name as Artist_Name,
            case when ua.userid = null then 0 else count(ua.userid) end as Number_of_users
            from IS601_User_Artists ua where 1=1"""

    artist_name = request.args.get('artist_name')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    no_of_users = request.args.get("no_users")
    operation = request.args.get("operation")
    
    filter["artist_name"] = artist_name
    filter["no_of_users"] = no_of_users
    filter["operation"] = operation

    if artist_name:
        query += f" and ua.name like '%%{filter['artist_name']}%%'"
    
    query += " group by Artist_Name, ua.userid"
    
    if no_of_users:
        query += f" having Number_of_users {filter['operation']} {filter['no_of_users']}"

    if column and order:
        filter["column"] = column
        filter["order"] = order
        if column in allowed_columns and order in ["asc", "desc"]:
            query += f" order by {filter['column']} {filter['order']}"
    if not limit.isnumeric() or int(limit) < 1 or int(limit) > 100:
        flash("Limit filter must be a number between 1 and 100","danger")
    else:
        limit = int(limit)
    if limit and int(limit) > 0 and int(limit) <= 100:
        filter["limit"] = limit
        query += f" limit {filter['limit']}"
    
    try:
        result = DB.selectAll(query, filter)
        if result.status:
            rows=result.rows
    except Exception as e:
        flash("Error retrieving tracks for the user. Try again.", "danger")
    allowed_columns = [("Artist_Name", "Artist Name"), ("Number_of_users", "Number of users")]
    return render_template("listartistsfavsummary.html",rows=rows, allowed_columns=allowed_columns)

@favourites.route('/listtracksfavsummary', methods=['GET','POST'])
@login_required
def listtracksfavourites():
    rows=[]
    filter = {}
    filter["userid"] = current_user.get_id()
    allowed_columns = ["name","artist_name","Number_of_users"]

    query=f"""select ut.name, ut.artistname as Artist_Name,
            case when ut.userid = null then 0 else count(ut.userid) end as Number_of_users
            from IS601_User_Tracks ut where 1=1"""

    track_name = request.args.get('track_name')
    artist_name = request.args.get('artist_name')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    no_of_users = request.args.get("no_users")
    operation = request.args.get("operation")

    filter["track_name"] = track_name
    filter["artist_name"] = artist_name
    filter["no_of_users"] = no_of_users
    filter["operation"] = operation

    if track_name:
        query += f" and ut.name like '%%{filter['track_name']}%%'"
    if artist_name:
        query += f" and ut.artistname like '%%{filter['artist_name']}%%'"
    
    query += " group by ut.name, Artist_Name, ut.userid"
    
    if no_of_users:
        query += f" having Number_of_users {filter['operation']} {filter['no_of_users']}"

    if column and order:
        filter["column"] = column
        filter["order"] = order
        if column in allowed_columns and order in ["asc", "desc"]:
            query += f" order by {filter['column']} {filter['order']}"
    if not limit.isnumeric() or int(limit) < 1 or int(limit) > 100:
        flash("Limit filter must be a number between 1 and 100","danger")
    else:
        limit = int(limit)
    if limit and int(limit) > 0 and int(limit) <= 100:
        filter["limit"] = limit
        query += f" limit {filter['limit']}"
    
    try:
        result = DB.selectAll(query, filter)
        if result.status:
            rows=result.rows
    except Exception as e:
        print(e)
        flash("Error retrieving tracks for the user. Try again.", "danger")
    allowed_columns = [("name", "Track Name"), ("artist_name", "Artist Name"), ("Number_of_users", "Number of users")]
    return render_template("listtracksfavsummary.html",rows=rows, allowed_columns=allowed_columns)

@favourites.route('/deleteuserfav', methods=['GET','POST'])
@login_required
def deleteuserfavourites():
    artistrows=[]
    trackrows=[]

    if request.method == "POST":
        delartist = request.form.get("delartist")
        deltrack = request.form.get("deltrack")

        if delartist:
            artistuserid = request.args.get('artistuserid')
            artistid = request.args.get('artistid')
            try:
                result=DB.delete("""delete from IS601_User_Artists where userid=%s and id=%s""", artistuserid, artistid)
                if result.status:
                    flash("Successfully deleted artist for user.", "success")
            except Exception as e:
                flash("Error deleting artist for user.","danger")
        
        if deltrack:
            trackuserid = request.args.get('trackuserid')
            trackid = request.args.get('trackid')
            try:
                result=DB.delete("""delete from IS601_User_Tracks where userid=%s and id=%s""", trackuserid, trackid)
                if result.status:
                    flash("Successfully deleted track for user.", "success")
            except Exception as e:
                flash("Error deleting track for user.","danger")
    try:
        artists = DB.selectAll("""select ua.userid, ua.id, ua.name as Artist_Name, ua.genre
                                from IS601_User_Artists ua""")
        if artists.status:
            artistrows=artists.rows
    except Exception as e:
        flash("Error retrieving favourite artists.","danger")

    try:
        tracks = DB.selectAll("""select ut.userid, ut.id, ut.name as Track_Name, ut.duration
                                from IS601_User_Tracks ut""")
        if tracks.status:
            trackrows=tracks.rows
    except Exception as e:
        flash("Error retrieving favourite tracks.","danger")
    return render_template("admin_delete_favourite.html", artistrows=artistrows, trackrows=trackrows)