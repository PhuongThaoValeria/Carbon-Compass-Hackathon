🌍 Carbon Compass

Brief Introduction
Carbon Compass is an AI-powered platform designed to help SMEs exporting to the European Union accurately estimate shipment carbon emissions, calculate CBAM (Carbon Border Adjustment Mechanism) fees, and identify practical strategies to reduce those costs.
By combining regulatory intelligence with logistics data, the app empowers exporters to make data-driven, sustainable, and cost-efficient trade decisions aligned with EU green compliance standards.

🔗Live Demo URL: https://cacbonsolutionsite.vercel.app/

✨ Key Features
- Carbon Emission Estimation: Calculates both embedded and transport-related emissions for each shipment.
- CBAM Fee Calculation: Determines potential carbon border adjustment payments based on EU regulations.
- Benchmark Comparison: Compares shipment emissions with EU industry benchmarks to identify high-risk products.
- Emission Reduction Suggestions: Provides AI-driven recommendations to minimize carbon intensity and reduce CBAM costs.
- Automated Reporting: Generates export-ready reports for compliance, audits, and sustainability disclosures.
- SME-Focused Design: Simplified, intuitive interface tailored to small and medium-sized exporters.

🧰 Tech Stack / Core Tools
- AI Engine: TRAE + Dify LLM for reasoning and emission calculation.
- Frontend Framework: React + Next.js (optimized for speed and interactivity).
- Backend Framework: Python (FastAPI) for emission logic and data processing.
- Database & Storage: Google Cloud Storage for dataset management and benchmarks.
- Deployment Platform: Vercel (frontend) + Google Cloud Run (backend).
- External Integrations: Connected to verified carbon emission databases and transport emission factor APIs.

Formula for this AI: 
- CBAM Fee = Quantity of goods (tons) × Embedded emissions (tCO₂/ton) × EUA price (€/tCO₂)
- Current futures contract for Dec 2025: approx from EUR 78.38/tCO₂ to 90/tCO₂ according to ICE data. ( sources: https://www.ice.com/products/197/EUA-Futures/data?utm_source=chatgpt.com&marketId=5474739)
- <img width="503" height="313" alt="image" src="https://github.com/user-attachments/assets/cb3e6d3d-5d0f-40dc-8371-233d924d2ba8" />
