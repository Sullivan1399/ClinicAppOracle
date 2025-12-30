// nurse.js

// 1. KHỞI TẠO & KIỂM TRA QUYỀN
const user = api.checkAuth('NURSE');
if (user) {
    document.getElementById('userDisplay').textContent = `Y tá: ${user.full_name}`;
    loadPatients();
    loadMetaData(); 
}

let allPatients = [];
let allDepartments = [];
let allDoctors = [];

// 2. QUẢN LÝ TAB
function switchTab(tabName, element) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.sidebar a').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
    if(element) element.classList.add('active');

    if (tabName === 'patients') loadPatients();
    if (tabName === 'waiting') loadWaitingVisits();
    if (tabName === 'pharmacy') loadPrescriptions();
    if (tabName === 'staff') loadStaffList(); // GỌI HÀM MỚI
}

// HÀM MỚI: Lấy danh sách nhân sự
async function loadStaffList() {
    try {
        const tbody = document.getElementById('staffTableBody');
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Đang tải...</td></tr>';
        
        const data = await api.request('/staff'); // Gọi đến endpoint lấy nhân sự
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Không có dữ liệu nhân sự.</td></tr>';
            return;
        }

        // Map vai trò sang tiếng Việt cho dễ đọc
        const roles = { 'DOCTOR': 'Bác sĩ', 'NURSE': 'Y tá', 'ADMIN': 'Quản trị' };

        tbody.innerHTML = data.map(s => `
            <tr>
                <td>${s.staff_id}</td>
                <td><strong>${s.full_name}</strong></td>
                <td><span class="badge" style="background: #3498db; color: white; padding: 2px 8px; border-radius: 4px;">
                    ${roles[s.role] || s.role}
                </span></td>
                <td>${s.department_name || '---'}</td>
                <td>${s.phone || '---'}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error("Lỗi tải staff:", error);
        document.getElementById('staffTableBody').innerHTML = 
            '<tr><td colspan="5" style="text-align: center; color: red;">Bạn không có quyền xem thông tin này hoặc lỗi kết nối.</td></tr>';
    }
}

// 3. QUẢN LÝ BỆNH NHÂN
async function loadPatients() {
    try {
        const data = await api.request('/patient'); 
        allPatients = data || [];
        displayPatients(allPatients);
    } catch (error) {
        console.error(error);
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

// Tìm kiếm bệnh nhân
document.getElementById('searchInput').addEventListener('input', (e) => {
    const key = e.target.value.toLowerCase();
    const filtered = allPatients.filter(p => 
        p.full_name.toLowerCase().includes(key) || 
        (p.phone && p.phone.includes(key)) ||
        (p.insurance_number && p.insurance_number.toLowerCase().includes(key))
    );
    displayPatients(filtered);
});

// SUBMIT FORM BỆNH NHÂN (CHỈ GIỮ 1 CÁI NÀY)
document.getElementById('patientForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('patientId').value;
    
    const payload = {
        full_name: document.getElementById('fullName').value.trim(),
        dob: document.getElementById('dateOfBirth').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phoneNumber').value.trim() || null,
        insurance_number: document.getElementById('insuranceNumber').value.trim() || null,
        address: document.getElementById('address').value.trim() || null
    };

    try {
        const url = id ? `/patient/${id}` : `/patient`;
        const method = id ? 'PUT' : 'POST';
        
        await api.request(url, method, payload);
        alert('Lưu thông tin bệnh nhân thành công!');
        closePatientModal();
        loadPatients();
    } catch (err) {
        alert("Lỗi: " + err.message);
    }
});

// 4. ĐĂNG KÝ KHÁM (VISIT)
async function loadMetaData() {
    try {
        const depts = await api.request('/department');
        if (depts) allDepartments = depts;
        const staffs = await api.request('/staff');
        if (staffs) allDoctors = staffs.filter(s => s.role === 'DOCTOR');
    } catch (e) { console.error("Lỗi load metadata", e); }
}

async function loadWaitingVisits() {
    try {
        const tbody = document.getElementById('waitingBody');
        tbody.innerHTML = '<tr><td colspan="5">Đang tải...</td></tr>';
        const visits = await api.request('/visit'); 
        const waiting = visits.filter(v => !v.staff_id);
        tbody.innerHTML = waiting.map(v => `
            <tr>
                <td>${new Date(v.visit_date).toLocaleString('vi-VN')}</td>
                <td><strong>${v.patient_name}</strong></td>
                <td>${v.department_name}</td>
                <td>${v.notes || '---'}</td>
                <td><span class="status-waiting">⏳ Chờ bác sĩ</span></td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5">Không thể tải danh sách chờ</td></tr>';
    }
}

document.getElementById('visitForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const patientId = document.getElementById('visitPatientId').value;
    const deptId = document.getElementById('departmentSelect').value;
    const notes = document.getElementById('visitNotes').value;

    if (!patientId || !deptId) {
        alert("Vui lòng chọn Khoa khám bệnh!");
        return;
    }

    const payload = {
        patient_id: parseInt(patientId),
        department_id: parseInt(deptId),
        notes: notes.trim() || null
    };

    try {
        await api.request('/visit', 'POST', payload);
        alert('Đăng ký vào hàng chờ thành công!');
        closeVisitModal();
        switchTab('waiting'); 
    } catch (error) {
        alert('Lỗi: ' + error.message);
    }
});

// 5. CẤP PHÁT THUỐC
async function loadPrescriptions() {
    try {
        const container = document.getElementById('prescriptionList');
        container.innerHTML = 'Đang tải đơn thuốc...';
        const data = await api.request('/prescription');
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:20px;">Hiện không có đơn thuốc nào.</p>';
            return;
        }

        container.innerHTML = data.map(p => `
            <div class="pres-card">
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #eee; padding-bottom:10px;">
                    <span><strong>Đơn thuốc #${p.prescription_id}</strong></span>
                    <span style="color: #666;">Ngày kê: ${new Date(p.created_date).toLocaleString('vi-VN')}</span>
                </div>
                <div style="padding: 10px 0;">
                    <p><strong>Bệnh nhân:</strong> ${p.visit_id}</p> 
                    <ul style="list-style: none; padding-left: 0; margin-top: 10px;">
                        ${p.details.map(d => `
                            <li style="padding: 5px; background: #f8f9fa; border-radius: 4px; margin-bottom:5px;">
                                🔹 ${d.medicine_name} - SL: <b>${d.quantity}</b> 
                                <br><small>👉 ${d.dosage}</small>
                            </li>
                        `).join('')}
                    </ul>
                </div>
               <!-- <div style="margin-top:10px; text-align:right;">
                    <button class="btn-success" onclick="confirmDispense(${p.prescription_id})">✅ Hoàn tất cấp thuốc</button>
                </div>-->
            </div>
        `).join('');
    } catch (e) {
        document.getElementById('prescriptionList').innerHTML = 'Lỗi tải đơn thuốc.';
    }
}

function confirmDispense(id) {
    if(confirm(`Xác nhận đã soạn và cấp đủ thuốc cho đơn #${id}?`)) {
        alert("Đã xác nhận cấp thuốc thành công!");
        loadPrescriptions();
    }
}

// 6. LOGIC HIỂN THỊ MODAL
function openPatientModal() {
    const title = document.getElementById('patientModalTitle');
    if (title) title.textContent = 'Thêm Bệnh Nhân Mới';
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
    document.getElementById('patientModal').style.display = 'block';
}

function editPatient(p) {
    const title = document.getElementById('patientModalTitle');
    if (title) title.textContent = 'Chỉnh Sửa Thông Tin';
    document.getElementById('patientId').value = p.patient_id;
    document.getElementById('fullName').value = p.full_name;
    document.getElementById('dateOfBirth').value = p.dob;
    document.getElementById('gender').value = p.gender;
    document.getElementById('phoneNumber').value = p.phone || '';
    document.getElementById('insuranceNumber').value = p.insurance_number || '';
    document.getElementById('address').value = p.address || '';
    document.getElementById('patientModal').style.display = 'block';
}

function closePatientModal() {
    document.getElementById('patientModal').style.display = 'none';
}

window.openVisitModal = function(p) {
    document.getElementById('visitPatientId').value = p.patient_id;
    document.getElementById('visitPatientInfo').textContent = `Bệnh nhân: ${p.full_name}`;
    document.getElementById('visitForm').reset();
    const deptSelect = document.getElementById('departmentSelect');
    if (deptSelect) {
        deptSelect.innerHTML = '<option value="">-- Chọn khoa --</option>' + 
            allDepartments.map(d => `<option value="${d.department_id}">${d.department_name}</option>`).join('');
    }
    document.getElementById('visitModal').style.display = 'block';
}

function closeVisitModal() {
    document.getElementById('visitModal').style.display = 'none';
}