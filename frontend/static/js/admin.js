// --- AUTH & INIT ---
const user = api.checkAuth('ADMIN');
if(user) document.getElementById('userDisplay').innerText = `Admin: ${user.full_name}`;

// Global Data Storage
let allDepts = [];
let allStaffs = [];
let allMeds = [];

// --- NAVIGATION LOGIC ---
function switchTab(tabName, element) {
    // 1. Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    // 2. Remove active class from sidebar
    document.querySelectorAll('.sidebar a').forEach(el => el.classList.remove('active'));
    
    // 3. Show selected tab & active sidebar
    document.getElementById(`tab-${tabName}`).classList.add('active');
    if(element) element.classList.add('active');

    // 4. Load data for that tab
    if (tabName === 'dept') loadDepartments();
    else if (tabName === 'staff') loadStaffs();
    else if (tabName === 'medicine') loadMedicines();
}

// Helper: Close any modal by ID
window.closeModal = (modalId) => document.getElementById(modalId).classList.remove('show');

// ============================================================
// 1. DEPARTMENT LOGIC
// ============================================================
async function loadDepartments() {
    try {
        const data = await api.request('/department/');
        allDepts = data; // Lưu lại để dùng cho dropdown bên Staff
        renderDeptTable(data);
    } catch (e) { console.error(e); }
}

function renderDeptTable(data) {
    const tbody = document.getElementById('deptBody');
    tbody.innerHTML = data.map(d => `
        <tr>
            <td>${d.department_id}</td>
            <td><strong>${d.department_name}</strong></td>
            <td>
                <button class="btn-edit" onclick='editDept(${JSON.stringify(d)})'>Sửa</button>
                <button class="btn-danger" onclick="deleteDept(${d.department_id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

window.openDeptModal = () => {
    document.getElementById('deptForm').reset();
    document.getElementById('deptId').value = '';
    document.getElementById('deptModal').classList.add('show');
}

window.editDept = (dept) => {
    document.getElementById('deptId').value = dept.department_id;
    document.getElementById('deptName').value = dept.department_name;
    document.getElementById('deptModal').classList.add('show');
}

document.getElementById('deptForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('deptId').value;
    const name = document.getElementById('deptName').value;

    try {
        if(id) await api.request(`/department/${id}`, 'PUT', { department_name: name });
        else await api.request('/department/', 'POST', { department_name: name });
        
        alert('Lưu khoa thành công!');
        closeModal('deptModal');
        loadDepartments();
    } catch (err) { alert(err.message); }
});

window.deleteDept = async (id) => {
    if(confirm('Xóa khoa này? (Lưu ý: Chỉ xóa được nếu khoa không có nhân viên/bệnh nhân)')) {
        try {
            await api.request(`/department/${id}`, 'DELETE');
            loadDepartments();
        } catch(e) { alert(e.message); }
    }
}

// ============================================================
// 2. STAFF LOGIC
// ============================================================
async function loadStaffs() {
    try {
        // Cần load department trước để hiển thị tên khoa trong bảng và dropdown
        if(allDepts.length === 0) await loadDepartments();
        
        const data = await api.request('/staff/');
        allStaffs = data;
        renderStaffTable(data);
    } catch (e) { console.error(e); }
}

function renderStaffTable(data) {
    const tbody = document.getElementById('staffBody');
    if(!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">Chưa có dữ liệu</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(s => {
        // Tìm tên khoa từ ID
        const dept = allDepts.find(d => d.department_id === s.department_id);
        const deptName = dept ? dept.department_name : '---';
        
        return `
        <tr>
            <td>${s.staff_id}</td>
            <td>${s.full_name}</td>
            <td>${s.username}</td>
            <td><span style="font-weight:bold; color:${s.role==='ADMIN'?'red':'blue'}">${s.role}</span></td>
            <td>${deptName}</td>
            <td>${s.phone || ''}</td>
            <td>
                <button class="btn-edit" onclick='editStaff(${JSON.stringify(s)})'>Sửa</button>
                <button class="btn-danger" onclick="deleteStaff(${s.staff_id})">Xóa</button>
            </td>
        </tr>
    `}).join('');
}

// Search Staff
document.getElementById('searchStaff').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allStaffs.filter(s => 
        s.full_name.toLowerCase().includes(term) || 
        s.username.toLowerCase().includes(term)
    );
    renderStaffTable(filtered);
});

// Helper: Fill Department Dropdown
function fillDeptDropdown(selectedId = null) {
    const select = document.getElementById('staffDept');
    select.innerHTML = '<option value="">-- Chọn Khoa --</option>' + 
        allDepts.map(d => `<option value="${d.department_id}" ${d.department_id === selectedId ? 'selected' : ''}>${d.department_name}</option>`).join('');
}

window.openStaffModal = () => {
    document.getElementById('staffForm').reset();
    document.getElementById('staffId').value = '';
    fillDeptDropdown();
    document.getElementById('staffModal').classList.add('show');
}

window.editStaff = (s) => {
    document.getElementById('staffId').value = s.staff_id;
    document.getElementById('staffName').value = s.full_name;
    document.getElementById('staffUsername').value = s.username;
    document.getElementById('staffRole').value = s.role;
    document.getElementById('staffPhone').value = s.phone || '';
    document.getElementById('staffPass').value = ''; // Không hiện pass cũ
    
    fillDeptDropdown(s.department_id);
    document.getElementById('staffModal').classList.add('show');
}

document.getElementById('staffForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('staffId').value;
    
    const payload = {
        full_name: document.getElementById('staffName').value,
        username: document.getElementById('staffUsername').value,
        role: document.getElementById('staffRole').value,
        department_id: parseInt(document.getElementById('staffDept').value) || null,
        phone: document.getElementById('staffPhone').value,
        email: null
    };

    // Xử lý password: Nếu tạo mới bắt buộc, nếu sửa thì tùy chọn
    const pass = document.getElementById('staffPass').value;
    if (pass) {
        payload.password = pass;
    } else if (!id) {
        alert("Vui lòng nhập mật khẩu cho nhân viên mới!");
        return;
    }

    try {
        if(id) await api.request(`/staff/${id}`, 'PUT', payload);
        else await api.request('/staff/', 'POST', payload);
        
        alert('Lưu nhân viên thành công!');
        closeModal('staffModal');
        loadStaffs();
    } catch (err) { alert(err.message); }
});

window.deleteStaff = async (id) => {
    if(confirm('Xóa nhân viên này?')) {
        try {
            await api.request(`/staff/${id}`, 'DELETE');
            loadStaffs();
        } catch(e) { alert(e.message); }
    }
}

// ============================================================
// 3. MEDICINE LOGIC (Giữ nguyên logic cũ của bạn)
// ============================================================
async function loadMedicines() {
    try {
        const data = await api.request('/medicine/');
        allMeds = data;
        renderMedTable(data);
    } catch (e) { console.error(e); }
}

function renderMedTable(data) {
    const tbody = document.getElementById('medBody');
    tbody.innerHTML = data.map(m => `
        <tr>
            <td>${m.medicine_id}</td>
            <td>${m.medicine_name}</td>
            <td>${m.unit}</td>
            <td>${Number(m.price).toLocaleString()}</td>
            <td>
                <button class="btn-edit" onclick='editMed(${JSON.stringify(m)})'>Sửa</button>
                <button class="btn-danger" onclick="deleteMed(${m.medicine_id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

document.getElementById('searchMed').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allMeds.filter(m => m.medicine_name.toLowerCase().includes(term));
    renderMedTable(filtered);
});

window.openMedModal = () => {
    document.getElementById('medForm').reset();
    document.getElementById('medId').value = '';
    document.getElementById('medModal').classList.add('show');
}

window.editMed = (item) => {
    document.getElementById('medId').value = item.medicine_id;
    document.getElementById('medName').value = item.medicine_name;
    document.getElementById('medUnit').value = item.unit;
    document.getElementById('medPrice').value = item.price;
    document.getElementById('medModal').classList.add('show');
}

document.getElementById('medForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('medId').value;
    const body = {
        medicine_name: document.getElementById('medName').value,
        unit: document.getElementById('medUnit').value,
        price: Number(document.getElementById('medPrice').value)
    };

    try {
        if(id) await api.request(`/medicine/${id}`, 'PUT', body);
        else await api.request('/medicine/', 'POST', body);
        
        alert('Lưu thuốc thành công!');
        closeModal('medModal');
        loadMedicines();
    } catch (err) { alert(err.message); }
});

window.deleteMed = async (id) => {
    if(confirm('Xóa thuốc này?')) {
        try {
            await api.request(`/medicine/${id}`, 'DELETE');
            loadMedicines();
        } catch(e) { alert(e.message); }
    }
}

// Khởi chạy mặc định: Load tab Department trước
loadDepartments();