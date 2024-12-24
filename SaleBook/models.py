from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Double, Date
from sqlalchemy.orm import relationship

from SaleBook import db, app
from enum import Enum as ClassEnum
from flask_login import UserMixin


class UserRole(ClassEnum):
    ADMIN = 1
    CUSTOMER = 2
    EMPLOYEE = 3
    INVENTORY_MANAGER = 4
    MANAGE = 5


class PaymentMethod(ClassEnum):
    ONLINE = 1
    OFFLINE = 2


class OrderStatus(ClassEnum):
    PENDING = 1  # Chờ lấy hàng
    SUCCESS = 2  # Thành công
    CANCEL = 3  # Đã hủy


class Regulation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)


class User(db.Model, UserMixin):
    # __tablename__ = ''

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True)
    phone_number = Column(String(12))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String(150),
                    default='https://res.cloudinary.com/drzc4fmxb/image/upload/v1733907010/xvethjfe9cycrroqi7po.jpg')
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    cart = relationship('Cart', lazy='subquery', cascade='all, delete-orphan')

    def __str__(self):
        return self.name


class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Double, default=0)
    stock_quantity = Column(Integer, default=0)
    description = Column(String(255), nullable=True)
    image = Column(String(150),
                   default='https://res.cloudinary.com/drzc4fmxb/image/upload/v1733048058/tkk9qbfthr5uzpnymx56.jpg')
    barcode = Column(String(50), unique=True, nullable=True)

    category = relationship('Category', backref='books', lazy=True)
    author = relationship('Author', backref='books', lazy=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)

    def __str__(self):
        return self.name


class Author(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Order(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(DateTime, default=datetime.now)
    status = Column(Enum(OrderStatus))
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.ONLINE)

    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    customer = relationship('User', backref='orders', lazy='subquery')
    order_detail = relationship('OrderDetail', backref='order', lazy='subquery', cascade='all, delete-orphan')

    @property
    def total_price(self):
        total_price = 0
        for detail in self.order_detail:
            total_price += detail.sub_total
        return total_price

    @property
    def time_to_cancel(self):
        if self.status.name == 'PENDING':
            regulation = Regulation.query.get(3).value
            # Giả sử thời gian hết hạn là 24 giờ sau khi đơn hàng được tạo
            expiry_time = self.order_date + timedelta(hours=regulation)
            return expiry_time
        return None


class OrderDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Double, nullable=False, default=0)

    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)

    book = relationship('Book')

    @property
    def sub_total(self):
        return self.quantity * self.unit_price


class Import(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    import_date = Column(DateTime, default=datetime.now())

    importer_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    importer = relationship('User', backref='imports', lazy=True)
    import_detail = relationship('ImportDetail', backref='import', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        total_price = 0
        for detail in self.import_detail:
            total_price += detail.sub_total
        return total_price


class ImportDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Double, nullable=False, default=0) # Tương lai tăng giá sách thì sao

    import_id = Column(Integer, ForeignKey('import.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)

    book = relationship('Book')

    @property
    def sub_total(self):
        return self.quantity * self.unit_price


class Invoice(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now)

    customer_id = Column(Integer, ForeignKey('user.id'))
    employee_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    employee = relationship('User', backref='invoice_employees', lazy=True, foreign_keys=[employee_id])
    customer = relationship('User', backref='invoice_customers', lazy=True, foreign_keys=[customer_id])
    invoice_detail = relationship('InvoiceDetail', backref='invoice', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        total_price = 0
        for detail in self.invoice_detail:
            total_price += detail.sub_total
        return total_price


class InvoiceDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Double, nullable=False, default=0)

    invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)

    books = relationship('Book', lazy=True)

    @property
    def sub_total(self):
        return self.quantity * self.unit_price


class Cart(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, default=1)

    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    books = relationship('Book', lazy='subquery')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # r1 = Regulation(name='Số lượng nhập tối thiểu', value=150)
        # r2 = Regulation(name='Nhập những đầu sách có số lượng ít hơn', value=300)
        # r3 = Regulation(name='Giờ hủy đơn', value=48)
        # db.session.add(r1)
        # db.session.add(r2)
        # db.session.add(r3)



        # import hashlib
        # importer = User(name='Admin', username = 'admin', password=str(hashlib.md5('123'.strip().encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN)
        # db.session.add(importer)

        # cus = User.query.get(1)
        # for cart_item in cus.cart:
        #     print(f'{cart_item.books}__{cart_item.quantity}')

        # author = Author(name='J. K. Rowling',description='J. K. Rowling là một nhà văn, nhà biên kịch người Anh')
        # category = Category(name='Novel')
        #
        # db.session.add(author)
        # db.session.add(category)
        #
        # db.session.commit()
        #
        # data = [
        #     {
        #         "name": "Harry Potter",
        #         "price": 17000000,
        #         "stock_quantity": 20,
        #         "description": "Bộ truyện viết về những cuộc phiêu lưu phù thủy của cậu bé Harry Potter cùng hai người bạn thân là Ron Weasley và Hermione Granger",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "Lord of the Rings",
        #         "price": 15000000,
        #         "stock_quantity": 15,
        #         "description": "Một câu chuyện thần thoại đầy hấp dẫn của J.R.R. Tolkien về cuộc chiến chống lại thế lực hắc ám Sauron.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "The Great Gatsby",
        #         "price": 200000,
        #         "stock_quantity": 50,
        #         "description": "Tác phẩm kinh điển của F. Scott Fitzgerald mô tả cuộc sống giàu có và đau khổ ở thập kỷ 1920.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "To Kill a Mockingbird",
        #         "price": 300000,
        #         "stock_quantity": 40,
        #         "description": "Cuốn sách đoạt giải Pulitzer của Harper Lee về cuộc đấu tranh chống phân biệt chủng tộc.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "1984",
        #         "price": 350000,
        #         "stock_quantity": 30,
        #         "description": "George Orwell vẽ ra một thế giới dystopian đầy ám ảnh.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "Pride and Prejudice",
        #         "price": 250000,
        #         "stock_quantity": 25,
        #         "description": "Tác phẩm lãng mạn nổi tiếng của Jane Austen kể về tình yêu và sự hiểu lầm.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "Moby Dick",
        #         "price": 450000,
        #         "stock_quantity": 10,
        #         "description": "Hành trình đầy bi kịch và phiêu lưu của thuyền trưởng Ahab do Herman Melville kể.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/lik7dt77bsptgg5eakgq.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "The Catcher in the Rye",
        #         "price": 300000,
        #         "stock_quantity": 20,
        #         "description": "Cuốn tiểu thuyết của J.D. Salinger về sự nổi loạn tuổi trẻ.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "War and Peace",
        #         "price": 700000,
        #         "stock_quantity": 12,
        #         "description": "Một tác phẩm vĩ đại của Leo Tolstoy về cuộc chiến và tình yêu ở nước Nga.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/qctxm4xjuiuy5axe767q.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     },
        #     {
        #         "name": "Crime and Punishment",
        #         "price": 500000,
        #         "stock_quantity": 18,
        #         "description": "Dostoevsky viết về tội ác và sự cứu chuộc đầy triết lý và sâu sắc.",
        #         "image": 'https://res.cloudinary.com/drzc4fmxb/image/upload/v1734077860/g0b1ypwqdp3ron415wcv.jpg',
        #         "category_id": 1,
        #         "author_id": 1
        #     }
        # ]
        #
        # for b in data:
        #     book = Book(**b)
        #     db.session.add(book)

        db.session.commit()

