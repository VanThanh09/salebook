// Đưa dữ liệu trả về từ server ra thẻ div
// Đưa dữ liệu trả: session[session_name]
function renderSessionData(data) {
//     console.log(typeof data);
//     console.log(JSON.stringify(data));
    if (data && JSON.stringify(data) !== '{"error":"Invalid request"}') {
        const importDetailsDiv = document.getElementById('importDetails');
        importDetailsDiv.innerHTML = '';  // Làm sạch div cũ
        const importDetails = data;
        var totalPrice = 0;
        Object.values(importDetails).forEach(item => {
            const bookInfo = `
            <div class="container my-3 card">
                <div class="row d-flex card-body">
                    <div class="col-md-3 d-block">
                        <img src="${item.image}" class="image" alt="book">
                    </div>
                    <div class="col-md-9 d-block">
                        <div class="d-flex justify-content-between w-100">
                            <h5 class="card-title text-start"><strong>${item.name}</strong></h5>
                            <p class="card-text text-muted text-end"><em>Giá: ${item.price.toLocaleString('vi-VN')} VNĐ</em></p>
                        </div>
                        <p><strong>Mô Tả:</strong> ${item.description}</p>
                        <div class="d-flex justify-content-between w-100">
                            <p><strong>Mã Vạch:</strong> ${item.barcode}</p>
                            <p><strong>Thể loại:</strong> ${item.category_id}</p>
                        </div>
                        <div class="d-flex justify-content-between w-100">
                            <p><strong>Số Lượng:</strong> ${item.quantity}</p>
                            <p><strong>Tác giả:</strong> ${item.author_id}</p>
                        </div>
                    </div>
                </div>
            </div>
            `;
            totalPrice = totalPrice + (item.quantity*item.price);

            importDetailsDiv.innerHTML += bookInfo;  // Thêm thông tin sách vào div
        });
        document.getElementById('totalPriceInvoice').innerText = totalPrice.toLocaleString('vi-VN') + " VNĐ";
    }
}


// Gửi form đến server, server trả về session, cập nhật div với dữ liệu session
// Thêm sách đã có sẵn trong csdl
document.getElementById('existImportForm').addEventListener('submit', function() {
    event.preventDefault();  // Ngừng hành động mặc định của form

    const quantity = parseInt(document.getElementById('quantityExist').value);
    if (window.min_book_per_import) {
        if (quantity < window.min_book_per_import) {
        // Nếu lớn hơn 150, hiển thị cảnh báo và không gửi form
        alert("Số lượng nhập phải lớn hơn " + window.min_book_per_import);
        return;  // Dừng việc gửi form
        }
    }

    const formData = new FormData(this);  // Lấy dữ liệu từ form

    // Gửi AJAX request
    fetch('/api/add_exist_book', {
        method: 'POST',
        body: formData
    }).then(res => {
        if (res.status == 494) {
            alert('Sách này còn hơn ' + window.remaining_book_for_import + ' quyển.\n Không thể nhập!!!');
            return
        }
        if (res.status == 500) {
            alert('Số lượng sách bán lớn hơn số lượng sách tồn kho');
            return
        }
        return res.json()
    }).then(data => {
        renderSessionData(data)
    }).catch(error => {
        console.error('Error:', error)
    });
});


//xóa toàn bộ sách đang lưu trong session theo key ( invoice_detail, import_detail)
function deleteAllBySessionName(session_name) {
    fetch('/api/clear_all_by_session_name', {
        method: 'POST',
        body: JSON.stringify({
            'session_name': session_name
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 200) {
            alert('Xóa toàn bộ sách thành công');
            window.location.reload();
        }
    });
}


window.addEventListener('beforeunload', function(event) {
    // Dừng camera trước khi người dùng rời trang hoặc đóng cửa sổ
});


// Lọc sách theo tên trong giao diện nhân viên
function filterBooks() {
    // Lấy giá trị từ ô input tìm kiếm
    let input = document.getElementById('searchBook');
    let filter = input.value.toLowerCase();  // Chuyển đổi thành chữ thường
    let select = document.getElementById('existBook');
    let options = select.getElementsByTagName('option');

    // Duyệt qua tất cả các mục trong dropdown và kiểm tra xem có chứa từ khóa tìm kiếm hay không
    for (let i = 0; i < options.length; i++) {
        let optionText = options[i].textContent || options[i].innerText; // Lấy văn bản của mỗi option
        if (optionText.toLowerCase().includes(filter)) {
            options[i].style.display = ''; // Hiển thị nếu tìm thấy từ khóa
        } else {
            options[i].style.display = 'none'; // Ẩn nếu không tìm thấy
        }
    }
}

