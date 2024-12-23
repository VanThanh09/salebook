// Gửi form đến server, server trả về session, cập nhật div với dữ liệu session
// Thêm sách mới chưa có trong csdl
document.getElementById('importForm').addEventListener('submit', function() {

    event.preventDefault();  // Ngừng hành động mặc định của form
    const quantity = parseInt(document.getElementById('quantity').value);

    if (quantity < window.min_book_per_import) {
        // Nếu lớn hơn 150, hiển thị cảnh báo và không gửi form
        alert("Số lượng nhập phải lớn hơn " + window.min_book_per_import);
        return;  // Dừng việc gửi form
    }

    const formData = new FormData(this);  // Lấy dữ liệu từ form
    // Gửi AJAX request
    fetch('/api/add_new_book', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.status == 500) {
            alert('Mã vạch đã tồn tại vui lòng đổi mã vạch khác!')
        } else {
            return response.json()
        }
    }).then(data => {
        renderSessionData(data)
    }).catch(error => {
        console.error('Error:', error)
    });
});

// Lấy dữ liệu từ session đổ ra màn hình dù có load lại trang
window.addEventListener('load', function() {
    fetch('/api/get_session_by_session_name', {
        method: 'POST',
        body: JSON.stringify({
            'session_name': 'import_detail'
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        return response.json()
    }).then(data => {  //sesion chứa thông tin import đang làm
    // console.log(typeof data);
    // console.log(JSON.stringify(data));
        renderSessionData(data) //Hàm trong main_employee.js
    })
    .catch(error => {
        console.error('Error loading import details:', error);
    });
});


//xác nhận thêm toàn bộ sách
function commitImport() {
    fetch('/api/commit_import_book', {
        method: 'POST',
    }).then(res => {
        if(res.status === 200) {
            alert('Thêm toán bộ sách thành công');
            window.location.reload();
        } else {
            alert('Xảy ra lỗi trong quá trình thêm!!');
        }
    }).catch(error => {
        console.error('Error confirm import details:', error);
    });
}


// Hàm để tạo mã vạch ngẫu nhiên
function createRandom() {
    const randomString = Math.random().toString(36).substr(2, 10).toUpperCase();
    return randomString;
}

// Thêm sự kiện click cho nút random
document.getElementById('randomBarcodeBtn').addEventListener('click', function() {
    const barcodeField = document.getElementById('barcode');
    barcodeField.value = createRandom();
});


// Đôi form khác khi ấn nút bên thanh nav trái
function showLayout(layoutNumber) {
    var layoutNew = document.getElementById("importNewBook");
    var layoutExist = document.getElementById("importExistBook");
    if (layoutNumber == 1) { // Hiển thị form exist book
        layoutNew.classList.remove("d-flex");
        layoutExist.classList.remove("d-none");
        layoutExist.classList.add("d-flex");
        layoutNew.classList.add("d-none");
    } else {    // Hiển thị form new book
        layoutNew.classList.remove("d-none");
        layoutExist.classList.remove("d-flex");
        layoutExist.classList.add("d-none");
        layoutNew.classList.add("d-flex");
    }
}