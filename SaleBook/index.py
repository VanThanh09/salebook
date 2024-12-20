from flask import render_template, request, redirect, jsonify, url_for, session
import dao, utils
from flask_login import login_user, logout_user, login_required, current_user
from SaleBook import app, login_manager
from SaleBook.dao import exist_user
import math
import stripe
import json

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
        user = exist_user(username)
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

    return render_template('user_process/login.html', err_msg=err_msg)


@app.route('/profile')
@login_required
def view_profile():
    orders = dao.get_order_by_customer_id(current_user.id)
    return render_template('user_process/profile.html', orders=orders)


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/admin')
@login_required
def admin():
    if dao.access_check(current_user.id):
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')
    else:
        return render_template('admin/admin.html')


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
    c_quantity = request.json.get('quantity',0)
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

    return {
        'cart_stats': utils.stats_cart(cart)
    }


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
        line_items = [] # Đại diện cho sản phẩm trong stripe, kiểu mảng dict
        metadata = {} # Thông tin bổ sung cho phiên thanh toán

        if cart:
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

        elif book:
            # Thông tin sản phẩm
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
            # Thông tin bổ sung để lấy webhook cho dễ
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
                metadata = metadata,
            )
            return jsonify({
                'checkout_url': checkout_session.url,
            })
        except Exception as e:
            return jsonify({ 'Error': str(e) }), 400

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
        total_price = sum(int(item["quantity"])*item["price"] for item in cart)

        # Tạo order và order detail
        order = dao.add_order_online(customer_id=checkout.customer_id, total_price=total_price)
        for c in cart:
            dao.add_order_detail(order_id=order.id, book_id=c["book_id"], quantity=int(c["quantity"]), unit_price=c["price"])

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


@app.route('/import_book')
@login_required
def import_book():
    if dao.check_access_import_book(current_user.id):
        categories = dao.get_all_category()
        authors = dao.get_all_author()
        return render_template('import_book.html', authors=authors, categories=categories)
    else:
        return render_template('err_auth.html', err='Bạn không có quyền truy cập')


@app.route('/add_import_detail', methods=['post'])
def add_import_detail():
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

    import_detail = session.get('import_detail')
    if not import_detail:
        import_detail = {}

    name = str(request.form.get('name'))
    price = int(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    description = request.form.get('description')
    # image = request.files.get('image')
    barcode = request.form.get('barcode')
    category_id = request.form.get('category_id')
    author_id = request.form.get('author_id')

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
            # "image": image,
            "barcode": barcode,
            "category_id": category_id,
            "author_id": author_id
        }

    session['import_detail'] = import_detail

    print(import_detail)

    # session.pop('import_detail', default=None)

    return jsonify(import_detail)

    #
    # # Kiểm tra nếu 'import_detail' chưa có trong session
    # if 'import_detail' not in session:
    #     session['import_detail'] = {}
    #
    # # Kiểm tra nếu mã vạch đã có trong session (dùng barcode làm khóa kiểm tra)
    # existing_import_id = None
    # for import_id, detail in session['import_detail'].items():
    #     if detail['barcode'] == barcode:
    #         existing_import_id = import_id
    #         break
    #
    # if existing_import_id:  # Nếu tìm thấy sản phẩm với barcode đã có
    #     # Tăng số lượng sản phẩm hiện tại
    #     session['import_detail'][existing_import_id]['quantity'] += quantity
    # else:
    #     # Nếu chưa có, tạo ID mới và lưu vào session
    #     import_id = str(len(session['import_detail']) + 1)  # Tạo import_id mới
    #     session['import_detail'][import_id] = import_detail
    #
    # # In ra session để kiểm tra
    # print(session)
    #


# @app.route('/add_import_detail', methods=['POST'])
# def add_import_detail():
#     # Lấy thông tin từ form
#     name = request.form.get('name')
#     price = int(request.form.get('price'))
#     quantity = int(request.form.get('quantity'))
#     description = request.form.get('description')
#     barcode = request.form.get('barcode')
#     category_id = request.form.get('category_id')
#     author_id = request.form.get('author_id')
#
#     # Lấy dữ liệu session, nếu không có thì tạo mới
#     import_detail = session.get('import_detail', {})
#
#     # Kiểm tra nếu đã có sách với mã vạch giống
#     if barcode in [im['barcode'] for im in import_detail.values()]:
#         return jsonify({
#             "Successfully": 40,
#             "message": "Sách đã tồn tại trong session",
#             "session": import_detail
#         })
#
#     # Thêm mới hoặc cập nhật sách
#     import_detail[name] = {
#         "name": name,
#         "price": price,
#         "quantity": quantity,
#         "description": description,
#         "barcode": barcode,
#         "category_id": category_id,
#         "author_id": author_id
#     }
#
#     # Cập nhật session
#     session['import_detail'] = import_detail
#
#     return jsonify({
#         "Successfully": 1,
#         "session": import_detail
#     })

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=8000)
