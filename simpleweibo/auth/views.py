from flask import render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user


from simpleweibo.auth import auth
from simpleweibo.extensions import db
from simpleweibo.models import User
from simpleweibo.email import send_mail
from simpleweibo.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm



@auth.route('/login',methods=['GET','POST'])
def login():
    """
    登陆账户
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('密码或账户错误')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    登出账户
    """
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    """
    注册账户
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.mail,
                  '确认您的账户',
                  template='auth/email/confirm.html',
                  user=user,
                  token=token
                  )
        u = User.query.filter_by(email=form.email.data).first()
        u.set_follow(u)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    """
    登录预处理
    """
    if current_user.is_authenticated:
        current_user.update_last_seen()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """ 账户验证
    :param token: 令牌
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认过您的账户了！')
    else:
        flash('确认链接无效或已过期！')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    """ 账户未确认
        账户注册以后会立即跳转到这里
    """
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """ 账户再确认
        """
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,
              '确认您的账户',
              template='auth/email/confirm.html',
              user=current_user,
              token=token)
    flash('新的确认邮件已发送至您的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/change-password/<username>',methods=['GET','POST'])
@login_required
def change_password(username):
    form = ChangePasswordForm()
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))
    if current_user == user and form.validate_on_submit():
        if not user.verify_password(form.old_password.data):
            flash('原密码错误')
            return redirect(url_for('auth.change_password', username=username))
        user.password = form.new_password.data
        db.session.add(user)
        db.session.commit()
        flash('密码修改成功')
    return render_template('auth/change_password.html', form=form)



