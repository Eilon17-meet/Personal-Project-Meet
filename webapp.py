from flask import *
from model import *
from flask import session as login_session
import string
import locale
import random
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "MY_SUPER_SECRET_KEY"
UPLOAD_FOLDER = 'static/pic/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

admin_email='eilon246810@gmail.com'

def verify_password(email,password):
    customer= session.query(Customer).filter_by(email= email).first()
    if not customer or not customer.verify_password(password):
        return False
    g.customer= customer
    return True

def calculateTotal(shoppingCart):
    total=0.0
    for item in shoppingCart.products:
        total+=item.quantity*float(item.product.price[1:])
    return total

def generateConfirmationNumber():
    return ''.join(random.choice(string.ascii_uppercase+string.digits) for x in xrange(16))

@app.route('/')
def index():
    return redirect(url_for('inventory',customer_id='None'))

@app.route('/hello/')
@app.route("/hello/<name>")
def hello(name=None):
    return render_template('hello_page.html',name=name)

@app.route('/inventory/<customer_id>')
def inventory(customer_id):
    if customer_id == 'None':
        return redirect(url_for('login'))
    customer = session.query(Customer).filter_by(id=customer_id).one()
    items = session.query(Product).all()
    return render_template("inventory.html",items=items,customer=customer)

@app.route('/user/<int:user_id>')
def show_user_profile(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id']==1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    customer=session.query(Customer).filter_by(id=user_id).one()
    return render_template('profile.html', customer=customer)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email is None or password is None:
            flash('missing somthing...')
            return redirect(url_for('login'))
        if verify_password(email,password):
            customer = session.query(Customer).filter_by(email=email).one()
            if email==admin_email:
                if 'id' in login_session:
                    del login_session['name']
                    del login_session['email']
                    del login_session['id']
                login_session['id']=1
                print '\n###############\n'
                print login_session
                print '\n###############\n'
                return redirect(url_for('admin_page',admin_email=customer.email))
            if customer.deleted:
                flash('Customer was Deleted in '+str(customer.when_deleted)+'!')
                return redirect(url_for('login'))

            login_session['name'] = customer.name
            login_session['email'] = customer.email
            login_session['id'] = customer.id
            
            flash ('login Successful! Welcome back, 00-%s' % customer.name)
            return redirect(url_for('inventory',customer_id=customer.id))
        else:
            flash('Incorrect username/password combination')
            return redirect(url_for('login'))

@app.route('/newCustomer', methods = ['GET','POST'])
def newCustomer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        if name =='' or email =='' or password =='' or address=='':
            flash("Your form is missing arguments")
            return redirect(url_for('newCustomer'))
        if session.query(Customer).filter_by(email = email).first() is not None or email==admin_email:
            flash("A user with this email address already exists")
            return redirect(url_for('newCustomer'))
        customer = Customer(name = name, email=email, address = address, deleted=False)
        customer.hash_password(password)
        session.add(customer)
        shoppingCart = ShoppingCart(customer=customer)
        session.add(shoppingCart)
        session.commit()
        #login
        login_session['name'] = customer.name
        login_session['email'] = customer.email
        login_session['id'] = customer.id
        flash ('login Successful! Welcome, agent 00-%s' % customer.name)
        return redirect(url_for('inventory',customer_id=session.query(Customer).all()[-1].id))
    else:
        return render_template('newCustomer.html')


@app.route("/product/<int:product_id>")
def product(product_id):
    product=session.query(Product).filter_by(id=product_id).one()
    all_products=session.query(Product).all()
    all_products.remove(product)
    all_products_dic={}
    for product_name in all_products:
        all_products_dic[str(product_name)]=product_name
    all_tags=[]
    for product_to_check in all_products:
        for tag in product_to_check.tags.split():
            if tag not in all_tags:
                all_tags.append(tag)
    
    tags=product.tags.split()

    number_of_similar_products = 6 #Number of how many similar products to show on the page.

            
    all_common_products=[]
    common_tags_dic={}
    for product_to_check in all_products:
        if product_to_check not in all_common_products:
            for tag in tags:
                if tag in product_to_check.tags.split():
                    all_common_products.append(product_to_check)
                    if str(product_to_check) not in common_tags_dic:
                        common_tags_dic[str(product_to_check)]=1
                    else:
                        common_tags_dic[str(product_to_check)]+=1

    common_tags_dic_list=sorted(common_tags_dic, key=common_tags_dic.__getitem__, reverse=True)[:number_of_similar_products]

    common_products=[]

    for i in common_tags_dic_list:
        common_products.append(all_products_dic[i])
    #common_products=[all_products_dic[common_tags_dic_list[0]],all_products_dic[common_tags_dic_list[1]],all_products_dic[common_tags_dic_list[2]]]

    return render_template('product.html',product=product,common_products=common_products)

@app.route("/product/<int:product_id>/addToCart", methods = ['POST'])
def addToCart(product_id):
    if 'id' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    quantity = request.form['quantity']
    product = session.query(Product).filter_by(id = product_id).one()
    shoppingCart = session.query(ShoppingCart).filter_by(customer_id = login_session['id']).one()
    if product.name in [item.product.name for item in shoppingCart.products]:
        assoc = session.query(ShoppingCartAssociation).filter_by(shoppingCart= shoppingCart) \
            .filter_by(product= product).one()
        assoc.quantity = int(assoc.quantity) + int(quantity)
        flash("Successfuly added to Shopping Cart")
        return redirect(url_for('shoppingCart'))
    else:
        a = ShoppingCartAssociation(product= product, quantity=quantity)
        shoppingCart.products.append(a)
        session.add_all([a,product,shoppingCart])
        session.commit()
        flash("Successfuly added to Shopping Cart")
        return redirect(url_for('shoppingCart'))
        
@app.route("/shoppingCart")
def shoppingCart():
    if 'id' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    shoppingCart=session.query(ShoppingCart).filter_by(customer_id=login_session['id']).one()
    return render_template('shoppingCart.html', shoppingCart=shoppingCart)

@app.route("/removeFromCart/<int:product_id>", methods = ['POST'])
def removeFromCart(product_id):
    if 'id' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    shoppingCart=session.query(ShoppingCart).filter_by(customer_id=login_session['id']).one()
    association=session.query(ShoppingCartAssociation).filter_by(shoppingCart=shoppingCart).filter_by(product_id=product_id).one()
    session.delete(association)
    session.commit()
    flash("Item extarminated successfully.")
    return redirect(url_for('shoppingCart'))

@app.route("/updateQuantity/<int:product_id>", methods = ['POST'])
def updateQuantity(product_id):
    if 'id' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    quantity=request.form['quantity']
    print '\n\n\n'+(quantity)+'\n\n\n'
    if quantity=='0':
        return removeFromCart(product_id)
    shoppingCart=session.query(ShoppingCart).filter_by(customer_id=login_session['id']).one()
    assoc=session.query(ShoppingCartAssociation).filter_by(shoppingCart=shoppingCart).filter_by(product_id=product_id).one()
    assoc.quantity=quantity
    session.add(assoc)
    session.commit()
    flash("Quantity Updated Succsessfully.")
    return redirect(url_for('shoppingCart'))

@app.route("/checkout", methods = ['GET', 'POST'])
def checkout():
    if 'id' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    shoppingCart=session.query(ShoppingCart).filter_by(customer_id=login_session['id']).one()
    if request.method=='POST':
        order=Order(customer_id=login_session['id'],confirmation=generateConfirmationNumber())
        order.total=calculateTotal(shoppingCart)
        for item in shoppingCart.products:
            assoc=OrdersAssociation(product=item.product,product_qty=item.quantity)
            order.products.append(assoc)
            session.delete(item)
        session.add_all([order,shoppingCart])
        session.commit()
        return redirect(url_for('confirmation', confirmation=order.confirmation))
    elif request.method=='GET':
        return render_template('checkout.html',shoppingCart=shoppingCart,total=calculateTotal(shoppingCart))


@app.route("/confirmation/<confirmation>")
def confirmation(confirmation):
    if 'name' not in login_session:
        flash("You must be logged in to perform this action, 007")
        return redirect(url_for('login'))
    order=session.query(Order).filter_by(confirmation=confirmation).one()
    return render_template('confirmation.html', order=order)

@app.route('/logout/are_you_sure', methods = ['GET', 'POST'])
def are_you_sure_to_log_out():
    if 'name' not in login_session:
        flash("You must be logged in order to log out, 007")
        return redirect(url_for('login'))
    if request.method=='GET':
        return render_template('are_you_sure.html')
    elif request.method=='POST':
        if request.form['choice']=='yes':
            return redirect(url_for('logout'))
        else:
            return redirect(url_for('inventory'))


@app.route('/upload_page/<int:customer_id>', methods = ['GET','POST'])
def upload_page(customer_id):
    if request.method=='GET':
        all_products=session.query(Product).all()
        all_tags=[]
        for product_to_check in all_products:
            for tag in product_to_check.tags.split():
                if tag not in all_tags:
                    all_tags.append(tag)

        return render_template('upload_product.html', tags=all_tags, customer_id=customer_id)
    
    elif request.method=='POST':
        image = request.files['pic']
        path = UPLOAD_FOLDER+secure_filename(image.filename)
        image.save(path)
        print os.path.realpath(image.filename)

        product_name=request.form['name']
        description=request.form['description']
        tags=request.form['tags']
        price=request.form['price']
        newProduct = Product(name=product_name, description=description, photo='/'+path, price=price, tags=tags, stars=0.5, number_of_reviews=0,customer_id=customer_id)
        session.add(newProduct)
        session.commit()
        return redirect(url_for('inventory',customer_id=customer_id))



@app.route('/logout')
def logout():
    if are_you_sure_to_log_out():
        del login_session['name']
        del login_session['email']
        del login_session['id']
        flash("Logged Out Succefully. May The Force Be With You, Agent")
        return redirect(url_for('inventory'))

@app.route('/admin_page/<admin_email>')
def admin_page(admin_email):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id']==1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    customers=session.query(Customer).all()
    admin=session.query(Customer).filter_by(email=admin_email).one()
    customers.remove(customers[0])
    return render_template('admin_page.html', customers=customers, admin=admin)

@app.route('/delete_user/are_you_sure/<int:user_id>', methods = ['GET', 'POST'])
def are_you_sure_to_delete(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id']==1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    user=session.query(Customer).filter_by(id=user_id).one()
    user_id=user.id
    if request.method=='GET':
        return render_template('delete_user_are_you_sure.html',user_id=user_id)
    elif request.method=='POST':
        if request.form['choice']=='yes':
            return redirect(url_for('delete_user', user_id=user_id))
        else:
            flash('User Not Deleted!')
            return redirect(url_for('inventory'))


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'id' not in login_session:
        flash("You Have To Log In, Admin!")
        return redirect(url_for('inventory'))
    if not login_session['id']==1:
        flash("You Are Not Allowed To Get To This Page!")
        return redirect(url_for('inventory'))
    user=session.query(Customer).filter_by(id=user_id).one()
    user.deleted=True
    user.when_deleted=datetime.now()
    session.commit()
    flash('User Deleted Successfuly!')
    return redirect(url_for('inventory'))

if __name__ == '__main__':
    app.run(debug=True)
