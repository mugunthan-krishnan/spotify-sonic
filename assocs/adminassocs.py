from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB
from roles.forms import RoleForm
from werkzeug.datastructures import MultiDict
from roles.permissions import admin_permission
adminassoc = Blueprint('adminassoc', __name__, url_prefix='/adminassocs',template_folder='templates')

@adminassoc.route("/addassoc", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def addassoc():
    userrows=[]
    entityrows=[]
    if request.method == "POST":
        entity=request.form.get('entity')
        userid=request.args.get('userid')

        try:
            result = DB.selectOne("select id from IS601_User_Entities where user_id=%s and entity_id=%s", userid,entity)
            if result.row:
                flash("Entity already associated to user. Add a different entity.", "warning")
            else:
                try:
                    result=DB.insertOne("insert into IS601_User_Entities(user_id,entity_id) VALUES(%s,%s)"
                                        ,userid,entity)
                    if result.status:
                        flash("Successfully associated entity to user.","success")
                except Exception as e:
                    flash("Error adding entity to user. Try again.","danger")
        except Exception as e:
            flash("Error retrieving entities. Try again.","danger")

    try:
        result = DB.selectAll("""select id, username, email from IS601_Users""")
        userrows=result.rows
        if not userrows:
            flash("No users in the system to add associations. Register a user to add associations.","info")
            return redirect("add_assoc.html")
        try:
            entityresult = DB.selectAll("select id as entity_id, name from IS601_Entities where is_active=1")
            if entityresult.status:
                entityrows = entityresult.rows
        except Exception as e:
            flash("Error retrieving entities to add associations to users. Try again.", "danger")
    except Exception as e:
        flash("Error retrieving users to add associations. Try again.", "danger")
    return render_template("add_assoc.html", entityrows=entityrows, userrows=userrows)

@adminassoc.route("/listassoc", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def listassoc():
    rows=[]

    filter = {}
    allowed_columns = ["username","is_active"]

    query="""select u.id as userid, ue.entity_id, u.username, e.name
            , e.description, ue.is_active from IS601_User_Entities ue
            join IS601_Entities e on e.id = ue.entity_id
            join IS601_Users u on u.id=ue.user_id where 1=1"""

    is_active = request.args.get('is_active')
    name = request.args.get('username')
    description = request.args.get('description')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    
    filter["is_active"] = is_active
    filter["username"] = name
    filter['description'] = description
    
    if name:
        query += f" and u.username like '%%{filter['username']}%%'"
    if description:
        query += f" and e.description like '%%{filter['description']}%%'"
    if is_active:
        query += f" and ue.is_active = '%%{filter['is_active']}%%'"
    
    if column and order:
        filter["column"] = column
        filter["order"] = order
        if column in allowed_columns and order in ["asc", "desc"]:
            query += f" order by {filter['column']} {filter['order']}"

    if column and order:
        query += f", u.username"
    else:
        query += f" order by u.username"
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
        flash("Error retrieving users and associations. Try again.", "danger")
    allowed_columns = [("username", "Username"), ("is_active", "Active?")]
    return render_template("listassoc.html", rows=rows, allowed_columns=allowed_columns)

@adminassoc.route("/deleteassoc", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def delassoc():
    userid=request.args.get('userid')
    entity_id=request.args.get('entityid')
    if not entity_id or not userid:
        flash("ID is missing!","danger")
        return redirect(url_for("adminassoc.listassoc"))
    else:
        try:
            result=DB.delete("""delete from IS601_User_Entities ue where ue.user_id = %s
                                and ue.entity_id = %s""", userid, entity_id)
            if result.status:
                flash("Successfully removed association to user.", "success")
        except Exception as e:
            flash("Error deleting user association. Try again.","danger")
            
    return redirect(url_for("adminassoc.listassoc"))

@adminassoc.route("/createassoc", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def createassoc():
    if request.method == "POST":
        assocs = request.form.get("assoc").split(',')
        data=[]
        for a in assocs:
            temp = a.strip().capitalize()
            tuple=(temp,1)
            data.append(tuple)
        if len(assocs) > 0:
                try:
                    result = DB.insertMany("INSERT INTO IS601_Entities(name, is_active) VALUES(%s, %s)", data)
                    if result.status:
                        flash("Association(s) created successfully", "success")
                        return redirect(url_for("roles.createassoc"))
                except Exception as e:
                    e = "Error creating associations. Try again."
                    flash(e, "danger")
    return render_template("createassoc.html")