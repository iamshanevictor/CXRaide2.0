<template>
  <div class="modal-overlay" v-if="show" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Input Patient Information</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="bi bi-x"></i>
        </button>
      </div>

      <div class="modal-body">
        <div class="form-grid">
          <!-- Row 1 -->
          <div class="form-group">
            <label for="patientName">Patient Name:</label>
            <input type="text" id="patientName" v-model="patientInfo.name" placeholder="Enter patient name" />
          </div>
          <div class="form-group">
            <label for="patientId">Patient ID No.:</label>
            <input type="text" id="patientId" v-model="patientInfo.id" readonly />
          </div>

          <!-- Row 2 -->
          <div class="form-group">
            <label for="gender">Gender:</label>
            <select id="gender" v-model="patientInfo.gender">
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label for="age">Age:</label>
            <input type="number" id="age" v-model="patientInfo.age" placeholder="Enter age" />
          </div>

          <!-- Row 3 -->
          <div class="form-group">
            <label for="examTaken">Exam Taken:</label>
            <input type="text" id="examTaken" v-model="patientInfo.examTaken" />
          </div>
          <div class="form-group">
            <label for="address">Address:</label>
            <input type="text" id="address" v-model="patientInfo.address" placeholder="Enter address" />
          </div>

          <!-- Row 4 -->
          <div class="form-group">
            <label for="resultDate">Result Date:</label>
            <input type="date" id="resultDate" v-model="patientInfo.resultDate" />
          </div>
          <div class="form-group">
            <label for="resultTime">Result Time:</label>
            <input type="time" id="resultTime" v-model="patientInfo.resultTime" />
          </div>
        </div>

        <!-- Clinical Indication -->
        <div class="form-section">
          <h3>CLINICAL INDICATION</h3>
          <select v-model="patientInfo.clinicalIndication">
            <option value="Patient presents with symptoms concerning for pulmonary or cardiovascular pathology">Patient presents with symptoms concerning for pulmonary or cardiovascular pathology</option>
            <option value="Annual check-up">Annual check-up</option>
            <option value="Follow-up for previous abnormality">Follow-up for previous abnormality</option>
            <option value="Pre-operative evaluation">Pre-operative evaluation</option>
            <option value="Post-operative evaluation">Post-operative evaluation</option>
          </select>
        </div>

        <!-- Findings -->
        <div class="form-section">
          <h3>FINDINGS</h3>
          
          <div class="finding-group">
            <label>Lungs:</label>
            <select v-model="patientInfo.findings.lungs">
              <option value="No significant abnormalities">No significant abnormalities</option>
              <option value="Pulmonary Edema: Findings consistent with pulmonary edema.">Pulmonary Edema: Findings consistent with pulmonary edema.</option>
              <option value="Infiltrates noted in lung fields">Infiltrates noted in lung fields</option>
            </select>
          </div>
          
          <div class="finding-group">
            <label>Heart:</label>
            <select v-model="patientInfo.findings.heart">
              <option value="Normal cardiac silhouette">Normal cardiac silhouette</option>
              <option value="Cardiomegaly: The cardiac silhouette is enlarged, suggesting cardiomegaly.">Cardiomegaly: The cardiac silhouette is enlarged, suggesting cardiomegaly.</option>
            </select>
          </div>
          
          <div class="finding-group">
            <label>Mediastinum:</label>
            <select v-model="patientInfo.findings.mediastinum">
              <option value="No significant abnormalities">No significant abnormalities</option>
              <option value="Mediastinal Widening: Widening of the mediastinum noted.">Mediastinal Widening: Widening of the mediastinum noted.</option>
            </select>
          </div>
          
          <div class="finding-group">
            <label>Diaphragm and Pleura:</label>
            <select v-model="patientInfo.findings.diaphragmPleura">
              <option value="No significant abnormalities">No significant abnormalities</option>
              <option value="Pleural Effusion (right): Fluid accumulation in the right pleural space.">Pleural Effusion (right): Fluid accumulation in the right pleural space.</option>
              <option value="Pleural Effusion (left): Fluid accumulation in the left pleural space.">Pleural Effusion (left): Fluid accumulation in the left pleural space.</option>
            </select>
          </div>
          
          <div class="finding-group">
            <label>Soft Tissues and Bones:</label>
            <select v-model="patientInfo.findings.softTissuesBones">
              <option value="No fractures or significant soft tissue changes">No fractures or significant soft tissue changes</option>
              <option value="Fracture noted">Fracture noted</option>
            </select>
          </div>
          
          <div class="finding-group">
            <label>Add more findings here:</label>
            <textarea v-model="patientInfo.findings.additional" placeholder="None."></textarea>
          </div>
        </div>

        <!-- Abnormalities -->
        <div class="form-section">
          <h3>THE ABNORMALITY FOUND IS/ARE:</h3>
          
          <div class="finding-group">
            <label>Main Abnormality:</label>
            <input type="text" v-model="patientInfo.abnormalities.main" placeholder="Enter main abnormality" />
          </div>
          
          <div class="finding-group">
            <label>Sub Abnormality:</label>
            <input type="text" v-model="patientInfo.abnormalities.sub" placeholder="Enter sub abnormality" />
          </div>
        </div>

        <!-- Impression and Recommendations -->
        <div class="form-section">
          <h3>IMPRESSION</h3>
          <select v-model="patientInfo.impression">
            <option value="Findings warrant further evaluation with follow-up imaging.">Findings warrant further evaluation with follow-up imaging.</option>
            <option value="No significant abnormalities.">No significant abnormalities.</option>
            <option value="Findings consistent with previous examination.">Findings consistent with previous examination.</option>
          </select>
          
          <h3>RECOMMENDATIONS</h3>
          <select v-model="patientInfo.recommendations">
            <option value="Clinical correlation and additional diagnostic testing recommended.">Clinical correlation and additional diagnostic testing recommended.</option>
            <option value="Follow-up imaging in 3 months.">Follow-up imaging in 3 months.</option>
            <option value="No further imaging required at this time.">No further imaging required at this time.</option>
          </select>
        </div>

        <!-- Report Preparation -->
        <div class="form-section">
          <h3>REPORT PREPARED BY</h3>
          
          <div class="finding-group">
            <label>Radiologist:</label>
            <input type="text" v-model="patientInfo.radiologist" placeholder="Enter radiologist name" />
          </div>
          
          <div class="finding-group">
            <label>Radiographer:</label>
            <input type="text" v-model="patientInfo.radiographer" placeholder="Enter radiographer name" />
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="submit-btn" @click="submitAndProceed">Submit and Proceed</button>
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PatientInfoModal",
  props: {
    show: {
      type: Boolean,
      default: false
    },
    reportType: {
      type: String,
      default: "Expert"
    }
  },
  data() {
    return {
      patientInfo: {
        name: "",
        id: this.generatePatientId(),
        gender: "Male",
        age: "",
        examTaken: "CHEST",
        address: "",
        resultDate: new Date().toISOString().split('T')[0],
        resultTime: new Date().toTimeString().slice(0, 5),
        clinicalIndication: "Patient presents with symptoms concerning for pulmonary or cardiovascular pathology",
        findings: {
          lungs: "No significant abnormalities",
          heart: "Normal cardiac silhouette",
          mediastinum: "No significant abnormalities",
          diaphragmPleura: "No significant abnormalities",
          softTissuesBones: "No fractures or significant soft tissue changes",
          additional: ""
        },
        abnormalities: {
          main: "",
          sub: ""
        },
        impression: "Findings warrant further evaluation with follow-up imaging.",
        recommendations: "Clinical correlation and additional diagnostic testing recommended.",
        radiologist: "",
        radiographer: ""
      }
    };
  },
  methods: {
    generatePatientId() {
      const prefix = "PID_";
      const randomNum1 = Math.floor(Math.random() * 1000);
      const randomNum2 = Math.floor(Math.random() * 1000);
      return `${prefix}${randomNum1}_${randomNum2}`;
    },
    submitAndProceed() {
      this.$emit('submit', { 
        patientInfo: this.patientInfo,
        reportType: this.reportType
      });
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.modal-container {
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.modal-header h2 {
  color: #f3f4f6;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: #f3f4f6;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.9rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

input, select, textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 0.75rem;
  color: #f3f4f6;
  font-size: 1rem;
  width: 100%;
  transition: border-color 0.2s;
}

/* Fix for dropdown options visibility */
select {
  appearance: menulist;
  background-color: rgba(15, 23, 42, 0.95);
}

select option {
  background-color: rgba(15, 23, 42, 0.95);
  color: #f3f4f6;
  padding: 10px;
}

/* Show the dropdown arrow clearly */
select {
  appearance: none;
  background-color: rgba(15, 23, 42, 0.95);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>');
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 35px; /* Space for the arrow */
  cursor: pointer;
}

/* Style for the dropdown on hover/focus */
select:hover, select:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.5);
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

textarea {
  min-height: 80px;
  resize: vertical;
}

.form-section {
  margin-bottom: 1.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 4px;
  padding: 1rem;
  background-color: rgba(15, 23, 42, 0.4);
}

.form-section h3 {
  color: #f3f4f6;
  font-size: 1.2rem;
  margin: 0 0 1rem 0;
  text-align: center;
  font-weight: 500;
  background-color: rgba(15, 23, 42, 0.6);
  padding: 0.5rem;
  border-radius: 4px;
}

/* Specific styling for selects in form sections */
.form-section select {
  background-color: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(59, 130, 246, 0.3);
  margin-bottom: 0.75rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section select:hover {
  border-color: #3b82f6;
  background-color: rgba(15, 23, 42, 0.8);
}

.finding-group {
  margin-bottom: 1rem;
}

.finding-group label {
  display: block;
  font-size: 0.9rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.submit-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.submit-btn:hover {
  background-color: #43A047;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
  border: none;
}

.cancel-btn:hover {
  background-color: #e53935;
}
</style> 