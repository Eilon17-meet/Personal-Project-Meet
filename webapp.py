import os

from flask import *
from flask import session as login_session
from werkzeug.utils import secure_filename

from model import *

app = Flask(__name__)
app.secret_key = "MY_SUPER_SECRET_KEY"
UPLOAD_PRODUCT_PIC_FOLDER = 'static/pic/product_pics/'
UPLOAD_USER_PIC_FOLDER = 'static/pic/user_pics/'
app.config['UPLOAD_PRODUCT_PIC_FOLDER'] = UPLOAD_PRODUCT_PIC_FOLDER
app.config['UPLOAD_USER_PIC_FOLDER'] = UPLOAD_USER_PIC_FOLDER

engine = create_engine('postgres://wnhfzdmxqiwjjh:8303f7e3899346cf3160f14b33f334a61505629ce61bdd1ae4c38250fb34771d@ec2-54-227-250-33.compute-1.amazonaws.com:5432/df1iuch3j1v8gi')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

admin_email = 'eilon246810@gmail.com'


def verify_password(email, password):
    customer = session.query(Customer).filter_by(email=email).first()
    if not customer or not customer.verify_password(password):
        return False
    g.customer = customer
    return True


def calculateTotal(shoppingCart):
    total = 0.0
    for item in shoppingCart.products:
        total += item.quantity * float(item.product.price[1:])
    return total


def generateConfirmationNumber():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))


@app.route('/')
def index():
    return redirect(url_for('inventory'))


@app.route('/hello/')
@app.route("/hello/<name>")
def hello(name=None):
    return render_template('hello_page.html', name=name)


@app.route('/inventory')
def inventory():
    if len(session.query(Customer).all()) == 1:
        if 'id' in login_session:
            if login_session['id'] != 1:
                del login_session['name']
                del login_session['email']
                del login_session['id']
    products = session.query(Product).all()
    return render_template("inventory.html", products=products[::-1])


@app.route('/user/<int:user_id>')
def show_user_profile(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id'] == 1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    customer = session.query(Customer).filter_by(id=user_id).one()
    return render_template('profile.html', customer=customer)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'id' in login_session:
        if login_session['id'] != 1:
            flash('You are already logged in, ' + login_session['name'])
            return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email is None or password is None:
            flash('missing somthing...')
            return redirect(url_for('login'))
        if verify_password(email, password):
            customer = session.query(Customer).filter_by(email=email).one()
            if email == admin_email:
                if 'id' in login_session:
                    if login_session['id'] != 1:
                        del login_session['name']
                        del login_session['email']
                        del login_session['id']
                login_session['id'] = 1
                return redirect(url_for('admin_page', admin_email=customer.email))
            if customer.deleted:
                flash('Customer was Deleted in ' + str(customer.when_deleted) + '!')
                return redirect(url_for('login'))

            login_session['name'] = customer.name
            login_session['email'] = customer.email
            login_session['id'] = customer.id

            flash('login Successful! Welcome back, %s.' % customer.name)
            return redirect(url_for('inventory', customer_id=customer.id))
        else:
            flash('Incorrect username/password combination')
            return redirect(url_for('login'))


@app.route('/newCustomer', methods=['GET', 'POST'])
def newCustomer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        name = first_name + ' ' + last_name
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        image = request.files['pic']

        if name == '' or email == '' or password == '' or address == '':
            flash("Your form is missing arguments")
            return redirect(url_for('newCustomer'))
        if session.query(Customer).filter_by(email=email).first() is not None or email == admin_email:
            flash("A user with this email address already exists")
            return redirect(url_for('newCustomer'))
        if image.filename == '':
            path='static/pic/user_pics/avatar_2x.png'
        else:
            filename = image.filename
            x = 0
            prefix = filename.split('.')[:-1]
            if type(prefix) == str:
                prefix = [prefix]
            suffix = filename.split('.')[-1]
            while filename in os.listdir(UPLOAD_USER_PIC_FOLDER):
                x += 1
                filename = secure_filename(''.join(word + '.' for word in prefix)[:-1] + '(' + str(x) + ').' + suffix)
            path = UPLOAD_USER_PIC_FOLDER + secure_filename(filename)
            image.save(path)
        customer = Customer(name=name, email=email, address=address, deleted=False, photo='/' + path)
        customer.hash_password(password)
        session.add(customer)
        session.commit()
        # login
        login_session['name'] = customer.name
        login_session['email'] = customer.email
        login_session['id'] = customer.id
        flash('You Are Successfully Signed Up! Welcome, %s.' % customer.name)
        return redirect(url_for('inventory', customer_id=session.query(Customer).all()[-1].id))
    else:
        return render_template('newCustomer.html')


@app.route("/product/<int:product_id>", methods=['GET', 'POST'])
def product(product_id):
    product = session.query(Product).filter_by(id=product_id).one()
    if request.method == 'GET':
        all_products = session.query(Product).all()
        all_products.remove(product)
        all_products_dic = {}
        for product_name in all_products:
            all_products_dic[str(product_name)] = product_name
        all_tags = []
        for product_to_check in all_products:
            for tag in product_to_check.tags.split():
                if tag not in all_tags:
                    all_tags.append(tag)

        tags = product.tags.split()

        number_of_similar_products = 6  # Number of how many similar products to show on the page.

        all_common_products = []
        common_tags_dic = {}
        for product_to_check in all_products:
            if product_to_check not in all_common_products:
                for tag in tags:
                    if tag in product_to_check.tags.split():
                        all_common_products.append(product_to_check)
                        if str(product_to_check) not in common_tags_dic:
                            common_tags_dic[str(product_to_check)] = 1
                        else:
                            common_tags_dic[str(product_to_check)] += 1

        common_tags_dic_list = sorted(common_tags_dic, key=common_tags_dic.__getitem__, reverse=True)[
                               :number_of_similar_products]

        common_products = []

        for i in common_tags_dic_list:
            common_products.append(all_products_dic[i])

        return render_template('product page.html', product=product, common_products=common_products)

    elif request.method == 'POST':
        if 'id' not in login_session:
            flash("You must be logged in order to preform this action")
            return redirect(url_for('login'))
        else:
            if login_session['id'] == 1:
                flash("You must be logged in order to preform this action")
                return redirect(url_for('login'))

        text = request.form['text']
        stars = request.form['rating']
        try:
            stars = int(stars)
        except:
            stars = 0
        new_comment = Comment(text=text, stars=stars, timestamp=datetime.now(), product_id=product_id,
                              customer_id=login_session['id'])
        session.add(new_comment)
        session.commit()
        all_comments = session.query(Comment).all()
        total_stars = 0
        for comment in all_comments:
            total_stars += comment.stars
        average = 1.0 * total_stars / len(all_comments)
        product.stars = average
        flash('Comment successfuly added!')
        return redirect(url_for('product', product_id=product_id))


@app.route("/product/<int:product_id>/add_to_favorites")
def add_to_favorites(product_id):
    if 'id' not in login_session:
        flash("You must be logged in order to perform this action")
        return redirect(url_for('login'))
    customer = session.query(Customer).filter_by(id=login_session['id']).one()
    if product_id in [fav.product.id for fav in customer.favorites]:
        flash("This product is already in your favorites")
        return redirect(url_for('favorites'))
    else:
        favorite = Favorite(product_id=product_id, customer_id=customer.id)
        customer.favorites.append(favorite)
        session.add_all([favorite, customer])
        session.commit()
        flash("Successfuly added to Favorites")
        return redirect(url_for('favorites'))


@app.route('/shoppingCart')
def shoppingCart():
    return redirect(url_for('favorites'))


@app.route('/my_products')
def my_products():
    if 'id' not in login_session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))
    user = session.query(Customer).filter_by(id=login_session['id']).one()
    products = session.query(Product).filter_by(customer_id=user.id).all()
    return render_template('my_products.html', products=products, user=user)


@app.route("/favorites")
def favorites():
    if 'id' not in login_session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))
    customer = session.query(Customer).filter_by(id=login_session['id']).one()
    return render_template('favorites.html', customer=customer)


@app.route("/removeFromCart/<int:product_id>", methods=['POST'])
def removeFromCart(product_id):
    if 'id' not in login_session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))
    favorite = session.query(Favorite).filter_by(customer_id=login_session['id']).filter_by(product_id=product_id).one()
    session.delete(favorite)
    session.commit()
    flash("Item deleted from favorites successfully.")
    return redirect(url_for('favorites'))


@app.route('/logout/are_you_sure', methods=['GET', 'POST'])
def are_you_sure_to_log_out():
    if 'name' not in login_session:
        flash("You must be logged in order to log out.")
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('are_you_sure.html')
    elif request.method == 'POST':
        if request.form['choice'] == 'yes':
            return redirect(url_for('logout'))
        else:
            return redirect(url_for('inventory'))


@app.route('/upload_page', methods=['GET', 'POST'])
def upload_page():
    if 'id' not in login_session:
        flash("You must be logged in order to preform this action")
        return redirect(url_for('login'))

    if request.method == 'GET':
        all_products = session.query(Product).all()
        all_tags = []
        for product_to_check in all_products:
            for tag in product_to_check.tags.split():
                if tag not in all_tags:
                    all_tags.append(tag)

        return render_template('upload_product.html', tags=all_tags)

    elif request.method == 'POST':
        image = request.files['pic']
        product_name = request.form['product_name']
        description = request.form['description']
        tags = request.form['tags']
        tags += ' ' + product_name.lower()
        price = request.form['price']
        if image.filename == '' or product_name == '' or description == '' or tags == '' or price == '':
            flash("Your form is missing arguments")
            flash('You must have a photo, a name, a description, a price and at least one tag for your product')
            return redirect(url_for('upload_page'))
        try:
            price = str(float(price))
        except:
            flash('Invalid Price')
            return redirect(url_for('upload_page'))
        if len(price.split('.')[1]) == 1:
            price += '0'
        elif len(price.split('.')[1]) > 2:
            pl = price.split('.')
            while len(pl[1]) != 2:
                pl[1] = pl[1][:-1]
            price = ''.join(i + '.' for i in pl)[:-1]

        filename = image.filename
        x = 0
        prefix = filename.split('.')[:-1]
        if type(prefix) == str:
            prefix = [prefix]
        suffix = filename.split('.')[-1]
        while filename in os.listdir(UPLOAD_PRODUCT_PIC_FOLDER):
            x += 1
            filename = secure_filename(''.join(word + '.' for word in prefix)[:-1] + '(' + str(x) + ').' + suffix)
        path = UPLOAD_PRODUCT_PIC_FOLDER + secure_filename(filename)
        image.save(path)

        '''if image =='' or email =='' or password =='' or address=='':
            flash("Your form is missing arguments")
            return redirect(url_for('newCustomer'))'''
        new_product = Product(name=product_name, timestamp=datetime.now(), description=description, photo='/' + path,
                              price=price, tags=tags, stars=0, customer_id=login_session['id'])
        session.add(new_product)
        session.commit()
        return redirect(url_for('inventory'))


@app.route('/logout')
def logout():
    if are_you_sure_to_log_out():
        del login_session['name']
        del login_session['email']
        del login_session['id']
        flash("Logged Out Succefully.")
        return redirect(url_for('inventory'))


@app.route('/admin_page/<admin_email>')
def admin_page(admin_email):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id'] == 1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    customers = session.query(Customer).all()
    admin = session.query(Customer).filter_by(email=admin_email).one()
    customers.remove(customers[0])
    return render_template('admin_page.html', customers=customers, admin=admin)


@app.route('/delete_user/are_you_sure/<int:user_id>', methods=['GET', 'POST'])
def are_you_sure_to_delete(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id'] == 1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    user = session.query(Customer).filter_by(id=user_id).one()
    user_id = user.id
    if request.method == 'GET':
        return render_template('delete_user_are_you_sure.html', user_id=user_id)
    elif request.method == 'POST':
        if request.form['choice'] == 'yes':
            return redirect(url_for('delete_user', user_id=user_id))
        else:
            flash('User Not Deleted!')
            return redirect(url_for('inventory'))


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id'] == 1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    user = session.query(Customer).filter_by(id=user_id).one()
    user.deleted = True
    user.when_deleted = datetime.now()
    session.commit()
    flash('User Deleted Successfully!')
    return redirect(url_for('admin_page', admin_email=admin_email))


if __name__ == '__main__':
    app.run(debug=True)
