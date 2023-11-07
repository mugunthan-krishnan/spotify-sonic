from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import login_user, login_required, logout_user, current_user

from sql.db import DB
artist = Blueprint('artist', __name__, url_prefix="/favourites/artist")

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The view artists function is used to view the artist chosen to view.
            The records are retrieved from the IS601_User_Artists table and displayed as
            readonly fields in a form. The user is displayed success and error messages
            on query failure and query success.
"""

@artist.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    row=[]
    id=request.args.get("id")
    type=request.args.get("type")
    if not id:
        flash("ID is missing. Try again.", "danger")
        return redirect("favourites.artists")
    else:
        try:
            result=DB.selectOne("""select name, genre, spotifyUrl, imageUrl from IS601_User_Artists where id=%s
                                and userid=%s""",id,current_user.get_id())
            row=result.row
            if not result.row:
                flash("No record of the artist available","warning")
        except Exception as e:
            e = "An error occurred when viewing the artist. Try again."
            flash(str(e), "danger")
    return render_template('viewfavourite.html', row=row, type=type)

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The edit artists function is used to edit the artist chosen to edit.
            The records are retrieved from the IS601_User_Artists table and displayed as
            fields in a form. The user can edit the fields and submit the form. The user
            is displayed success and error messages on query failure and query success.
"""

@artist.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    row=[]
    id=request.args.get("id")
    type=request.args.get("type")
    if not id:
        flash("ID is missing. Try again.", "danger")
        return redirect("favourites.artists")
    else:
        if request.method == "POST":
            trackName = request.form.get("name")
            spotifyUrl = request.form.get("spotifyurl")
            imageUrl = request.form.get("imageurl")
            artistName = request.form.get("artist_name", None)
            genre = request.form.get("genre", None)
            if not artistName:
                flash("Enter an artist name", "danger")
            elif not genre:
                flash("Enter genre(s) for the artist", "danger")
        
            if artistName and genre:
                try:
                    result=DB.update("""update IS601_User_Artists set name=%s, genre=%s, spotifyUrl=%s, imageUrl=%s 
                                        where id=%s and userid=%s""",artistName,artistName,spotifyUrl,imageUrl
                                        ,id,current_user.get_id())
                    row=result.row
                    if result.status:
                        flash("Artist updated sucessfully","success")
                except Exception as e:
                    e = "An error occurred when editing the artist. Try again."
                    flash(str(e), "danger")
            
    try:
        result=DB.selectOne("""select name, genre, spotifyUrl, imageUrl from IS601_User_Artists where id=%s
                                and userid=%s""",id,current_user.get_id())
        row=result.row
        if not result.row:
            flash("No record of the artist available","warning")
    except Exception as e:
        e = "An error occurred when retrieving the artist. Try again."
        flash(str(e), "danger")
    return render_template('editfavourite.html', row=row, type=type)

"""
    UCID:   mk2246
    Date:   04/24/2023
    Desc:   The delete artists function is used to delete the artist from favourites.
            The user is displayed success and error messages on query failure and
            query success.
"""

@artist.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    id = request.args.get("id")
    if not id:
        flash("ID is missing!", "danger")
        return redirect(url_for("favourites.artists"))
    else:
        args = {**request.args}
        if id:
            try:
                result = DB.delete("DELETE FROM IS601_User_Artists WHERE id = %s", id)
                if result.status:
                    flash("Removed artist from favourites", "success")
            except Exception as e:
                e = "Artist could not be removed from favourites due to an error"
                flash(str(e), "danger")
            del args["id"]
    return redirect(url_for('favourites.artists', **args))