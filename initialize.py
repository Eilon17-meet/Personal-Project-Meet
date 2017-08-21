from model import *
import wikipedia
engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

session.query(Comment).delete()
session.query(Product).delete()
session.query(Customer).delete()
admin_email = 'eilon246810@gmail.com'
admin_password = 'eilon123'
admin = Customer(name='Manager Eilon', email=admin_email, address='No Adress')
admin.hash_password(admin_password)
session.add(admin)
session.commit()

products = [
    # {'name':'M16 Rifle', 'description':wikipedia.summary(wikipedia.search('m16 rifle')[0],sentences=1), 'photo':'/static/pic/M16.gif', 'price':'14999.99', 'tags':'gun peach'},
    # {'name':'Uzi', 'description':wikipedia.summary(wikipedia.search('uzi')[0],sentences=1), 'photo':'http://vignette4.wikia.nocookie.net/roblox-apocalypse-rising/images/8/87/Replica_Uzi.jpg/revision/latest?cb=20150128093212', 'price':'1299.99', 'tags':'gun submachine-gun'},
    # {'name':'Desert Eagel', 'description':wikipedia.summary(wikipedia.search('imi desert eagle')[0],sentences=1), 'photo':'http://www.gunsandammo.com/files/2016/01/desert-eagle-lightweight-1.jpg', 'price':'1599.99', 'tags':'pistol gun handgun'},

    {'name': 'Ibanez RG6PCMLTD', 'description': 'In Blue Reef Gradation',
     'photo': 'https://content.andertons.co.uk/2/1/images/catalog/i/xl_129412-tmpA4EE.jpg', 'price': '1299.99',
     'tags': 'guitar music '},
    # {'name':'Lemon Lime', 'description':'Obey your Thirst', 'photo':'https://i5.walmartimages.com/asr/f6bbc322-83c3-49d9-a9b6-35f05aea0226_1.e37e538746a60bad395e7a0b19ab4f6c.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF', 'price':'2.99','tags':'drink fruit'},
    # {'name':'Tutti Fruiti', 'description':'Tropical Fruit Punch', 'photo':'https://i5.walmartimages.com/asr/859eac0f-f23f-4bf3-b190-91a97d495bbe_1.1376acaadf8d89cb4a12f42fd0318b53.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF', 'price':'1.89','tags':'drink fruit'},
    # {'name':'Root Beer', 'description':'Made from Sassafras', 'photo':'http://cdn6.bigcommerce.com/s-vs756cw/products/1114/images/1739/Tower_Root_Beer__34890.1448901409.1280.1280.png?c=2', 'price':'1.50','tags':'drink'},
    # {'name':'Strawberry', 'description':'Not Fanta, but the next best thing', 'photo':'http://texaslegacybrands.com/media/catalog/product/cache/1/image/800x/9df78eab33525d08d6e5fb8d27136e95/n/e/nesbitt-040190.jpg', 'price':'0.99','tags':'drink fruit'},
    # {'name':'Traditional Cola', 'description':'A Traditional Favorite', 'photo':'https://i5.walmartimages.com/asr/d6ae552d-5bf8-4fcb-9a2f-3be899a90024_1.1da92d09e8dd1ecf04a0d178a909c5cc.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF', 'price':'.88','tags':'drink'},
    # {'name':'Grape', 'description':'Fresh off the vine goodness', 'photo':'http://www.zandh.co.uk/media/catalog/product/cache/1/image/600x600/9df78eab33525d08d6e5fb8d27136e95/o/l/old_jamaica_grape_soda.png', 'price':'1.29','tags':'drink fruit'},
    # {'name':'Simply Orange', 'description':'Pure Squeezed Orange Juice', 'photo':'http://www.coca-colaproductfacts.com/content/dam/productfacts/us/productDetails/ProductImages/SimplyOrange.png', 'price':'2.15','tags':'drink fruit'},
    # {'name':'Peach', 'description':'Fuzzy Navel of Refreshment', 'photo':'http://cdn.shopify.com/s/files/1/0341/3157/products/big-peach-soda_1024x1024.jpg', 'price':'1.99','tags':'drink fruit'},
    # {'name':'Diet Cola', 'description':'Same great taste without the calories', 'photo':'http://acttwomagazine.com/wp-content/uploads/2015/07/Diet_Cola1.jpg', 'price':'1.00','tags':'drink'},
    # {'name':'Energy Cola', 'description':'Gives you wings', 'photo':'https://jarrodhart.files.wordpress.com/2011/09/generic_energy_drink.jpg', 'price':'2.99','tags':'drink'},

]
print
for product in products:
    product['tags'] += ' ' + product['name'].lower()

for product in products:
    newProduct = Product(name=product['name'], description=product['description'], photo=product['photo'],
                         price=product['price'], tags=product['tags'], stars=3.6, customer_id=1)
    session.add(newProduct)
    print(product['name'] + ': ' + str(newProduct.stars))
session.commit()
print('\nNumber Of Products: ' + str(len(products)))
