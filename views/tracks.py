from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import login_required, current_user
import re
from sql.db import DB
tracks = Blueprint('tracks', __name__, url_prefix="/favourites/tracks")

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The view tracks function is used to view the track chosen to view.
            The records are retrieved from the IS601_User_Tracks table and displayed as
            readonly fields in a form. The user is displayed success and error messages
            on query failure and query success.
"""

@tracks.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    row=[]
    id=request.args.get("id")
    type=request.args.get("type")
    if not id:
        flash("ID is missing. Try again.", "danger")
        return redirect("favourites.tracks")
    else:
        try:
            result=DB.selectOne("""select name, artistname, albumname, albumUrl, duration from IS601_User_Tracks where id=%s
                                and userid=%s""",id,current_user.get_id())
            row=result.row
            if not result.row:
                flash("No record of the track available","warning")
        except Exception as e:
            e = "An error occurred when viewing the track. Try again."
            flash(str(e), "danger")
    
    return render_template('viewfavourite.html', row=row, type=type)

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The edit tracks function is used to edit the track chosen to edit.
            The records are retrieved from the IS601_User_Tracks table and displayed as
            fields in a form. The user can edit the fields and submit the form. The user
            is displayed success and error messages on query failure and query success.
"""

@tracks.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    row=[]
    id=request.args.get("id")
    type=request.args.get("type")
    if not id:
        flash("ID is missing. Try again.", "danger")
        return redirect("favourites.tracks")
    else:
        if request.method == "POST":
            trackName = request.form.get("name")
            artistName = request.form.get("artist_name")
            albumName = request.form.get("album_name")
            albumUrl = request.form.get("album_url")
            duration = request.form.get("duration")
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
        
            if trackName and duration and artistName and durationFlag:
                try:
                    result=DB.update("""update IS601_User_Tracks set name=%s, artistname=%s, albumname=%s, albumurl=%s
                                        , duration=%s where id=%s and userid=%s""",trackName,artistName,albumName,albumUrl
                                        ,duration,id,current_user.get_id())
                    row=result.row
                    if result.status:
                        flash("Track updated sucessfully","success")
                except Exception as e:
                    e = "An error occurred when editing the track. Try again."
                    flash(str(e), "danger")
            
    try:
        result=DB.selectOne("""select name, artistname, albumname, albumurl, duration from IS601_User_Tracks where id=%s
                            and userid=%s""",id,current_user.get_id())
        row=result.row
        if not result.row:
            flash("No record of the track available","warning")
    except Exception as e:
        e = "An error occurred when retrieving the track. Try again."
        flash(str(e), "danger")
    return render_template('editfavourite.html', row=row, type=type)

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The delete track function is used to delete the track from favourites.
            The user is displayed success and error messages on query failure and
            query success.
"""

@tracks.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    id = request.args.get("id")
    if not id:
        flash("ID is missing!", "danger")
        return redirect(url_for("favourites.tracks"))
    else:
        args = {**request.args}
        if id:
            try:
                result = DB.delete("DELETE FROM IS601_User_Tracks WHERE id = %s", id)
                if result.status:
                    flash("Removed track from favourites", "success")
            except Exception as e:
                e = "Track could not be removed from favourites due to an error"
                flash(str(e), "danger")
            del args["id"]
    return redirect(url_for('favourites.tracks', **args))