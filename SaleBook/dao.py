from SaleBook import app, db
import hashlib
from SaleBook.models import User, UserRole, Book, Category, Cart, Author, Order, PaymentMethod, OrderDetail, Import, \
    ImportDetail
import cloudinary.uploader

# add__ thêm mới
# get__ lấy thông tin
# get_all__ lấy tất cả, lấy tất cả theo điều kiện
# count__ đếm số lượng
# check__ kiểm tra tồn tại
# access_check__ kiểm tra quyền truy cập


# load sản phẩm cho trang chủ
def load_book(kw=None, page=1):
    query = Book.query

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size

    if kw:
        query = query.filter(Book.name.contains(kw))

    # if cate_id:
    #     query = query.filter(Product.category_id == cate_id)
    query = query.slice(start, start + page_size)

    return query.all()


# đếm số lượng sách (phân trang)
def count_books():
    return Book.query.count()


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def get_all_book():
    return Book.query.all()


def add_new_book(name, price, quantity, description, barcode, category_id, author_id, image=None):

    b = Book(name=name, price=price, stock_quantity=quantity, description=description,barcode=barcode, category_id=category_id, author_id=author_id)
    if image:
        res = cloudinary.uploader.upload(image)
        b.image = res.get('secure_url')
    db.session.add(b)
    db.session.commit()
    return b


def check_exist_book(book_name):
    b = Book.query.filter(Book.name==book_name).first()
    return b.id


def add_exist_book(book_id, quantity):
    b = Book.query.get(book_id)
    b.stock_quantity += quantity
    db.session.add(b)
    db.session.commit()
    return


def reduce_book_bought(book_id ,quantity):
    b = get_book_by_id(book_id=book_id)
    b.stock_quantity -= int(quantity)
    db.session.add(b)
    db.session.commit()
    return


def get_all_category():
    return Category.query.all()


def add_category(name, description):
    c = Category(name=name, description=description)
    db.session.add(c)
    db.session.commit()
    return


def get_all_author():
    return Author.query.all()


def add_author(name, description):
    a = Author(name=name, description=description)
    db.session.add(a)
    db.session.commit()
    return


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password)).first()


def add_customer(name, username, password, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()
    return


# Kiểm tra user đã tồn tại khi tạo tài khoản
def check_exist_user(username):
    return User.query.filter(User.username.__eq__(username.strip())).first()


# Kiểm tra user không có quyền vào trang admin
def access_check(user_id):
    return User.query.filter(User.user_role.__eq__(UserRole.CUSTOMER)).first()


#Trả về true nếu là importer, false nếu không phải
def access_check_import_book(user_id):
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.INVENTORY_MANAGER:
        return True
    return False


# Thêm một sản phẩm vô cart
def add_to_cart(customer_id, book_id, quantity):
    cart = Cart.query.filter(Cart.book_id == book_id, Cart.customer_id == customer_id).first()
    if cart:
        cart.quantity += quantity
    else:
        new_cart = Cart(quantity=quantity, book_id=book_id, customer_id=customer_id)
        db.session.add(new_cart)
    db.session.commit()
    return


# lấy tất cả sản phẩm trong cart của một user
def get_all_cart(customer_id):
    return Cart.query.filter(Cart.customer_id == customer_id).all()


# xóa một saản phẩm trong cart
def remove_cart_by_id(cart_id):
    c = Cart.query.get(cart_id)
    db.session.delete(c)
    db.session.commit()
    return


# xóa tất cả sản phẩm trong cart
def remove_all_cart_by_userid(customer_id):
    cart = Cart.query.filter(Cart.customer_id == customer_id).all()
    for c in cart:
        db.session.delete(c)
    db.session.commit()
    return


# Thay đổi sô lượng sản phẩm trong cart
def change_cart_quantity(cart_id, quantity):
    cart = Cart.query.get(cart_id)
    cart.quantity = quantity
    db.session.add(cart)
    db.session.commit()
    return


# Thêm một order
def add_order_online(customer_id, total_price):
    order = Order(customer_id=customer_id, total_price=total_price)
    db.session.add(order)
    db.session.commit()
    return order


# Thêm một order_detail (danh mục nhỏ trong order)
def add_order_detail(order_id, book_id, quantity, unit_price):
    o_detail = OrderDetail(order_id=order_id, book_id=book_id, quantity=quantity, unit_price=unit_price)
    db.session.add(o_detail)
    db.session.commit()
    return


# lấy tất cả order của một customer
def get_all_order_by_customer_id(customer_id):
    return Order.query.filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()


def add_import_book(importer_id, total_price):
    i = Import(importer_id=importer_id, total_price=total_price)
    db.session.add(i)
    db.session.commit()
    return i


def add_import_detail_book(quantity, unit_price, import_id, book_id):
    i_detail = ImportDetail(quantity=quantity, unit_price=unit_price, import_id=import_id, book_id=book_id)
    db.session.add(i_detail)
    db.session.commit()
    return


def get_all_import_by_importer(importer_id):
    return Import.query.filter(Import.importer_id == importer_id).order_by(Import.import_date.desc()).all()











