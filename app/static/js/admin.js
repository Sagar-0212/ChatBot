/**
 * Controls navigation tabs inside the Admin Command Center.
 */
function switchTab(event, tabId) {
    // Hide all panels
    const panels = document.querySelectorAll('.db-panel');
    panels.forEach(panel => {
        panel.classList.remove('active');
    });

    // Deactivate all tab links
    const tabLinks = document.querySelectorAll('.db-tab-link');
    tabLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Show selected panel & set tab as active
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

/**
 * Triggers scikit-learn model training asynchronously on backend.
 */
function retrainModel() {
    const statusText = document.getElementById('retrain-status');
    const retrainBtn = document.getElementById('btn-retrain-model');
    const syncIcon = retrainBtn.querySelector('i');
    
    statusText.textContent = "Retraining in progress...";
    statusText.style.color = "var(--accent-blue)";
    retrainBtn.disabled = true;
    syncIcon.classList.add('spinning');

    fetch('/admin/api/train', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        syncIcon.classList.remove('spinning');
        retrainBtn.disabled = false;
        
        if (data.error) {
            statusText.textContent = "Error during retraining.";
            statusText.style.color = "var(--status-error)";
            alert(`Retraining failed: ${data.error}`);
        } else {
            statusText.textContent = "Reloaded successfully!";
            statusText.style.color = "var(--status-online)";
            alert(data.message);
            setTimeout(() => {
                statusText.textContent = "";
            }, 5000);
        }
    })
    .catch(error => {
        syncIcon.classList.remove('spinning');
        retrainBtn.disabled = false;
        statusText.textContent = "Connection error.";
        statusText.style.color = "var(--status-error)";
        console.error("Retrain error:", error);
    });
}

// ==========================================
// FAQ MODAL & AJAX OPERATIONS
// ==========================================
const faqModal = document.getElementById('faq-modal');
const faqForm = document.getElementById('faq-form');
const faqTitle = document.getElementById('modal-title');
const faqIdInput = document.getElementById('faq-id');
const faqQuestionInput = document.getElementById('faq-question');
const faqAnswerInput = document.getElementById('faq-answer');
const faqIntentInput = document.getElementById('faq-intent');
const faqKeywordsInput = document.getElementById('faq-keywords');

function openFaqModal() {
    faqTitle.textContent = "Add New FAQ";
    faqForm.reset();
    faqIdInput.value = "";
    faqModal.classList.add('active');
}

function closeFaqModal() {
    faqModal.classList.remove('active');
}

function editFaq(id, question, answer, intentCategory, keywordTags) {
    faqTitle.textContent = "Edit FAQ Record";
    faqIdInput.value = id;
    faqQuestionInput.value = question;
    faqAnswerInput.value = answer;
    faqIntentInput.value = intentCategory;
    faqKeywordsInput.value = keywordTags;
    faqModal.classList.add('active');
}

function saveFaq(event) {
    event.preventDefault();
    const id = faqIdInput.value;
    const isEdit = id !== "";
    const endpoint = isEdit ? `/admin/api/faq/${id}/update` : '/admin/api/faq';
    
    fetch(endpoint, {
        method: 'POST',
        body: new FormData(faqForm)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            closeFaqModal();
            window.location.reload();
        }
    })
    .catch(err => alert("An error occurred. Check logs."));
}

function deleteFaq(faqId) {
    if (!confirm("Delete this FAQ record?")) return;
    fetch(`/admin/api/faq/${faqId}/delete`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            const row = document.getElementById(`faq-row-${faqId}`);
            if (row) row.remove();
            else window.location.reload();
        }
    });
}

// ==========================================
// ADMISSIONS MODAL & AJAX OPERATIONS
// ==========================================
const admissionModal = document.getElementById('admission-modal');
const admissionForm = document.getElementById('admission-form');
const admissionTitle = document.getElementById('admission-modal-title');
const admissionIdInput = document.getElementById('admission-id');
const admissionProgramInput = document.getElementById('admission-program');
const admissionEligibilityInput = document.getElementById('admission-eligibility');
const admissionFeesInput = document.getElementById('admission-fees');
const admissionSeatsInput = document.getElementById('admission-seats');
const admissionLastDateInput = document.getElementById('admission-lastdate');
const admissionDocsInput = document.getElementById('admission-docs');

function openAdmissionModal() {
    admissionTitle.textContent = "Add New Program";
    admissionForm.reset();
    admissionIdInput.value = "";
    admissionModal.classList.add('active');
}

function closeAdmissionModal() {
    admissionModal.classList.remove('active');
}

function editAdmission(id, program, eligibility, totalFees, intakeSeats, lastDate, documentsRequired) {
    admissionTitle.textContent = "Edit Admission Program";
    admissionIdInput.value = id;
    admissionProgramInput.value = program;
    admissionEligibilityInput.value = eligibility;
    admissionFeesInput.value = totalFees;
    admissionSeatsInput.value = intakeSeats;
    admissionLastDateInput.value = lastDate;
    admissionDocsInput.value = documentsRequired;
    admissionModal.classList.add('active');
}

function saveAdmission(event) {
    event.preventDefault();
    const id = admissionIdInput.value;
    const isEdit = id !== "";
    const endpoint = isEdit ? `/admin/api/admission/${id}/update` : '/admin/api/admission';
    
    fetch(endpoint, {
        method: 'POST',
        body: new FormData(admissionForm)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            closeAdmissionModal();
            window.location.reload();
        }
    })
    .catch(err => alert("An error occurred. Check logs."));
}

function deleteAdmission(progId) {
    if (!confirm("Are you sure you want to delete this program?")) return;
    fetch(`/admin/api/admission/${progId}/delete`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            const row = document.getElementById(`admission-row-${progId}`);
            if (row) row.remove();
            else window.location.reload();
        }
    });
}

// ==========================================
// EXAMS MODAL & AJAX OPERATIONS
// ==========================================
// ==========================================
// EXAMS MODAL & AJAX OPERATIONS
// ==========================================
const examModal = document.getElementById('exam-modal');
const examForm = document.getElementById('exam-form');
const examTitle = document.getElementById('exam-modal-title');
const examIdInput = document.getElementById('exam-id');
const examSubjectCodeInput = document.getElementById('exam-subject-code');
const examSubjectInput = document.getElementById('exam-subject');
const examDeptInput = document.getElementById('exam-department');
const examYearInput = document.getElementById('exam-year');
const examSemesterInput = document.getElementById('exam-semester');
const examTypeInput = document.getElementById('exam-type');
const examDateInput = document.getElementById('exam-date');
const examTimeInput = document.getElementById('exam-time');
const examVenueInput = document.getElementById('exam-venue');
const examDurationInput = document.getElementById('exam-duration');

function openExamModal() {
    examTitle.textContent = "Schedule Exam";
    examForm.reset();
    examIdInput.value = "";
    examModal.classList.add('active');
}

function closeExamModal() {
    examModal.classList.remove('active');
}

function editExam(id, subjectCode, subject, department, yearOfStudy, semester, examDate, examTime, venue, durationMinutes, examType) {
    examTitle.textContent = "Edit Exam Schedule";
    examIdInput.value = id;
    examSubjectCodeInput.value = subjectCode;
    examSubjectInput.value = subject;
    examDeptInput.value = department;
    examYearInput.value = yearOfStudy;
    examSemesterInput.value = semester;
    examTypeInput.value = examType;
    examDateInput.value = examDate;
    examTimeInput.value = examTime;
    examVenueInput.value = venue;
    examDurationInput.value = durationMinutes;
    examModal.classList.add('active');
}

function saveExam(event) {
    event.preventDefault();
    const id = examIdInput.value;
    const isEdit = id !== "";
    const endpoint = isEdit ? `/admin/api/exam/${id}/update` : '/admin/api/exam';
    
    fetch(endpoint, {
        method: 'POST',
        body: new FormData(examForm)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            closeExamModal();
            window.location.reload();
        }
    })
    .catch(err => alert("An error occurred."));
}

function deleteExam(examId) {
    if (!confirm("Are you sure you want to delete this exam schedule?")) return;
    fetch(`/admin/api/exam/${examId}/delete`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            const row = document.getElementById(`exam-row-${examId}`);
            if (row) row.remove();
            else window.location.reload();
        }
    });
}

// ==========================================
// TIMETABLE MODAL & AJAX OPERATIONS
// ==========================================
const timetableModal = document.getElementById('timetable-modal');
const timetableForm = document.getElementById('timetable-form');
const timetableTitle = document.getElementById('timetable-modal-title');
const timetableIdInput = document.getElementById('timetable-id');
const timetableSubjectInput = document.getElementById('timetable-subject');
const timetableDeptInput = document.getElementById('timetable-department');
const timetableYearInput = document.getElementById('timetable-year');
const timetableSemesterInput = document.getElementById('timetable-semester');
const timetableDayInput = document.getElementById('timetable-day');
const timetableStartInput = document.getElementById('timetable-start');
const timetableEndInput = document.getElementById('timetable-end');
const timetableRoomInput = document.getElementById('timetable-room');
const timetableFacultyInput = document.getElementById('timetable-faculty');

function openTimetableModal() {
    timetableTitle.textContent = "Add Class Slot";
    timetableForm.reset();
    timetableIdInput.value = "";
    timetableModal.classList.add('active');
}

function closeTimetableModal() {
    timetableModal.classList.remove('active');
}

function editTimetable(id, department, yearOfStudy, semester, dayOfWeek, subject, startTime, endTime, roomNo, facultyName) {
    timetableTitle.textContent = "Edit Timetable Slot";
    timetableIdInput.value = id;
    timetableSubjectInput.value = subject;
    timetableDeptInput.value = department;
    timetableYearInput.value = yearOfStudy;
    timetableSemesterInput.value = semester;
    timetableDayInput.value = dayOfWeek;
    timetableStartInput.value = startTime;
    timetableEndInput.value = endTime;
    timetableRoomInput.value = roomNo;
    timetableFacultyInput.value = facultyName;
    timetableModal.classList.add('active');
}

function saveTimetable(event) {
    event.preventDefault();
    const id = timetableIdInput.value;
    const isEdit = id !== "";
    const endpoint = isEdit ? `/admin/api/timetable/${id}/update` : '/admin/api/timetable';
    
    fetch(endpoint, {
        method: 'POST',
        body: new FormData(timetableForm)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            closeTimetableModal();
            window.location.reload();
        }
    })
    .catch(err => alert("An error occurred."));
}

function deleteTimetable(slotId) {
    if (!confirm("Are you sure you want to delete this timetable slot?")) return;
    fetch(`/admin/api/timetable/${slotId}/delete`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) alert(`Failed: ${data.error}`);
        else {
            alert(data.message);
            const row = document.getElementById(`timetable-row-${slotId}`);
            if (row) row.remove();
            else window.location.reload();
        }
    });
}

// ==========================================
// INTERACTIVE PREVIEWS & PRINT INTEGRATION
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    if (typeof allExamsData !== "undefined") {
        renderExamsPreview();
    }
    if (typeof allTimetableData !== "undefined") {
        renderTimetablePreview();
    }
});

function renderExamsPreview() {
    const dept = document.getElementById("preview-exam-dept").value;
    const year = parseInt(document.getElementById("preview-exam-year").value);
    const sem = parseInt(document.getElementById("preview-exam-sem").value);
    const container = document.getElementById("exam-preview-container");

    const filtered = allExamsData.filter(ex => 
        ex.department === dept && ex.year_of_study === year && ex.semester === sem
    );

    if (filtered.length === 0) {
        container.innerHTML = `<div class="empty-preview-state">No examinations scheduled for ${dept} Year ${year} Sem ${sem}.</div>`;
        return;
    }

    let html = `
        <table class="exam-schedule-table">
            <thead>
                <tr>
                    <th>Subject Code</th>
                    <th>Subject Name</th>
                    <th>Exam Date</th>
                    <th>Time Slot</th>
                    <th>Venue</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
    `;

    filtered.forEach(ex => {
        html += `
            <tr>
                <td><code>${ex.subject_code}</code></td>
                <td><strong>${ex.subject}</strong></td>
                <td>${ex.exam_date}</td>
                <td>${ex.exam_time}</td>
                <td>${ex.venue}</td>
                <td>${ex.duration_minutes} mins</td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function renderTimetablePreview() {
    const dept = document.getElementById("preview-tt-dept").value;
    const year = parseInt(document.getElementById("preview-tt-year").value);
    const sem = parseInt(document.getElementById("preview-tt-sem").value);
    const container = document.getElementById("timetable-preview-container");

    const filtered = allTimetableData.filter(slot => 
        slot.department === dept && slot.year_of_study === year && slot.semester === sem
    );

    if (filtered.length === 0) {
        container.innerHTML = `<div class="empty-preview-state">No class slots scheduled for ${dept} Year ${year} Sem ${sem}.</div>`;
        return;
    }

    // Extract unique sorted time slots
    const slotsSet = new Set();
    filtered.forEach(s => slotsSet.add(`${s.start_time} - ${s.end_time}`));
    const timeSlots = Array.from(slotsSet).sort((a, b) => {
        const tA = a.split(" - ")[0];
        const tB = b.split(" - ")[0];
        return tA.localeCompare(tB);
    });

    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

    let html = `
        <table class="timetable-grid-table">
            <thead>
                <tr>
                    <th>Time Slot</th>
                    ${days.map(d => `<th>${d}</th>`).join("")}
                </tr>
            </thead>
            <tbody>
    `;

    timeSlots.forEach(timeSlot => {
        html += `<tr>`;
        html += `<td class="time-slot-cell"><strong>${timeSlot}</strong></td>`;
        
        days.forEach(day => {
            const daySlots = filtered.filter(s => 
                s.day_of_week.toLowerCase() === day.toLowerCase() && 
                `${s.start_time} - ${s.end_time}` === timeSlot
            );

            if (daySlots.length > 0) {
                html += `<td class="grid-slot-cell active-slot">`;
                daySlots.forEach(s => {
                    html += `
                        <div class="slot-content">
                            <span class="slot-subject">${s.subject}</span>
                            <div class="slot-details-inline">
                                <span class="slot-room"><i class="bx bx-map"></i> Room: ${s.room_no}</span>
                                <span class="slot-faculty" title="Faculty Name"><i class="bx bx-user"></i> ${s.faculty_name}</span>
                            </div>
                        </div>
                    `;
                });
                html += `</td>`;
            } else {
                html += `<td class="grid-slot-cell empty-slot">-</td>`;
            }
        });
        html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function printFilteredExams() {
    const dept = document.getElementById("preview-exam-dept").value;
    const year = document.getElementById("preview-exam-year").value;
    const sem = document.getElementById("preview-exam-sem").value;
    window.open(`/schedules?dept=${dept}&year=${year}&sem=${sem}`, '_blank');
}

function printFilteredTimetable() {
    const dept = document.getElementById("preview-tt-dept").value;
    const year = document.getElementById("preview-tt-year").value;
    const sem = document.getElementById("preview-tt-sem").value;
    window.open(`/schedules?dept=${dept}&year=${year}&sem=${sem}`, '_blank');
}
