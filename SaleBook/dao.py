from datetime import datetime, timedelta

from SaleBook import app, db
import hashlib
from SaleBook.models import User, UserRole, Book, Category, Cart, Author, Order, OrderDetail, Import, Invoice, \
    ImportDetail, InvoiceDetail, Regulation, PaymentMethod, OrderStatus
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
    b = Book(name=name, price=price, stock_quantity=quantity, description=description, barcode=barcode,
             category_id=category_id, author_id=author_id)
    if image:
        res = cloudinary.uploader.upload(image)
        b.image = res.get('secure_url')
    db.session.add(b)
    db.session.commit()
    return b


def check_exist_book(book_name):
    b = Book.query.filter(Book.name == book_name).first()
    return b.id


def get_all_barcode_book():
    return Book.query.with_entities(Book.barcode).all()


def add_exist_book(book_id, quantity):
    b = Book.query.get(book_id)
    b.stock_quantity += quantity
    db.session.add(b)
    db.session.commit()
    return


def reduce_book_bought(book_id, quantity):
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


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(UserRole.ADMIN))

    return u.first()


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
    u = User.query.get(user_id)
    if u and u.user_role in {UserRole.INVENTORY_MANAGER, UserRole.ADMIN, UserRole.EMPLOYEE, UserRole.MANAGE}:
        return True
    return False


# Trả về true nếu là importer, false nếu không phải
def access_check_importer(user_id):
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.INVENTORY_MANAGER:
        return True
    return False


def access_check_employee(user_id):
    u = User.query.get(user_id)
    if u and u.user_role == UserRole.EMPLOYEE:
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
def add_order_online(customer_id):
    order = Order(customer_id=customer_id)
    order.status = OrderStatus.SUCCESS
    db.session.add(order)
    db.session.commit()
    return order


def add_order_offline(customer_id):
    order = Order(customer_id=customer_id)
    order.payment_method = PaymentMethod.OFFLINE
    order.status = OrderStatus.PENDING
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


def get_all_order_with_page_size(customer_id, page=1):
    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size

    o = Order.query.filter(Order.customer_id == customer_id)
    o = o.order_by(Order.order_date.desc())
    o = o.slice(start, start + page_size)
    return o.all()


def count_order_by_customer(customer_id):
    return Order.query.filter(Order.customer_id == customer_id).count()


def get_all_order_pending():
    return Order.query.filter(Order.status == OrderStatus.PENDING).order_by(Order.order_date.desc()).all()


def get_order_by_id(order_id):
    return Order.query.get(order_id)


def set_order_success(order_id):
    o = Order.query.get(order_id)
    o.status = OrderStatus.SUCCESS
    db.session.add(o)
    db.session.commit()


def add_import_book(importer_id):
    i = Import(importer_id=importer_id)
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


def add_invoice_book(employee_id):
    i = Invoice(employee_id=employee_id)
    db.session.add(i)
    db.session.commit()
    return i


def add_invoice_detail_book(invoice_id, book_id, quantity, unit_price):
    i_detail = InvoiceDetail(invoice_id=invoice_id, book_id=book_id, quantity=quantity, unit_price=unit_price)
    db.session.add(i_detail)
    db.session.commit()
    return


def get_all_invoice_by_employee(employee_id):
    return Invoice.query.filter(Invoice.employee_id == employee_id).order_by(Invoice.created_date.desc()).all()


def get_minimun_quantity():
    regulation = Regulation.query.get(1)
    return regulation.value


def get_minimum_stock():
    regulation = Regulation.query.get(2)
    return regulation.value


def get_cancel_time():
    regulation = Regulation.query.get(3)
    return regulation.value


# Tự động hủy đơn hàng
def auto_cancel_order():
    expired_orders = Order.query.filter(Order.status == OrderStatus.PENDING).all()
    if expired_orders:  # Nếu có được list đơn hàng pending
        for order in expired_orders:  # với một đơn hàng trong list đơn hàng pending
            if order.time_to_cancel <= datetime.now():  # nếu đã vượt quá thời gian chờ thì hủy đơn
                order.status = OrderStatus.CANCEL
                for detail in order.order_detail:  # với mỗi chi tiết đơn hàng trong một đơn hàng
                    add_exist_book(book_id=detail.book_id, quantity=detail.quantity)
    db.session.commit()
    return


# Báo cáo thống kê
from sqlalchemy import func, extract


def invoice_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Book.id, Book.name, func.sum(InvoiceDetail.quantity * InvoiceDetail.unit_price)) \
        .join(InvoiceDetail, InvoiceDetail.book_id.__eq__(Book.id), isouter=True) \
        .join(Invoice, Invoice.id.__eq__(InvoiceDetail.invoice_id)) \
        .group_by(Book.id, Book.name)

    if kw:
        p.filter(Book.name.contains(kw))

    return p.all()


def order_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(
        Category.name,
        func.sum(OrderDetail.quantity * OrderDetail.unit_price).label('total_revenue')
    ).join(Book, Book.id == OrderDetail.book_id) \
        .join(Category, Category.id == Book.category_id) \
        .join(Order, Order.id == OrderDetail.order_id) \
        .filter(Order.status == 'SUCCESS') \
        .group_by(Category.name) \

    if kw:
        p.filter(Book.name.contains(kw))

    return p.all()


def get_stats_online(year, month, kw=None):
    results = db.session.query(
        Category.name.label('category_name'),
        func.sum(OrderDetail.quantity * OrderDetail.unit_price).label('revenue'),
        func.sum(OrderDetail.quantity).label('rental_count')
    ).join(Book, Book.id == OrderDetail.book_id) \
        .join(Category, Category.id == Book.category_id) \
        .join(Order, Order.id == OrderDetail.order_id) \
        .filter(
        Order.status == 'SUCCESS',
        extract('year', Order.order_date) == year,
        extract('month', Order.order_date) == month
    ).group_by(Category.name)

    # Tính tổng doanh thu
    total_revenue = sum([row.revenue for row in results])

    if kw:
        results = results.filter(Category.name.ilike(f'%{kw}%'))

    results = results.all()

    # Thêm tỷ lệ doanh thu
    report = []
    for row in results:
        percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
        report.append({
            'category_name': row.category_name,
            'revenue': row.revenue,
            'rental_count': row.rental_count,
            'percentage': percentage
        })

    return report, total_revenue


def get_stats_store(year, month, kw=None):
    results = db.session.query(
        Category.name.label('category_name'),
        func.sum(InvoiceDetail.quantity * InvoiceDetail.unit_price).label('revenue'),
        func.sum(InvoiceDetail.quantity).label('rental_count')
    ).join(Book, Book.id == InvoiceDetail.book_id) \
        .join(Category, Category.id == Book.category_id) \
        .join(Invoice, Invoice.id == InvoiceDetail.invoice_id) \
        .filter(
        extract('year', Invoice.created_date) == year,
        extract('month', Invoice.created_date) == month
    ).group_by(Category.name)

    # Tính tổng doanh thu
    total_revenue = sum([row.revenue for row in results])

    if kw:
        results = results.filter(Category.name.ilike(f'%{kw}%'))

    results = results.all()

    # Thêm tỷ lệ doanh thu
    report = []
    for row in results:
        percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
        report.append({
            'category_name': row.category_name,
            'revenue': row.revenue,
            'rental_count': row.rental_count,
            'percentage': percentage
        })

    return report, total_revenue
