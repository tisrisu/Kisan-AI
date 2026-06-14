/**
 * KisanAI — API Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...options.headers,
      },
    };

    // Don't set Content-Type for FormData (browser does it automatically with boundary)
    if (!(options.body instanceof FormData)) {
      config.headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `API Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error.name === "TypeError" && error.message === "Failed to fetch") {
        // API not reachable — return demo data
        console.warn("API not reachable, using demo mode");
        return null;
      }
      throw error;
    }
  }

  // ─── Diagnosis ───
  async diagnose(formData) {
    return this.request("/diagnose", {
      method: "POST",
      body: formData,
    });
  }

  // ─── Feedback ───
  async submitFeedback(data) {
    return this.request("/feedback", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ─── History ───
  async getHistory(farmerId, page = 1, perPage = 20) {
    return this.request(`/history/${farmerId}?page=${page}&per_page=${perPage}`);
  }

  // ─── Reference Data ───
  async getDistricts() {
    return this.request("/districts");
  }

  async getCrops(category = null) {
    const params = category ? `?category=${category}` : "";
    return this.request(`/crops${params}`);
  }

  async getDiseaseDetail(diseaseId) {
    return this.request(`/diseases/${diseaseId}`);
  }

  // ─── Health ───
  async healthCheck() {
    return this.request("/health");
  }
}

const api = new ApiClient();
export default api;

// Demo data for when API is not available
export const DEMO_DISTRICTS = [
  { id: 1, name: "Guntur", state: "Andhra Pradesh", code: "AP-GNT", major_crops: ["Chili", "Cotton", "Rice"] },
  { id: 2, name: "Krishna", state: "Andhra Pradesh", code: "AP-KRI", major_crops: ["Rice", "Cotton"] },
  { id: 6, name: "Thanjavur", state: "Tamil Nadu", code: "TN-TNJ", major_crops: ["Rice", "Sugarcane"] },
  { id: 7, name: "Coimbatore", state: "Tamil Nadu", code: "TN-CBE", major_crops: ["Cotton", "Coconut"] },
  { id: 10, name: "Karimnagar", state: "Telangana", code: "TS-KMN", major_crops: ["Rice", "Cotton"] },
  { id: 13, name: "Ludhiana", state: "Punjab", code: "PB-LDH", major_crops: ["Wheat", "Rice"] },
  { id: 16, name: "Lucknow", state: "Uttar Pradesh", code: "UP-LKO", major_crops: ["Wheat", "Rice"] },
  { id: 19, name: "Nashik", state: "Maharashtra", code: "MH-NSK", major_crops: ["Grapes", "Onion"] },
];

export const DEMO_CROPS = [
  { id: 1, name: "IR-64", category: "Rice" },
  { id: 2, name: "Pusa Basmati", category: "Rice" },
  { id: 3, name: "Samba Mahsuri", category: "Rice" },
  { id: 6, name: "BT Cotton", category: "Cotton" },
  { id: 9, name: "Teja", category: "Chili" },
  { id: 12, name: "HD-2967", category: "Wheat" },
  { id: 15, name: "Pusa Ruby", category: "Tomato" },
  { id: 17, name: "Kufri Jyoti", category: "Potato" },
  { id: 19, name: "DHM-117", category: "Corn" },
];

export const DEMO_RESULT = {
  submission_id: 1,
  diagnosis_id: 1,
  disease_name: "Rice Blast",
  scientific_name: "Magnaporthe oryzae",
  confidence: 94.2,
  severity: {
    level: "Moderate",
    level_id: 1,
    confidence: 78.5,
    distribution: { Mild: 12.3, Moderate: 78.5, Severe: 9.2 },
  },
  predictions: [
    { rank: 1, disease_id: 0, disease_name: "Rice Blast", scientific_name: "Magnaporthe oryzae", confidence: 94.2 },
    { rank: 2, disease_id: 2, disease_name: "Brown Spot", scientific_name: "Cochliobolus miyabeanus", confidence: 3.8 },
    { rank: 3, disease_id: 3, disease_name: "Sheath Blight", scientific_name: "Rhizoctonia solani", confidence: 1.2 },
  ],
  medications: [
    { id: 1, name: "Tricyclazole 75% WP", dosage: "0.6g per liter of water" },
    { id: 2, name: "Isoprothiolane 40% EC", dosage: "1.5ml per liter of water" },
    { id: 3, name: "Carbendazim 50% WP", dosage: "1g per liter of water" },
  ],
  precautions: [
    "Wear mask and gloves while spraying",
    "Do NOT spray near water bodies",
    "Spray during evening hours (low wind)",
    "Wait 14 days before harvest",
    "Drain excess field water",
    "Remove severely infected plants",
    "Contact nearest KVK if >30% crop affected",
  ],
  prevention_tips: [
    "Use resistant varieties (Tetep, Zenith)",
    "Balanced fertilization — avoid excess nitrogen",
    "Proper plant spacing for air circulation",
    "Crop rotation with non-host crops",
    "Use certified disease-free seeds",
  ],
  model_type: "demo",
  translations: { hi: "चावल का ब्लास्ट", te: "వరి బ్లాస్ట్", ta: "நெல் பிளாஸ்ட்" },
  created_at: new Date().toISOString(),
};
