from flask import Blueprint, flash, redirect, request, render_template, url_for, current_app
from sql.db import DB
from flask_login import login_required, current_user
userassoc = Blueprint('userassoc', __name__)

"""
    UCID:   mk2246
    Date:   05/01/2023
    Desc:   The addassociation functionality allows the users to add permissions to the application to their users.
            The associations specific to the user are stored to the IS601_User_Entities table. After addition of
            associations, a success message is displayed to the user. If the addition fails, a failure message is
            displayed to the user. Users can add multiple associations at the same time from the associations
            available to the user.
"""

@userassoc.route('/addassoc', methods=['GET','POST'])
@login_required
def addassociation():
    rows=[]
    if request.method == "POST":
        associations=request.form.getlist("assoc_checkbox")
        dataList = []
        for a in associations:
            tempTuple = (current_user.get_id(), a)
            dataList.append(tempTuple)
        if dataList:
            try:
                result = DB.insertMany("insert into IS601_User_Entities(user_id, entity_id) values(%s, %s)", dataList)
                if result.status:
                    flash("Association(s) added to user.","success")
            except Exception as e:
                print(e)
                flash("Error adding associations. Try again.", "danger")
    try:
        result = DB.selectAll("""select id,name from IS601_Entities where is_active=1""")
        rows=result.rows
    except Exception as e:
        flash("Error retrieving associations. Try again.", "danger")
    return render_template("add_user_assoc.html",rows=rows)

@userassoc.route('/listassoc', methods=['GET','POST'])
@login_required
def listassociation():
    rows=[]
    filter = {}
    filter["userid"] = current_user.get_id()
    allowed_columns = ["description","is_active"]

    query=f"""select ue.id, e.name, e.description, ue.is_active from IS601_User_Entities ue
            join IS601_Entities e on e.id = ue.entity_id 
            where ue.user_id = {filter['userid']}"""

    description = request.args.get('description')
    is_active = request.args.get('is_active')
    name = request.args.get('association')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    
    filter["description"] = description
    filter["is_active"] = is_active
    filter["name"] = name

    if name:
        query += f" and e.name like '%%{filter['name']}%%'"
    if description:
        query += f" and e.description like '%%{filter['description']}%%'"
    if is_active:
        query += f" and ue.is_active = '%%{filter['is_active']}%%'"
    
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
        e = "Error retrieving associations for the user. Try again."
        flash(e, "danger")
    count = len(rows)
    allowed_columns = [("description", "Description"), ("is_active", "Active?")]
    return render_template("list_user_assoc.html",rows=rows, allowed_columns=allowed_columns, count=count)

"""
    UCID:   mk2246
    Date:   05/01/2023
    Desc:   The deleteassociation functionality allows the users to delete associations.
            The associations specific to the user are deleted from the IS601_User_Entities table. After deletion of
            associations, a success message is displayed to the user. If the deletion fails, a failure message is
            displayed to the user. Users can delete multiple associations at the same time from the associations
            available to the user by clicking on Clear All Associations or Clear Inactive Associations or
            Clear Active Associations.
"""

@userassoc.route('/deleteassoc', methods=['GET','POST'])
@login_required
def deleteassociation():
    if request.method == "POST":
        makeinactive=request.form.get("makeinactive")
        clearinactive = request.form.get('clearinactive')
        clearactive = request.form.get('clearactive')
        clearall = request.form.get('clearall')
        entityid=request.args.get("id")
        if not entityid:
            flash("ID is missing!","danger")
            return redirect(url_for("userassoc.listassociation"))
        delFlag=False
        if makeinactive:
            try:
                inactiveresult=DB.update("""update IS601_User_Entities ue
                                            set ue.is_active=0 where ue.user_id=%s
                                            and ue.id=%s"""
                                            , current_user.get_id(), entityid)
                if inactiveresult.status:
                    flash("Association set as inactive.","success")
            except Exception as e:
                flash("Error making association as inactive.","danger")
        if clearall or clearactive or clearinactive:
            try:
                selectresult=DB.selectAll("""select ue.id from IS601_User_Entities ue
                                            where ue.user_id = %s""", current_user.get_id())
                selectrows=selectresult.rows
                if selectresult.status:
                    for r in selectrows:
                        entityid=r['id']
                        try:
                            if clearall:
                                query=f"""delete from IS601_User_Entities ue 
                                            where ue.id = %s and ue.user_id = %s"""
                            elif clearactive:
                                query=f"""delete from IS601_User_Entities ue 
                                            where ue.id = %s and ue.user_id = %s and ue.is_active=1"""
                            elif clearinactive:
                                query=f"""delete from IS601_User_Entities ue 
                                            where ue.id = %s and ue.user_id = %s and ue.is_active=0"""
                            result = DB.delete(query, entityid, current_user.get_id())
                            delFlag=True
                        except Exception as e:
                            print(e)
                if delFlag:
                    flash("Cleared associations for user.", "success")
            except Exception as e:
                flash("Error clearing associations for the user. Try again.", "danger")
    else:
        entityid=request.args.get("id")
        try:
            result = DB.delete(f"""delete from IS601_User_Entities ue
                                where ue.id = {entityid} and ue.user_id = %s"""
                                , current_user.get_id())
            if result.status:
                flash("Deleted association for user", "success")
        except Exception as e:
            flash("Error deleting association for user.", "danger")

    return redirect(url_for("userassoc.listassociation"))

@userassoc.route('/assocreport', methods=['GET'])
@login_required
def associationreport():
    entityrows = []
    rows = []
    allowed_columns=["name", "Number_of_users"]
    filter={}

    try:
        entityresult = DB.selectAll("select id as entity_id, name from IS601_Entities where is_active=1")
        if entityresult.status:
            entityrows = entityresult.rows
    except Exception as e:
        flash("Error retrieving entities. Try again.", "danger")
    
    query= """select e.name as association_name, count(ue.entity_id) as Number_of_users
                from IS601_Entities e
                left join IS601_User_Entities ue on ue.entity_id = e.id
                where e.is_active = 1"""

    entity_id = request.args.get('entity')
    no_of_users = request.args.get('no_users')
    limit = request.args.get("limit","10")
    column = request.args.get("column")
    order = request.args.get("order")
    operation = request.args.get('operation')
    filter["entity_id"] = entity_id
    filter["no_of_users"] = no_of_users
    filter["operation"] = operation
    
    if entity_id:
        query += f" and e.id = {filter['entity_id']}"

    query += " group by association_name"
    
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
            rows = result.rows
    except Exception as e:
        flash("Error retrieving entities associated to users. Try again.", "danger")
    
    allowed_columns=[("name", "Association Name"), ("Number_of_users", "Number of users")]
    return render_template("assoc_report.html", entityrows=entityrows, rows=rows, allowed_columns=allowed_columns)