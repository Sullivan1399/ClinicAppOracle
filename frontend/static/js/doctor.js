// Kiểm tra quyền DOCTOR
const user = api.checkAuth('DOCTOR');

if (user) {
    document.getElementById('doctorName').textContent = `Bác sĩ: ${user.full_name}`;
    loadWaitingList();
}

// Global Vars
let allMedicines = []; // Cache danh sách thuốc để search nhanh
let currentPrescription = []; // Danh sách thuốc đang kê tạm thời

// --- 1. Danh sách chờ khám ---

async function loadWaitingList() {
    try {
        // Gọi API endpoint mới chuyên cho danh sách chờ
        // Backend tự lấy department_id từ Token của bác sĩ
        const visits = await api.request(`/visit/waiting`); 
        
        const container = document.getElementById('waitingList');
        if (!visits || visits.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">Không có bệnh nhân chờ.</p>';
            return;
        }

        container.innerHTML = visits.map(v => `
            <div class="patient-card">
                <div>
                    <div style="font-weight: bold; font-size: 1.1em; color: #2c3e50;">${v.patient_name}</div>
                    <div style="color: #7f8c8d; font-size: 0.9em; margin-top: 5px;">
                        🕒 Đăng ký lúc: ${new Date(v.visit_date).toLocaleTimeString('vi-VN')} <br>
                        📝 Lý do: ${v.notes || '---'}
                    </div>
                </div>
                <button class="btn-primary" onclick='startExam(${JSON.stringify(v)})'>Tiếp nhận</button>
            </div>
        `).join('');

    } catch (e) {
        console.error(e);
        document.getElementById('waitingList').innerHTML = '<p style="color: red; text-align:center;">Lỗi tải danh sách</p>';
    }
}

// --- 2. Bắt đầu khám ---
async function startExam(visit) {
    // Ẩn danh sách, hiện form khám
    document.getElementById('waitingSection').style.display = 'none';
    document.getElementById('examSection').style.display = 'block';
    
    // Fill thông tin cơ bản từ visit (nếu có sẵn tên bệnh nhân)
    document.getElementById('currentPatientName').textContent = `Đang khám: ${visit.patient_name || 'Bệnh nhân #' + visit.patient_id}`;
    document.getElementById('visitId').value = visit.visit_id;
    document.getElementById('diagnosis').value = '';
    document.getElementById('notes').value = '';
    
    // Load chi tiết bệnh nhân
    try {
        console.log("Fetching patient info for ID:", visit.patient_id); // Log để debug
        const patient = await api.request(`/patient/${visit.patient_id}`);
        
        console.log("Patient Data:", patient); // Log dữ liệu nhận được

        if (patient) {
            // Tính tuổi
            let age = '?';
            if (patient.dob) {
                const birthYear = new Date(patient.dob).getFullYear();
                const currentYear = new Date().getFullYear();
                age = currentYear - birthYear;
            }

            document.getElementById('patientInfo').innerHTML = `
                <div style="line-height: 1.6;">
                    <p><strong>Họ tên:</strong> ${patient.full_name}</p>
                    <p><strong>Ngày sinh:</strong> ${patient.dob ? new Date(patient.dob).toLocaleDateString('vi-VN') : 'N/A'} (Tuổi: ${age})</p>
                    <p><strong>Giới tính:</strong> ${patient.gender === 'M' ? 'Nam' : 'Nữ'}</p>
                    <p><strong>SĐT:</strong> ${patient.phone || '---'}</p>
                    <p><strong>BHYT:</strong> ${patient.insurance_number || 'Không'}</p>
                    <p><strong>Địa chỉ:</strong> ${patient.address || '---'}</p>
                </div>
            `;
        } else {
            throw new Error("Dữ liệu bệnh nhân rỗng");
        }

    } catch(e) { 
        console.error("Lỗi load patient:", e);
        document.getElementById('patientInfo').innerHTML = `<span style="color:red">Không thể tải thông tin chi tiết (ID: ${visit.patient_id})</span>`; 
    }

    // Load danh sách thuốc (chỉ load 1 lần)
    if (allMedicines.length === 0) {
        try {
            console.log("Đang tải danh sách thuốc...");
            const data = await api.request('/medicine/');
            console.log("Danh sách thuốc từ API:", data); // <--- Quan trọng: Xem cấu trúc thuốc ở đây

            if (Array.isArray(data)) {
                allMedicines = data;
            } else {
                console.error("API thuốc trả về không phải mảng:", data);
            }
        } catch(e) { console.error("Lỗi load thuốc", e); }
    }
    
    // Reset đơn thuốc
    currentPrescription = [];
    renderPrescription();
}
// Hàm quay lại danh sách chờ (ẩn giao diện khám)
function cancelExam() {
    // Ẩn phần khám bệnh
    document.getElementById('examSection').style.display = 'none';
    
    // Hiện lại danh sách chờ
    document.getElementById('waitingSection').style.display = 'block';
    
    // Reset các ô nhập liệu để lần sau khám không bị lưu dữ liệu cũ
    document.getElementById('visitId').value = '';
    document.getElementById('diagnosis').value = '';
    document.getElementById('notes').value = '';
    document.getElementById('patientInfo').innerHTML = 'Loading...';
    
    // Reset đơn thuốc
    currentPrescription = [];
    renderPrescription();
    document.getElementById('medSearch').value = '';
    
    // Tải lại danh sách chờ để cập nhật
    loadWaitingList();
}
// --- 3. Kê đơn thuốc ---

// Autocomplete
const searchInput = document.getElementById('medSearch');
const suggestions = document.getElementById('medSuggestions');

searchInput.addEventListener('input', () => {
    const val = searchInput.value.toLowerCase();
    suggestions.innerHTML = '';
    
    if (val.length < 1) {
        suggestions.style.display = 'none';
        return;
    }

    const matches = allMedicines.filter(m => m.medicine_name.toLowerCase().includes(val));
    
    if (matches.length > 0) {
        suggestions.style.display = 'block';
        matches.forEach(m => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `<b>${m.medicine_name}</b> <small>(${m.unit})</small>`;
            div.onclick = () => selectMedicine(m);
            suggestions.appendChild(div);
        });
    } else {
        suggestions.style.display = 'none';
    }
});

function selectMedicine(m) {
    document.getElementById('selectedMedName').value = m.medicine_name;
    document.getElementById('selectedMedId').value = m.medicine_id;
    document.getElementById('medSearch').value = '';
    suggestions.style.display = 'none';
    document.getElementById('medQty').focus();
}

function addDrug() {
    const id = document.getElementById('selectedMedId').value;
    const name = document.getElementById('selectedMedName').value;
    const qty = document.getElementById('medQty').value;
    const usage = document.getElementById('medUsage').value;

    if (!id || !qty) {
        alert("Vui lòng chọn thuốc và nhập số lượng");
        return;
    }

    currentPrescription.push({
        medicine_id: parseInt(id),
        medicine_name: name,
        quantity: parseInt(qty),
        dosage: usage
    });

    // Reset input
    document.getElementById('selectedMedName').value = '';
    document.getElementById('selectedMedId').value = '';
    document.getElementById('medQty').value = '';
    document.getElementById('medUsage').value = '';
    
    renderPrescription();
}

function removeDrug(index) {
    currentPrescription.splice(index, 1);
    renderPrescription();
}

function renderPrescription() {
    const tbody = document.getElementById('presTable');
    if (currentPrescription.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999; padding: 20px;">Chưa có thuốc nào</td></tr>';
        return;
    }

    tbody.innerHTML = currentPrescription.map((drug, i) => `
        <tr>
            <td>${drug.medicine_name}</td>
            <td style="text-align: center;">${drug.quantity}</td>
            <td>${drug.dosage}</td>
            <td style="text-align: center;"><button class="btn-remove" onclick="removeDrug(${i})">Xóa</button></td>
        </tr>
    `).join('');
}

// --- 4. Lưu Khám ---

async function finishExam() {
    const visitId = document.getElementById('visitId').value;
    const diagnosis = document.getElementById('diagnosis').value;
    const notes = document.getElementById('notes').value;

    if (!diagnosis) {
        alert("Vui lòng nhập chẩn đoán bệnh!");
        return;
    }

    try {
        // Gọi API Claim & Update
        await api.request(`/visit/${visitId}/claim`, 'PUT', {
            diagnosis: diagnosis,
            notes: notes
        });

        // Tạo đơn thuốc (giữ nguyên logic cũ)
        if (currentPrescription.length > 0) {
            // ... (code tạo đơn thuốc cũ)
        }

        alert("Đã lưu bệnh án thành công!");
        cancelExam(); // Quay lại danh sách

    } catch (e) {
        alert("Lỗi: " + e.message); // Nếu đã có bác sĩ khác khám, nó sẽ báo lỗi ở đây
        loadWaitingList(); // Tải lại danh sách để cập nhật tình trạng mới nhất
    }
}