// Thêm một sản phẩm vô cart
// book_detail.html
function addToCart(book_id, customer_id) {
        fetch("/api/carts", {
            method: "POST",
            body: JSON.stringify({
                "book_id": book_id,
                "customer_id": customer_id,
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => {
            if(res.status === 401) {
                window.location.href = '/login'
            } else {
                return res.json();
            }
        }).then(data => {
            let items = document.getElementsByClassName("cart-counter");
            for (let item of items)
                item.innerText = data.total_quantity;
        });
}


//xóa một sản phẩm khỏi cart
//cart.html
function removeCart(cart_id) {
    console.log('helo')
    fetch("/api/remove_cart", {
        method: 'POST',
        body: JSON.stringify({
            "cart_id": cart_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 400) {
            alert("Không có sản phẩm nào để xóa.");
            throw new Err("Bad Request: No product to delete.");

        }else {
            return res.json();
        }
    }).then(data => {
//            alert("Sản phẩm đã được xóa khỏi giỏ hàng.");
            window.location.reload();
    }).catch(err => {
        console.error("Fetch error:", err);
        alert("Có lỗi xảy ra khi xóa sản phẩm!!!");
    });
}


// Thay đổi số lượng sản phẩm trong cart
// cart.html
function changeCart(cart_id, quantity, customer_id, stock_quantity) {
    if (quantity > stock_quantity) {
        alert('Số lượng tối đa còn lại là ' + stock_quantity + '\nXin lỗi vì sự bất tiện này')
        document.getElementById(cart_id).value = stock_quantity;
        quantity = stock_quantity;
    }

    if (quantity < 0) {
        alert('Số lượng tối thiểu là 1\nHãy xóa sản phẩm nếu bạn không muốn mua')
        document.getElementById(cart_id).value = 0;
        quantity = 0;
    }

    fetch("/api/change_cart", {
        method: 'POST',
        body: JSON.stringify({
            "cart_id": cart_id,
            "quantity": quantity,
            "customer_id": customer_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 400) {
            alert("Không có sản phẩm nào để xóa.");
            throw new Err("Bad Request: No product to delete.");
        }else {
            return res.json();
        }
    }).then(data => {
        let items = document.getElementsByClassName("cart-counter");

        for (let item of items)
            item.innerText = data.total_quantity;

        document.getElementById("iii").innerText = data.total_quantity;
        document.getElementById("cart-total-amount").value = data.total_amount.toLocaleString() + "VNĐ";


//        window.location.reload();
    });
}


function isAuthUser() {
    fetch("/api/carts", {
            method: "POST",
        }).then(res => {
            if(res.status === 401) {
                window.location.href = '/login'
            } else {
                return
            }
        })
}


// Mua sản phẩm với stripe
//bood_id và quantity là mua ở trong book_detail
// customer_id là mua trong cart
function payment(book_id, quantity, customer_id) {
    fetch("/create-checkout-session", {
        method: 'POST',
        body: JSON.stringify({
            "book_id": book_id,
            "quantity": quantity,
            "customer_id": customer_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 401) {
            window.location.href = '/login'
        } else {
            return res.json(); // chuyêển res thành đối tượng js
        }
    }).then(result => {
        window.location.href = result.checkout_url
    });
}

function demo() {
    console.log('1')
}

