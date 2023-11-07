from flask import Blueprint, flash, redirect, request, render_template, url_for, current_app
from sql.db import DB
from flask_login import login_required, current_user
from roles.permissions import admin_permission
feature = Blueprint('feature', __name__)

@feature.route('/requestfeature', methods=['GET','POST'])
@login_required
def userrequest():
    if request.method == "POST":
        featuredesc = request.form.get("feature")
        if featuredesc:
            try:
                result = DB.insertOne("insert into IS601_Features(feature_desc) VALUES(%s)", featuredesc)
                if result.status:
                    flash("Successfully requested a new feature.","success")
            except Exception as e:
                flash("Error requesting a new feature. Try again.","danger")
    return render_template("requestfeature.html")

@feature.route('/requestedfeatures', methods=['GET','POST'])
@admin_permission.require(http_exception=403)
@login_required
def requestedfeatures():
    rows=[]
    try:
        result = DB.selectAll("select id, feature_desc as feature from IS601_Features")
        if result.status:
            rows=result.rows
    except Exception as e:
        flash("Error requesting a new feature. Try again.","danger")
    return render_template("featuresview.html", rows=rows)