from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
UPLOAD_FOLDER = '/Desktop/Blog/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["id"] == 1:
            return f(*args, **kwargs)
        else:
            flash("Buraya girmeyi denememeliydin","danger")
            return redirect(url_for("layout"))
    return decorated_function
class articleform(Form):
    title = StringField()
    content = TextAreaField()
    link = StringField()
class register(Form):
    name = StringField("İsim",validators=[validators.DataRequired("Lütfen isminizi giriniz."),validators.Length(max=15)])
    fname = StringField("Soyad",validators=[validators.Optional(),validators.Length(max=20)])
    email = StringField("Email Adresi",validators=[validators.DataRequired(),validators.Email(message="Lütfen doğru bir mail giriniz.")])
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen şifrenizi giriniz."),
        validators.EqualTo(fieldname= "confirm",message="Şifreler uyuşmuyor.")
    ])
    confirm = PasswordField("Şifre doğrulama")
class loginform(Form):
    email = StringField("Email")
    password = PasswordField("Şifre")
class profileform(Form):
    name = StringField("İsim",validators=[validators.DataRequired("Lütfen isminizi giriniz."),validators.Length(max=15)])
    fname = StringField("Soyad",validators=[validators.Optional(),validators.Length(max=20)])
    email = StringField("Email Adresi",validators=[validators.DataRequired(),validators.Email(message="Lütfen doğru bir mail giriniz.")])
    password = PasswordField("Parola",validators=[validators.DataRequired(message="Lütfen şifrenizi giriniz."),])
class setpassw(Form):
    oldpassword = PasswordField("Şu anki şifreniz",validators=[validators.DataRequired(message="Lütfen şifrenizi giriniz.")])
    password = PasswordField("Yeni şifreniz",validators=[
        validators.DataRequired(message="Lütfen şifrenizi giriniz."),
        validators.EqualTo(fieldname= "confirm",message="Şifreler uyuşmuyor.")
    ])
    confirm = PasswordField("Şifre doğrulama")  
app = Flask(__name__)
app.config["MYSQL_HOST"] = "mysql08.turhost.com"
app.config["MYSQL_USER"] = "keremgl"
app.config["MYSQL_PASSWORD"] = "C4bbartv61!"
app.config["MYSQL_DB"] = "keremglc_mysql"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
app.secret_key = "blog"
@app.route("/")
def layout():
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles"
    cursor.execute(sorgu)
    data = cursor.fetchall()
    data2 = data[::-1]
    data3 = data2[:5]
    return render_template("index.html",articles = data3)
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/register",methods=['GET', 'POST'])
def reg():
    form = register(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        fname = form.fname.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu2 = "Select * from users"
        cursor.execute(sorgu2)
        data2 = cursor.fetchall()
        for i in data2:
            if i["email"] == email:
                flash("Bu mail adresi başka bir hesap tarafından kullanılıyor.Lütfen tekrar deneyiniz","warning")
                return redirect(url_for("reg"))
        sorgu = "insert into users(name,fname,email,password) values(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,fname,email,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla kayıt oldunuz!!!","success")
        return redirect(url_for("giris"))
    else:
        return render_template("register.html",form=form)
@app.route("/login",methods =["GET","POST"])
def giris():
    form = loginform(request.form)
    if request.method == "POST":
        email = form.email.data
        password_first = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "select * from users where email = %s"
        result = cursor.execute(sorgu,(email,))
        if result > 0 : 
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_first,real_password):
                flash("Başarıyla giriş yaptınız!","success")
                session["giris"] = True
                ad = data["name"]
                nu = data["Id"]
                session["id"] = nu
                session["username"] = ad
                session["fname"] = data["fname"]   
                session["email"] = data["email"]         
                return redirect(url_for("layout"))
            else:
                flash("Şifre hatalı !!!","danger")
                return redirect(url_for("giris"))
        else:
            flash("Lütfen girdiğiniz emaili kontrol ediniz!","danger")
            return redirect(url_for("giris"))  
    else:
        return render_template("login.html",form = form)
@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış yaptınız!","danger")
    return redirect(url_for("layout"))
@app.route("/H20041232",methods = ["POST","GET"])
@login_required
def admin():
    return render_template("admin.html")
@app.route("/add_article",methods=['GET', 'POST'])
@login_required
def ekle():
    form = articleform(request.form)
    if request.method == "POST":
        title = form.title.data
        content = form.content.data
        link = form.link.data
        cursor = mysql.connection.cursor()
        sorgu = "insert into articles(title,content,author,link) values(%s,%s,%s,%s)"
        cursor.execute(sorgu,(title,content,"Kerem Gül(Yönetici)",link))
        mysql.connection.commit()
        cursor.close()
        flash("Makale başarıyla eklendi.","success")
        return redirect(url_for("admin"))
    else:
        return render_template("addarticle.html",form = form)
@app.route("/article/<string:id>")
def makale(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")
@app.route("/articles")
def showcase():
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles"
    cursor.execute(sorgu)
    data = cursor.fetchall()
    return render_template("showcase.html",articles = data)
@app.route("/search",methods = ["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("layout"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "select * from articles where title like '%" + keyword + "%'"
        result = cursor.execute(sorgu)
        if result == 0:
            flash("Böyle bir yazı bulunumadı...","warning")
            return redirect(url_for("/articles"))
        else:
            data = cursor.fetchall()
            return render_template("showcase.html",articles = data)       
@app.route("/edit_article")
@login_required 
def edit():
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles"
    cursor.execute(sorgu)
    data = cursor.fetchall()
    return render_template("editarticle.html",articles = data)
@app.route("/searchs",methods = ["GET","POST"])
def searchs():
    if request.method == "GET":
        return redirect(url_for("layout"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "select * from articles where title like '%" + keyword + "%'"
        result = cursor.execute(sorgu)
        if result == 0:
            flash("Böyle bir yazı bulunumadı...","warning")
            return redirect(url_for("/edit_article"))
        else:
            data = cursor.fetchall()
            return render_template("editarticle.html",articles = data)
@app.route("/delete_article/<string:id>")
@login_required
def delet(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where id = %s"
    res = cursor.execute(sorgu,(id,))
    if res == 0:
        flash("Böyle bi makale bulunulamadı","warning")
        return  redirect(url_for("layout"))
    else:
        sorgu2 = "delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        flash("Makale Başarıyla silindi.","success")
        return redirect(url_for("edit"))
@app.route("/update/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where id = %s"
        res = cursor.execute(sorgu,(id,))
        if res == 0:
            flash("Böyle bir makale bulunamadı.","warning")
            return redirect(url_for("edit"))
        else:
            sonhal = cursor.fetchone()
            form = articleform()
            form.title.data = sonhal["title"]
            form.content.data = sonhal["content"]
            return render_template("Update.html", form = form)
    else:
        form = articleform(request.form)
        newt = form.title.data
        newc = form.content.data
        cursor = mysql.connection.cursor()
        sorgu = "Update articles set title = %s, content = %s where id = %s"
        cursor.execute(sorgu,(newt,newc,id))
        mysql.connection.commit()
        flash("Makale başaryıla güncellendi.","success")
        return redirect(url_for("edit"))
@app.route("/profile/<string:id>",methods = ["GET","POST"])
def profile(id):
    if session["id"] == int(id) or session["id"] == 1:
        if request.method == "GET":
            cursor = mysql.connection.cursor()
            sorgu = "select * from users where id = %s"
            cursor.execute(sorgu,(id,))
            data = cursor.fetchone()
            return render_template("bilgiler.html",user = data)
    else:
        flash("Bu işlemi yapmak için yetkiniz yoktur.","warning")
        return redirect(url_for("layout"))
@app.route("/profile_update/<string:id>",methods = ["GET","POST"])
def profile_updat(id):
    if session["id"]:
        if session["id"] == int(id) or session["id"] == 1:
            if request.method == "GET":
                cursor = mysql.connection.cursor()
                sorgu = "select * from users where id = %s"
                cursor.execute(sorgu,(int(id),))
                data = cursor.fetchone()
                form = profileform()
                form.name.data = data["name"]
                form.fname.data = data["fname"]
                form.email.data = data["email"]
                return render_template("bilgiler_update.html",form = form,user = data)  
            else:
                form = profileform(request.form)
                cursor = mysql.connection.cursor()
                sorgu2 = "Select * from users"
                cursor.execute(sorgu2)
                data2 = cursor.fetchall()
                for i in data2:
                    if form.email.data == i["email"]:
                        flash("Bu mail adresi başka bir hesap tarafından kullanılıyor.","warning")
                        return redirect(url_for("profile",id = id))   
                sorgu = "Update users set name = %s,fname = %s,email = %s where id = %s"
                cursor.execute(sorgu,(form.name.data,form.fname.data,form.email.data,id))
                mysql.connection.commit()
                flash("Bilgileriniz başarıyla güncellendi","success")
                return redirect(url_for("profile_updat",id = id)) 
        else:
            flash("Bu işlemi yapmak için yetkiniz yoktur.","warning")
            return redirect(url_for("layout"))
    else:
        flash("Bu işlemi yapmak için giriş yapmalısınız.","warning")
        return redirect(url_for("layout"))       
@app.route("/set_password/<string:id>",methods = ["GET","POST"])
def setpas(id):
    if session["id"] == int(id) or session["id"] == 1:
        form = setpassw(request.form)
        if request.method == "GET":
            cursor = mysql.connection.cursor()
            sorgu = "select * from users where id = %s"
            cursor.execute(sorgu,(int(id),))
            data = cursor.fetchone()
            return render_template("setpass.html",form = form,user = data)   
        elif request.method =="POST" and form.validate():
            cursor = mysql.connection.cursor()
            sorgu = "select * from users where id = %s"
            cursor.execute(sorgu,(int(id),))
            data = cursor.fetchone()
            if sha256_crypt.verify(form.oldpassword.data,data["password"]):
                sorgu2 = "update users set password = %s where id = %s"
                password = sha256_crypt.encrypt(form.password.data)
                cursor.execute(sorgu2,(password,int(id)))
                mysql.connection.commit()
                sorgu3 = "select * from users where id = %s"
                cursor.execute(sorgu3,(int(id),))
                data3 = cursor.fetchone
                flash("Şifre başarıyla değiştirildi","success")
                return redirect(url_for("profile",user = data3,id = id))
            else:
                flash("Girdiğiniz şifre mevcut şifrenizle uyuşmamaktadır.","danger")
                return redirect(url_for("setpas",id = id,user = data))
    else:   
        flash("Bu işlemi yapmak için yetkiniz yoktur.","warning")
        return redirect(url_for("layout"))
if __name__ == "__main__":
    app.run(debug=True)
    