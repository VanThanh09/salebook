// Lấy dữ liệu từ session đổ ra màn hình dù có load lại trang
window.addEventListener('load', function() {

    fetch('/api/get_session_by_session_name', {
        method: 'POST',
        body: JSON.stringify({
            'session_name': 'invoice_detail'
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


function commitInvoice() {
    fetch('/api/commit_invoice_book', {
        method: 'POST',
    }).then(res => {
        if (res.status == 200) {
            alert('Đã thêm hóa đơn thành công');
            window.location.reload();
        } else {
            alert('Xảy ra lỗi trong quá trình thêm!!');
        }
    }).catch(error => {
        console.log('error: ',error);
    });
}


//Camera quét mã vạch
// Sự kiện quét thành công
function onScanSuccess(decodedText, decodedResult) {
    document.getElementById('barcode').value = decodedText;

    let input = document.getElementById('barcode').value;
    let select = document.getElementById('existBook');
    let options = select.getElementsByTagName('option');
    let quantity = document.getElementById('quantityExist');

    let found = false;
    for (let option of options) {
        if (option.dataset.barcode === input) {
            options[0].selected = false;
            option.selected = true;
            quantity.value = 1;
            found = true;
        } else {
            option.selected = false;
        }
    }
    if (!found) {
        quantity.value = '';
        options[0].selected = true;
    }
}

//Quét thất bại
function onScanFailure(error) {
    console.error('error scan: ', error);
}

// Bắt sự kiện khi trang bị đóng hoặc người dùng thoát (đóng tab)
window.addEventListener('beforeunload', function(event) {
    // Dừng camera trước khi người dùng rời trang hoặc đóng cửa sổ
});

// Khởi chạy html5-qrcode
let html5QrcodeScanner = new Html5QrcodeScanner(
    "scanner", { fps: 10, qrbox: 250 }
);
html5QrcodeScanner.render(onScanSuccess, onScanFailure);

