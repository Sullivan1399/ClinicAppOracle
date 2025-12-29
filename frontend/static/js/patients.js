// Kiểm tra quyền NURSE (Y tá)
const user = api.checkAuth('NURSE');

if (user) {
    document.getElementById('userDisplay').textContent = `Y tá: ${user.full_name}`;
    
    // Khởi chạy dữ liệu
    loadPatients();
    loadMetaData(); // Load trước Khoa & Bác sĩ để dùng cho Modal đăng ký khám
}

// Global Variables
let allPatients = [];
let allDepartments = [];
let allDoctors = [];

// --- 1. QUẢN LÝ BỆNH NHÂN ---

async function loadPatients() {
    try {
        // Sử dụng api.request thay vì fetch thủ công
        const data = await api.request('/patient/');
        
        if (data) {
            allPatients = data;
            displayPatients(allPatients);
        }
    } catch (error) {
        document.getElementById('tableBody').innerHTML = '<tr><td colspan="8" style="text-align: center; color: red;">Lỗi tải dữ liệu</td></tr>';
    }
}

function displayPatients(patients) {
    const tbody = document.getElementById('tableBody');
    if (!patients || patients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Chưa có bệnh nhân nào</td></tr>';
        return;
    }

    tbody.innerHTML = patients.map(p => `
        <tr>
            <td>${p.patient_id}</td>
            <td><strong>${p.full_name}</strong></td>
            <td>${p.dob ? new Date(p.dob).toLocaleDateString('vi-VN') : ''}</td>
            <td>${p.gender === 'M' ? 'Nam' : 'Nữ'}</td>
            <td>${p.phone || ''}</td>
            <td>${p.insurance_number || ''}</td>
            <td>${p.address || ''}</td>
            <td>
                <button class="btn-success" onclick='openVisitModal(${JSON.stringify(p)})'>Đăng Ký Khám</button>
                <button class="btn-edit" style="background: #f39c12; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;" onclick='editPatient(${JSON.stringify(p)})'>Sửa</button>
            </td>
        </tr>
    `).join('');
}

// Tìm kiếm Client-side
document.getElementById('searchInput').addEventListener('input', (e) => {
    const key = e.target.value.toLowerCase();
    const filtered = allPatients.filter(p => 
        p.full_name.toLowerCase().includes(key) || 
        (p.phone && p.phone.includes(key)) ||
        (p.insurance_number && p.insurance_number.toLowerCase().includes(key))
    );
    displayPatients(filtered);
});

// --- Modal Logic ---

function openPatientModal() {
    document.getElementById('patientModalTitle').textContent = 'Thêm Bệnh Nhân Mới';
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
    document.getElementById('patientModal').classList.add('show');
}

function editPatient(p) {
    document.getElementById('patientModalTitle').textContent = 'Chỉnh Sửa Thông Tin';
    document.getElementById('patientId').value = p.patient_id;
    document.getElementById('fullName').value = p.full_name;
    document.getElementById('dateOfBirth').value = p.dob;
    document.getElementById('gender').value = p.gender;
    document.getElementById('phoneNumber').value = p.phone;
    document.getElementById('insuranceNumber').value = p.insurance_number;
    document.getElementById('address').value = p.address;
    document.getElementById('patientModal').classList.add('show');
}

function closePatientModal() {
    document.getElementById('patientModal').classList.remove('show');
}

// Submit Form Bệnh Nhân
document.getElementById('patientForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('patientId').value;
    
    const payload = {
        full_name: document.getElementById('fullName').value,
        dob: document.getElementById('dateOfBirth').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phoneNumber').value,
        insurance_number: document.getElementById('insuranceNumber').value,
        address: document.getElementById('address').value
    };

    try {
        const url = id ? `/patient/${id}` : `/patient/`;
        const method = id ? 'PUT' : 'POST';
        
        await api.request(url, method, payload);
        
        alert('Lưu thành công!');
        closePatientModal();
        loadPatients();
    } catch (err) {
        alert(err.message);
    }
});

// --- 2. ĐĂNG KÝ KHÁM (VISIT) ---

async function loadMetaData() {
    try {
        // Load Departments
        const depts = await api.request('/department/');
        if (depts) allDepartments = depts;

        // Load Staffs (để lọc Bác sĩ)
        const staffs = await api.request('/staff/');
        if (staffs) {
            allDoctors = staffs.filter(s => s.role === 'DOCTOR');
        }
    } catch (e) { console.error("Lỗi load metadata", e); }
}

window.openVisitModal = function(p) {
    document.getElementById('visitPatientId').value = p.patient_id;
    document.getElementById('visitPatientInfo').textContent = `${p.full_name}`;
    
    // Reset form
    document.getElementById('visitForm').reset();
    
    // XỬ LÝ ẨN BÁC SĨ & TẮT VALIDATION
    const docSelect = document.getElementById('doctorSelect');
    const docSelectDiv = docSelect.closest('.form-group');
    
    if(docSelectDiv) {
        docSelectDiv.style.display = 'none'; // Ẩn giao diện
    }
    
    // QUAN TRỌNG: Bỏ thuộc tính required để trình duyệt không bắt lỗi nữa
    docSelect.required = false; 
    docSelect.disabled = true;  // Disable luôn cho chắc chắn

    // Render Departments
    const deptSelect = document.getElementById('departmentSelect');
    deptSelect.innerHTML = '<option value="">-- Chọn khoa --</option>' + 
        allDepartments.map(d => `<option value="${d.department_id}">${d.department_name}</option>`).join('');

    document.getElementById('visitModal').classList.add('show');
}

window.closeVisitModal = function() {
    document.getElementById('visitModal').classList.remove('show');
}

// Xử lý khi chọn Khoa -> Lọc Bác sĩ
document.getElementById('departmentSelect').addEventListener('change', (e) => {
    const deptId = parseInt(e.target.value);
    const docSelect = document.getElementById('doctorSelect');
    
    if (!deptId) {
        docSelect.innerHTML = '<option value="">-- Vui lòng chọn khoa trước --</option>';
        docSelect.disabled = true;
        return;
    }

    // Filter Doctors by Dept ID
    const docs = allDoctors.filter(d => d.department_id === deptId);
    
    if (docs.length === 0) {
        docSelect.innerHTML = '<option value="">-- Khoa này chưa có bác sĩ --</option>';
        docSelect.disabled = true;
    } else {
        docSelect.innerHTML = '<option value="">-- Chọn bác sĩ --</option>' + 
            docs.map(d => `<option value="${d.staff_id}">${d.full_name}</option>`).join('');
        docSelect.disabled = false;
    }
});

// Submit Đăng Ký Khám
document.getElementById('visitForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Lấy giá trị từ form
    const patientId = document.getElementById('visitPatientId').value;
    const deptId = document.getElementById('departmentSelect').value;
    const notes = document.getElementById('visitNotes').value;

    // Kiểm tra dữ liệu đầu vào cơ bản
    if (!patientId || !deptId) {
        alert("Vui lòng chọn Khoa khám bệnh!");
        return;
    }

    const payload = {
        patient_id: parseInt(patientId),
        department_id: parseInt(deptId),
        staff_id: null, // <--- QUAN TRỌNG: Sửa 0 thành null
        notes: notes
    };

    console.log("Sending payload:", payload); // Log để kiểm tra

    try {
        // Lưu ý: Đảm bảo đường dẫn API chính xác (có thể là /visit hoặc /visit/)
        await api.request('/visit/', 'POST', payload);
        
        alert('Đăng ký vào hàng chờ thành công!');
        closeVisitModal();
    } catch (error) {
        console.error("API Error:", error);
        alert('Lỗi đăng ký: ' + error.message);
    }
});