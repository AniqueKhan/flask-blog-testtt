from flask import render_template,url_for,flash,redirect,request,Blueprint

from flaskblog.users.forms import LoginForm,SignUpForm,UpdateProfileForm,RequestResetForm,ResetPasswordForm
from flaskblog.models import User,Post
from flaskblog import bcrypt,db
from flask_login import login_user,current_user,logout_user,login_required


from flaskblog.users.utils import save_picture,send_reset_email

users= Blueprint("users",__name__)



@users.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=3)
    return render_template("user_profile.html",posts=posts,user=user)

@users.route("/signup",methods=['GET',"POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user  = User(username = form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created for '+ form.username.data+"! You can now login.",'success')
        return redirect(url_for('users.login'))
    return render_template("signup.html",title='SignUp',form=form)

@users.route("/login",methods=['GET',"POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            flash("Login Successful. Welcome , "+ user.username+"!",'success')
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check your email and password.','danger')
    return render_template("login.html",title='Login',form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/profile')
@login_required
def profile():
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).filter_by(author = current_user).paginate(page=page,per_page=3)
    return render_template("profile.html",title='Profile',image_file=image_file,posts=posts)


@users.route("/edit_profile",methods=['GET','POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your profile has been successfully updated!",'success')
        return redirect(url_for("users.profile"))
    elif request.method=='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("edit_profile.html",form=form)

@users.route("/reset_password",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instruction to reset your password",'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

@users.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token.",'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You can now login.",'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html',title='Reset Password',form=form)