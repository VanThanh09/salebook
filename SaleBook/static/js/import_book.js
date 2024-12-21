// Gửi form và cập nhật div với dữ liệu session
//Thêm sách mới
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
    fetch('/add_new_book', {
        method: 'POST',
        body: formData
    }).then(response => {
        return response.json()
    }).then(data => {
        if (data) {
            const importDetailsDiv = document.getElementById('importDetails');
            importDetailsDiv.innerHTML = '';  // Làm sạch div cũ
            const importDetails = data;

            Object.values(importDetails).forEach(item => {
                const bookInfo = `
                <div class="container my-3 card">
                    <div class="row d-flex card-body">
                        <div class="col-md-3 d-block">
                            <img src= "${item.image}" class="image" alt="book">
                        </div>
                        <div class="col-md-9 d-block">
                            <div class="d-flex justify-content-between w-100">
                                <h5 class="card-title text-start"><strong>${item.name}</strong></h5>
                                <p class="card-text text-muted text-end"><em>Giá: ${item.price.toLocaleString('vi-VN')} VNĐ</em></p>
                            </div>
                            <p><strong>Mô Tả:</strong> ${item.description}</p>
                            <div class="d-flex justify-content-between w-100">
                                <p class="text-start"><strong>Mã Vạch:</strong> ${item.barcode}</p>
                                <p class="text-end"><strong>Số Lượng:</strong> ${item.quantity}</p>
                            </div>
                            <div class="d-flex justify-content-between w-100">
                                <p class="text-start"><strong>Thể loại:</strong> ${item.category_id}</p>
                                <p class="text-end"><strong>Tác giả:</strong> ${item.author_id}</p>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                importDetailsDiv.innerHTML += bookInfo;  // Thêm thông tin sách vào div
            });
        }
    }).catch(error => {
        console.error('Error:', error)
    });
});

// Gửi form và cập nhật div với dữ liệu session
// Thêm sách đã có sẵn trong csdl
document.getElementById('existImportForm').addEventListener('submit', function() {
    event.preventDefault();  // Ngừng hành động mặc định của form

    const quantity = parseInt(document.getElementById('quantityExist').value);

    if (quantity < window.min_book_per_import) {
        // Nếu lớn hơn 150, hiển thị cảnh báo và không gửi form
        alert("Số lượng nhập phải lớn hơn " + window.min_book_per_import);
        return;  // Dừng việc gửi form
    }

    const formData = new FormData(this);  // Lấy dữ liệu từ form

    // Gửi AJAX request
    fetch('/add_exist_book', {
        method: 'POST',
        body: formData
    }).then(res => {
        if (res.status == 494) {
            alert('Sách này còn hơn ' + window.remaining_book_for_import + ' quyển.\n Không thể nhập!!!');
        } else {
            return res.json()
        }
    }).then(data => {
        if (data) {
            const importDetailsDiv = document.getElementById('importDetails');
            importDetailsDiv.innerHTML = '';  // Làm sạch div cũ
            const importDetails = data;

            Object.values(importDetails).forEach(item => {
                const bookInfo = `
                <div class="container my-3 card">
                    <div class="row d-flex card-body">
                        <div class="col-md-3 d-block">
                            <img src= "${item.image}" class="image" alt="book">
                        </div>
                        <div class="col-md-9 d-block">
                            <div class="d-flex justify-content-between w-100">
                                <h5 class="card-title text-start"><strong>${item.name}</strong></h5>
                                <p class="card-text text-muted text-end"><em>Giá: ${item.price.toLocaleString('vi-VN')} VNĐ</em></p>
                            </div>
                            <p><strong>Mô Tả:</strong> ${item.description}</p>
                            <div class="d-flex justify-content-between w-100">
                                <p class="text-start"><strong>Mã Vạch:</strong> ${item.barcode}</p>
                                <p class="text-end"><strong>Số Lượng:</strong> ${item.quantity}</p>
                            </div>
                            <div class="d-flex justify-content-between w-100">
                                <p class="text-start"><strong>Thể loại:</strong> ${item.category_id}</p>
                                <p class="text-end"><strong>Tác giả:</strong> ${item.author_id}</p>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                importDetailsDiv.innerHTML += bookInfo;  // Thêm thông tin sách vào div
            });
        }
    }).catch(error => {
        console.error('Error:', error)
    });
});


// cập nhật div khi load trang nếu có dữ liệu
window.addEventListener('load', function() {
    fetch('/get_session_import', {
        method: 'POST',
    }).then(response => {
        return response.json()
    }).then(data => {  //sesion chứa thông tin import đang làm
//    console.log(typeof data);
//    console.log(JSON.stringify(data));
        if (data && JSON.stringify(data) !== '{"error":"Invalid request"}') {
            const importDetailsDiv = document.getElementById('importDetails');
            importDetailsDiv.innerHTML = '';  // Làm sạch div cũ
            const importDetails = data;

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
                                <p class="text-start"><strong>Mã Vạch:</strong> ${item.barcode}</p>
                                <p class="text-end"><strong>Số Lượng:</strong> ${item.quantity}</p>
                            </div>
                            <div class="d-flex justify-content-between w-100">
                                <p class="text-start"><strong>Thể loại:</strong> ${item.category_id}</p>
                                <p class="text-end"><strong>Tác giả:</strong> ${item.author_id}</p>
                            </div>
                        </div>
                    </div>
                </div>
                `;

                importDetailsDiv.innerHTML += bookInfo;  // Thêm thông tin sách vào div
//
//                const books = document.querySelectorAll('.card');
//                books.forEach(book => {
//                    book.addEventListener('click', function() {
//                        // Lấy dữ liệu của sách khi người dùng click vào ô sách
//                        const bookData = data
//                        console.log('Thông tin sách đã chọn:', item);
//                        // Bạn có thể xử lý thông tin sách ở đây, ví dụ hiển thị lên một modal, hoặc thao tác gì đó
//                    });
//                });
            });
        }
    })
    .catch(error => {
        console.error('Error loading import details:', error);
    });
});


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


//commit import book
function commitImport() {
    fetch('/import_session_book', {
        method: 'POST',
    }).then(res => {
        if(res.status === 200) {
            alert('Thêm toán bộ sách thành công');
            window.location.reload();
        }
    });
}


//delete all import book
function deleteAllImport() {
    fetch('/clear_all_import_session', {
        method: 'POST',
    }).then(res => {
        if(res.status === 200) {
            alert('Xóa toàn bộ sách thành công');
            window.location.reload();
        }
    });
}