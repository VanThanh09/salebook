from flask import render_template, request, redirect, jsonify, url_for, session

from SaleBook.admin import *
import dao, utils
from flask_login import login_user, logout_user, login_required, current_user
from SaleBook import app, login_manager
import math
import stripe
import json
import os
from SaleBook.models import UserRole

endpoint_secret = 'whsec_PPI1L0c1djpR8XXd08RbEKQzoBJE6Ppe'

login_manager.login_view = "/login"


@app.route("/")
def home():
    kw = request.args.get('search_query')
    page = request.args.get('page', 1)

    books = dao.load_book(kw=kw, page=int(page))

    total = dao.count_books()
    page_size = app.config['PAGE_SIZE']
    return render_template('index.html', books=books, pages=math.ceil(total / page_size), page=int(page))


@app.route('/errauth')
def err_auth():
    return render_template('err_auth.html')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.check_exist_user(username)
        if not username or not password:
            err_msg = 'Vui lòng điền username và password!!'
        elif user:
            err_msg = 'Username đã tồn tại. Vui lòng đổi username khác!'
        else:
            confirm = request.form.get('confirm')
            if password.__eq__(confirm):
                data = request.form.copy()
                del data['confirm']

                dao.add_customer(avatar=request.files.get('avatar'), **data)

                return redirect('/login')
            else:
                err_msg = 'Mật khẩu không khớp!'

    return render_template('user_process/register.html', err_msg=err_msg)


@app.route("/login", methods=['get', 'post'])
def login_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = 'Sai thông tin tài khoản mật khẩu!'
            # print(user)
    return render_template('user_process/login.html', s="")


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user)

    return redirect('/admin')


@app.route('/profile')
@login_required
def view_profile():
    page = int(request.args.get('page', 1))
    total = dao.count_order_by_customer(customer_id=current_user.id)
    page_size = app.config['PAGE_SIZE']

    orders = dao.get_all_order_with_page_size(customer_id=current_user.id, page=int(page))

    return render_template('user_process/profile.html', orders=orders, pages=math.ceil(total / page_size), page=page)


@app.route('/logout')
def logout_process():
    session.clear()
    logout_user()
    return redirect('/')


@login_manager.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/<book_name>')
def product_detail(book_name):
    book_id = request.args.get('book_id')
    book = dao.get_book_by_id(book_id)
    if book:
        return render_template('book_detail.html', book=book)
    else:
        return render_template('err_auth.html', err='Url này có vẻ không tồn tại!')


@app.route('/api/carts', methods=['POST'])
def add_to_cart_api():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401  # Nếu người dùng chưa đăng nhập

    book_id = request.json.get('book_id')
    customer_id = request.json.get('customer_id')
    quantity = request.json.get('quantity', 1)

    if not book_id or not customer_id or quantity < 1:
        return jsonify({"error": "Invalid data"}), 400  # Kiểm tra dữ liệu hợp lệ

    dao.add_to_cart(customer_id=customer_id, book_id=book_id, quantity=quantity)

    cart = dao.get_all_cart(customer_id)

    return jsonify(utils.stats_cart(cart))


@app.route('/cart')
@login_required
def view_cart_detail():
    cart = dao.get_all_cart(current_user.id)
    return render_template('payment/cart.html', cart=cart)


@app.route('/api/remove_cart', methods=['POST'])
def remove_cart():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401  # Nếu người dùng chưa đăng nhập

    c_id = request.json.get('cart_id')

    if not c_id:
        return jsonify({"error": "Invalid data"}), 400  # Kiểm tra dữ liệu hợp lệ

    dao.remove_cart_by_id(c_id)

    return jsonify({'message': 'successfully'})


@app.route('/api/change_cart', methods=['POST'])
def chang_cart():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401  # Nếu người dùng chưa đăng nhập

    cart_id = request.json.get('cart_id')
    c_quantity = request.json.get('quantity', 0)
    customer_id = request.json.get('customer_id')

    if not cart_id:
        return jsonify({"error": "Invalid data"}), 400  # Kiểm tra dữ liệu hợp lệ

    dao.change_cart_quantity(cart_id=cart_id, quantity=c_quantity)
    cart = dao.get_all_cart(customer_id)

    return jsonify(utils.stats_cart(cart))


@app.context_processor
def common_response():
    if current_user.is_authenticated:
        cart = dao.get_all_cart(current_user.id)
    else:
        cart = {}

    if current_user.is_authenticated:
        dashboard = ''
        if dao.access_check_importer(current_user.id):
            dashboard = '/import_book'
        if dao.access_check_employee(current_user.id):
            dashboard = '/sale_book'
        if dao.access_check_admin(current_user.id):
            dashboard = '/admin'

        if dashboard:
            return {
                'cart_stats': utils.stats_cart(cart),
                'dashboard': dashboard
            }

    return {
        'cart_stats': utils.stats_cart(cart)
    }


@app.route('/api/checkout_in_store', methods=['POST'])
def checkout_in_store():
    """
    Tạo order tự hết hạn sau giờ quy định
    :return:
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401  # Nếu người dùng chưa đăng nhập

    if request.method.__eq__('POST'):
        # Lấy thông tin từ post tạo đối tượng cần thiết
        book_id = request.json.get('book_id')
        customer_id = request.json.get('customer_id')

        book = dao.get_book_by_id(book_id=book_id)
        cart = dao.get_all_cart(customer_id=customer_id)

        if cart:
            order = dao.add_order_offline(customer_id=current_user.id)
            for c in cart:
                dao.add_order_detail(order_id=order.id, book_id=c.book_id, quantity=c.quantity,
                                     unit_price=dao.get_book_by_id(c.book_id).price)
                dao.reduce_book_bought(book_id=c.book_id, quantity=c.quantity)
            dao.remove_all_cart_by_userid(current_user.id)
            return jsonify({'success': 'Đơn hàng đã được ghi nhận'}), 200

        elif book:
            quantity = request.json.get('quantity')
            order = dao.add_order_offline(customer_id=current_user.id)
            dao.add_order_detail(order_id=order.id, book_id=book.id, quantity=quantity,
                                 unit_price=book.price)
            dao.reduce_book_bought(book_id=book.id, quantity=quantity)
            print(order.time_to_cancel)
            return jsonify({'success': 'Đơn hàng đã được ghi nhận'}), 200

        else:
            return jsonify({'error': 'Invalid'}), 404
    else:
        return jsonify({'error': 'Invalid request'}), 404


@app.route('/api/commit_checkout_offline', methods=['POST'])
@login_required
def commit_checkout_offline():
    """
    xác nhận lấy đơn thanh toán tại cửa hàng thành công để dừng quá trình hết hạn
    :return:
    """
    if dao.access_check_employee(current_user.id):
        order_id = request.json.get('order_id')
        dao.set_order_success(order_id)
        return jsonify({'success': 'Thành công'}), 200
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/order_pending')
@login_required
def order_pending():
    """
    Lấy danh sách các order đang chờ
    :return:
    """
    if dao.access_check_employee(current_user.id):
        search = request.args.get('search_order')
        not_found = ''
        if search:
            orders = dao.get_order_by_id(int(search))
            if not orders:
                not_found = 'Không tìm thấy đơn hàng'
                orders = dao.get_all_order_pending()
        else:
            orders = dao.get_all_order_pending()

        return render_template('employee/order_pending.html', orders=orders, not_found=not_found)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Nhận (book_id, quantity, customer_id)

    Tham số: (book_id, quantity, null)= Chức năng mua ngay trong book_detail
    Tham số: (null, null, customer_id)= Chức năng thanh toán trong giỏ hàng

    """
    # xác thực đăng nhập
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401  # Nếu người dùng chưa đăng nhập

    if request.method.__eq__('POST'):

        # Lấy thông tin từ post tạo đối tượng cần thiết
        book_id = request.json.get('book_id')
        quantity = request.json.get('quantity')
        customer_id = request.json.get('customer_id')

        book = dao.get_book_by_id(book_id)
        cart = dao.get_all_cart(customer_id)
        cart = [c for c in cart if c.quantity != 0]
        line_items = []  # Đại diện cho sản phẩm trong stripe, kiểu mảng dict
        metadata = {}  # Thông tin bổ sung cho phiên thanh toán

        if cart:  # Thanh toán cart
            for c in cart:
                line_items.append({
                    'price_data': {
                        'currency': 'vnd',
                        'product_data': {
                            'name': c.books.name,
                            'description': c.books.description,
                            'images': [c.books.image],

                        },
                        'unit_amount': int(c.books.price),
                    },
                    'quantity': c.quantity,
                })

            cart_details = [{
                'book_id': c.books.id,
                'quantity': c.quantity,
                'price': c.books.price
            } for c in cart]

            # Lưu chuỗi JSON vào metadata
            metadata = {
                'customer_id': customer_id,
                'cart': json.dumps(cart_details),  # Chuyển đổi mảng thành chuỗi JSON
                'is_cart': 1
            }

        elif book:  # Mua ngay trong sản phầm
            line_items.append({
                'price_data': {
                    'currency': 'vnd',
                    'product_data': {
                        'name': book.name,
                        'description': book.description,
                        'images': [book.image],
                    },
                    'unit_amount': int(book.price),
                },
                'quantity': quantity,
            })

            cart_details = [{
                'book_id': book.id,
                'quantity': quantity,
                'price': book.price
            }]
            metadata = {
                'customer_id': current_user.id,
                'cart': json.dumps(cart_details),
                'is_cart': 0
            }

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=url_for('success', _external=True),
                cancel_url=url_for('cancel', _external=True),
                metadata=metadata,
            )
            return jsonify({
                'checkout_url': checkout_session.url,
            })
        except Exception as e:
            return jsonify({'Error': str(e)}), 400
    else:
        return jsonify({'error': 'Invalid request'}), 404


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print('Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Sự kiện phiên thanh tóan thành công
    if event and event['type'] == 'checkout.session.completed':
        # Lấy chuỗi dict đã gửi lên từ trước đó
        checkout = event['data']['object']['metadata']
        cart = json.loads(checkout.cart)

        # Tạo order và order detail
        order = dao.add_order_online(customer_id=checkout.customer_id)
        for c in cart:
            dao.add_order_detail(order_id=order.id, book_id=c["book_id"], quantity=int(c["quantity"]),
                                 unit_price=c["price"])

        # Giảm số lượng hàng tồn kho
        for c in cart:
            dao.reduce_book_bought(book_id=c["book_id"], quantity=int(c["quantity"]))

        # Xóa rỗng giỏ hàng
        if int(checkout["is_cart"]) == 1:
            dao.remove_all_cart_by_userid(checkout['customer_id'])

    else:
        # Unexpected event type
        print('{}'.format(event['type']))

    return jsonify(success=True)


@app.route('/success')
def success():
    return render_template('payment/success.html')


@app.route('/cancel')
def cancel():
    return render_template('payment/cancel.html')


@app.route('/import_book', endpoint='import_books')
@login_required
def import_book():
    if dao.access_check_importer(current_user.id):
        categories = dao.get_all_category()
        authors = dao.get_all_author()
        books = dao.get_all_book()
        min_book_per_import = dao.get_minimun_quantity()
        remaining_book_for_import = dao.get_minimum_stock()
        return render_template('importer/import_book.html', authors=authors, categories=categories, books=books,
                               min_book_per_import=min_book_per_import,
                               remaining_book_for_import=remaining_book_for_import)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/api/add_new_book', methods=['post'])
@login_required
def add_new_book():
    """
    {
        "1": {
            "id": "1",
            "name": "..",
            "price": 123,
            "quantity": 2,
            "description": "..",
            "image": "https://..",
            "barcode": "..",
            "category_id": 1,
            "author_id": 1,
        }, "2": {
            "id": "1",
            "name": "..",
            "price": 123,
            "quantity": 2,
            "description": "..",
            "image": "https://..",
            "barcode": "..",
            "category_id": 1,
            "author_id": 1,
        }
    }
    """

    if dao.access_check(current_user.id):
        session_name = request.form.get('session_name')
        import_detail = session.get(session_name)
        if not import_detail:
            import_detail = {}

        # Lấy toàn bộ barcode đã tồn tại và barcode trong form để so sánh
        barcodes = dao.get_all_barcode_book()
        barcode = request.form.get('barcode')

        for b in barcodes:
            if b[0] == barcode:
                return jsonify({'error': 'barcode existed'}), 500

        name = str(request.form.get('name'))
        price = int(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        author_id = request.form.get('author_id')
        is_new = request.form.get('is_new')

        image = request.files.get('image')

        image.save(os.path.join(app.root_path, 'static/uploads/', image.filename))

        image_url = 'static/uploads/' + image.filename

        # for import_id, im in import_detail.items():  # Lặp qua các item trong dictionary
        #     if barcode == im["barcode"]: # Kiểm tra nếu barcode trùng
        #         return jsonify({
        #             "Successfully": 40,
        #             "session": session.get('import_detail')
        #         })

        if name in import_detail:
            import_detail[name]["quantity"] += quantity
        else:
            import_detail[name] = {
                "name": name,
                "price": price,
                "quantity": quantity,
                "description": description,
                "image": image_url,
                "barcode": barcode,
                "category_id": category_id,
                "author_id": author_id,
                "is_new": is_new
            }

        session[session_name] = import_detail

        return jsonify(import_detail)
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/api/add_exist_book', methods=['post'])
@login_required
def add_exist_book():
    """
    Thêm sách đã có trong cơ sở dữ liệu vào session
    session_name: thêm cho mục nào đó (bán sách, nhập sách), đặt ẩn trong form
    :return:
    """

    if dao.access_check(current_user.id):
        session_name = request.form.get('session_name')
        # print(session_name)
        details = session.get(session_name)
        if not details:
            details = {}

        book_id = request.form.get('book_id')
        # print(book_id)
        b = dao.get_book_by_id(book_id)
        book_id = str(b.id)

        # Kiểm tra  quy định số lượng còn lại thì nhập
        if session_name == 'import_detail':

            if b.stock_quantity > dao.get_minimum_stock():
                return jsonify({'message': 'failed'}), 494

        # Kiểm tra số lượng bán ra nhỏ hơn trong kho
        if session_name == 'invoice_detail':
            if b.stock_quantity < int(request.form.get('quantity')):
                return jsonify({'message': 'failed'}), 500
            if book_id in details:
                if details[book_id]["quantity"] + int(request.form.get('quantity')) > b.stock_quantity:
                    return jsonify({'message': 'failed'}), 500

        if b:
            name = b.name
            price = b.price
            quantity = int(request.form.get('quantity'))
            description = b.description
            image = b.image
            barcode = b.barcode
            category_id = b.category_id
            author_id = b.author_id
            is_new = request.form.get('is_new')

            if book_id in details:
                details[book_id]["quantity"] += quantity
            else:
                details[book_id] = {
                    "book_id": book_id,
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "description": description,
                    "image": image,
                    "barcode": barcode,
                    "category_id": category_id,
                    "author_id": author_id,
                    "is_new": is_new
                }

            session[session_name] = details
            # print(details)
            return jsonify(details)
        else:
            return jsonify({'message': 'failed'}), 400
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/api/commit_import_book', methods=['post'])
@login_required
def commit_import_book():
    """
    lấy thông tin từ session
    tạo import
    thêm thông tin sách từ session vào csdl
    tạo import_detail
    :return:
    """
    # tính total price
    if dao.access_check_importer(current_user.id):

        imp = dao.add_import_book(importer_id=current_user.id)
        for key in session['import_detail']:
            import_detail = session['import_detail'][key]
            if int(import_detail['is_new']) == 0:
                dao.add_exist_book(book_id=import_detail['book_id'], quantity=import_detail['quantity'])
                dao.add_import_detail_book(quantity=import_detail['quantity'], unit_price=import_detail['price'],
                                           import_id=imp.id, book_id=import_detail['book_id'])

            if int(import_detail['is_new']) == 1:
                b = dao.add_new_book(name=import_detail['name'], price=import_detail['price'],
                                     quantity=import_detail['quantity'], description=import_detail['description'],
                                     barcode=import_detail['barcode'], category_id=import_detail['category_id'],
                                     author_id=import_detail['author_id'], image=import_detail['image'])
                dao.add_import_detail_book(quantity=import_detail['quantity'], unit_price=import_detail['price'],
                                           import_id=imp.id, book_id=b.id)
                os.remove(import_detail['image'])

        del session['import_detail']
        return jsonify({'message': 'successfully'}), 200
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/api/clear_all_by_session_name', methods=['post'])
@login_required
def clear_all_by_session_name():
    if dao.access_check(current_user.id):
        session_name = request.json.get('session_name')
        if session[session_name]:
            for key in session[session_name]:
                details = session[session_name][key]
                if int(details['is_new']) == 1:
                    try:
                        os.remove(details['image'])
                    except FileNotFoundError:
                        print("File không tồn tại.")
            del session[session_name]
            return jsonify({'message': 'successfully'}), 200
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/api/get_session_by_session_name', methods=['post'])
@login_required
def get_session_import():
    if dao.access_check(current_user.id):
        session_name = request.json.get('session_name')
        import_detail = session.get(session_name)
        if import_detail:
            return import_detail
        else:
            return jsonify({'error': 'Invalid request'}), 404
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/add_author', methods=['get', 'post'])
@login_required
def add_author():
    if dao.access_check_importer(current_user.id):
        s = ''
        if request.method.__eq__('POST'):
            name = request.form.get('name')
            description = request.form.get('description')
            dao.add_author(name, description)
            s = "Thêm tác giả thành công"
            return render_template('add_author.html', successfully=s)

        return render_template('importer/add_author.html')
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/add_category', methods=['get', 'post'])
@login_required
def add_category():
    if dao.access_check_importer(current_user.id):
        s = ''
        if request.method.__eq__('POST'):
            name = request.form.get('name')
            description = request.form.get('description')
            dao.add_category(name, description)
            s = "Thêm danh mục thành công"
            return render_template('importer/add_category.html', successfully=s)

        return render_template('importer/add_category.html')
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/import_history')
@login_required
def view_import_history():
    if dao.access_check_importer(current_user.id):
        imps = dao.get_all_import_by_importer(current_user.id)
        return render_template('importer/import_history.html', imps=imps)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/sale_book')
@login_required
def sale_book():
    if dao.access_check_employee(current_user.id):
        books = dao.get_all_book()
        return render_template('employee/sale_book.html', books=books)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/api/commit_invoice_book', methods=['post'])
@login_required
def commit_invoice_book():
    """
    lấy thông tin từ session
    tạo invoice
    thêm thông tin sách từ session vào csdl
    tạo invoice_detail
    :return:
    """
    if dao.access_check_employee(current_user.id):

        invoice = dao.add_invoice_book(employee_id=current_user.id)
        for key in session['invoice_detail']:
            invoice_detail = session['invoice_detail'][key]
            if int(invoice_detail['is_new']) == 0:
                dao.reduce_book_bought(book_id=invoice_detail['book_id'], quantity=invoice_detail['quantity'])
                dao.add_invoice_detail_book(invoice_id=invoice.id, book_id=invoice_detail['book_id'],
                                            unit_price=invoice_detail['price'], quantity=invoice_detail['quantity'])

        del session['invoice_detail']
        return jsonify({'message': 'successfully'}), 200
    else:
        return jsonify({'message': 'failed'}), 400


@app.route('/sale_history')
@login_required
def sale_history():
    if dao.access_check_employee(current_user.id):
        invoices = dao.get_all_invoice_by_employee(current_user.id)
        return render_template('employee/sale_history.html', invoices=invoices)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


import threading
import time

import schedule


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def cancel_order_with_app_context():
    with app.app_context():
        dao.auto_cancel_order()


schedule.every(1).minute.do(cancel_order_with_app_context)

stop_run_continuously = run_continuously()

if __name__ == "__main__":
    try:
        with app.app_context():
            app.run(debug=True)
    finally:
        stop_run_continuously.set()

# app.run(debug=True, host='0.0.0.0', port=8000)
