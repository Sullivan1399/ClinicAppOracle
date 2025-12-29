// Khởi tạo API
const deptApi = new ClinicAPI('http://127.0.0.1:8000'); // Sửa port nếu cần

document.addEventListener('DOMContentLoaded', () => {
    loadDepartments();

    // Xử lý Submit Form
    const form = document.getElementById('dept-form');
    form.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('dept-id').value;
        const name = document.getElementById('dept-name').value;
        
        try {
            if (id) {
                // Update
                await deptApi.request(`/departments/${id}`, 'PUT', { department_name: name });
                document.getElementById('msg').innerText = "Cập nhật thành công!";
            } else {
                // Create
                await deptApi.request('/departments/', 'POST', { department_name: name });
                document.getElementById('msg').innerText = "Thêm mới thành công!";
            }
            resetForm();
            loadDepartments();
        } catch (err) {
            alert("Lỗi: " + err.message);
        }
    };
});

// Hàm tải danh sách
async function loadDepartments() {
    try {
        const list = await deptApi.request('/departments/', 'GET');
        const tbody = document.getElementById('dept-list');
        tbody.innerHTML = '';

        list.forEach(dept => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${dept.department_id}</td>
                <td>${dept.department_name}</td>
                <td>
                    <span class="action-btn" onclick="editDept(${dept.department_id}, '${dept.department_name}')">Sửa</span> | 
                    <span class="action-btn delete-btn" onclick="deleteDept(${dept.department_id})">Xóa</span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

// Hàm chuẩn bị form để sửa
window.editDept = (id, name) => {
    document.getElementById('dept-id').value = id;
    document.getElementById('dept-name').value = name;
    document.getElementById('btn-save').innerText = "Cập nhật";
    document.getElementById('btn-cancel').style.display = "inline-block";
};

// Hàm xóa
window.deleteDept = async (id) => {
    if (confirm("Bạn có chắc chắn muốn xóa khoa này?")) {
        try {
            await deptApi.request(`/departments/${id}`, 'DELETE');
            loadDepartments();
        } catch (err) {
            alert("Không thể xóa: " + err.message);
        }
    }
};

// Hàm reset form
window.resetForm = () => {
    document.getElementById('dept-id').value = '';
    document.getElementById('dept-name').value = '';
    document.getElementById('btn-save').innerText = "Thêm mới";
    document.getElementById('btn-cancel').style.display = "none";
    document.getElementById('msg').innerText = "";
};