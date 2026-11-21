"""
generate_profiles.py - Generator Profil Kandidat Sintetis Otomatis
Membangkitkan 96 profil query (24 profil dasar x 4 kondisi bahasa C0, C1, C2, C3)
berdasarkan perakitan komponen struktural modular (S1, S2, S3, S4).
"""
import json
import re
from pathlib import Path

OUT_FILE = Path("data/candidate_profiles.json")

# ----------------------------------------------------------------------------
# DATABASE 24 PROFIL DASAR (8 BIDANG IT x 3 LEVEL PENGALAMAN)
# ----------------------------------------------------------------------------
BASE_PROFILES = [
    # ---------------- 1. BACKEND ----------------
    {
        "base_id": "P01", "role_group": "backend", "level": "Junior", "exp_years": 1,
        "S1_id": "Pengembang Backend Junior", "S1_en": "Junior Backend Developer",
        "S2_id": "memiliki pengalaman 1 tahun dalam membangun dan mengelola layanan web API.", "S2_en": "with 1 year of experience building and maintaining web API services.",
        "S3_id": "Terbiasa merancang basis data relasional, membuat dokumentasi sistem, dan melakukan integrasi RESTful API.", "S3_en": "Experienced in relational database design, writing system documentation, and RESTful API integration.",
        "S4_id": "Menguasai bahasa PHP, kerangka kerja Laravel, basis data MySQL, dan kontrol versi Git.", "S4_en": "Proficient in PHP, Laravel framework, MySQL database, and Git version control."
    },
    {
        "base_id": "P02", "role_group": "backend", "level": "Mid", "exp_years": 3,
        "S1_id": "Pengembang Backend Tingkat Menengah", "S1_en": "Mid-level Backend Engineer",
        "S2_id": "memiliki pengalaman 3 tahun dalam merancang arsitektur microservices dan basis data berskala menengah.", "S2_en": "with 3 years of experience designing microservices architecture and medium-scale databases.",
        "S3_id": "Berpengalaman mengoptimalkan kueri basis data, manajemen repositori, dan otomasi alur kerja backend.", "S3_en": "Experienced in database query optimization, repository management, and automated backend workflows.",
        "S4_id": "Menguasai Node.js, Express, basis data PostgreSQL, kontainerisasi Docker, dan caching Redis.", "S4_en": "Proficient in Node.js, Express, PostgreSQL database, Docker containerization, and Redis caching."
    },
    {
        "base_id": "P03", "role_group": "backend", "level": "Senior", "exp_years": 5,
        "S1_id": "Pengembang Backend Senior", "S1_en": "Senior Backend Engineer",
        "S2_id": "memiliki pengalaman 5 tahun memimpin pengembangan sistem terdistribusi skala enterprise.", "S2_en": "with 5 years of experience leading enterprise-scale distributed system development.",
        "S3_id": "Fokus pada arsitektur dengan ketersediaan tinggi, pemrosesan data real-time, dan otomasi alur kerja deployment.", "S3_en": "Focused on high-availability architecture, real-time data streaming, and automated deployment pipelines.",
        "S4_id": "Menguasai Java Spring Boot, Apache Kafka, arsitektur Kubernetes, dan infrastruktur AWS.", "S4_en": "Proficient in Java Spring Boot, Apache Kafka, Kubernetes architecture, and AWS cloud infrastructure."
    },

    # ---------------- 2. FRONTEND ----------------
    {
        "base_id": "P04", "role_group": "frontend", "level": "Junior", "exp_years": 1,
        "S1_id": "Pengembang Frontend Junior", "S1_en": "Junior Frontend Developer",
        "S2_id": "memiliki pengalaman 1 tahun dalam membangun antarmuka web yang responsif.", "S2_en": "with 1 year of experience building responsive web interfaces.",
        "S3_id": "Terbiasa menerjemahkan desain UI menjadi komponen web interaktif serta melakukan integrasi API.", "S3_en": "Skilled in translating UI designs into interactive web components and performing API integration.",
        "S4_id": "Menguasai HTML5, CSS3, JavaScript ES6, React.js, dan Tailwind CSS.", "S4_en": "Proficient in HTML5, CSS3, JavaScript ES6, React.js, and Tailwind CSS."
    },
    {
        "base_id": "P05", "role_group": "frontend", "level": "Mid", "exp_years": 3,
        "S1_id": "Pengembang Frontend Tingkat Menengah", "S1_en": "Mid-level Frontend Engineer",
        "S2_id": "memiliki pengalaman 3 tahun dalam mengoptimalkan performa aplikasi web modern.", "S2_en": "with 3 years of experience optimizing modern web application performance.",
        "S3_id": "Berpengalaman mengelola state aplikasi kompleks, arsitektur render server-side, dan pengujian unit antarmuka.", "S3_en": "Experienced in complex state management, server-side rendering architecture, and UI unit testing.",
        "S4_id": "Menguasai TypeScript, Next.js, Redux Toolkit, Vue.js, dan framework pengujian Jest.", "S4_en": "Proficient in TypeScript, Next.js, Redux Toolkit, Vue.js, and Jest testing framework."
    },
    {
        "base_id": "P06", "role_group": "frontend", "level": "Senior", "exp_years": 5,
        "S1_id": "Pengembang Frontend Senior", "S1_en": "Senior Frontend Engineer",
        "S2_id": "memiliki pengalaman 5 tahun merancang arsitektur sistem frontend berskala masif.", "S2_en": "with 5 years of experience architecting large-scale frontend systems.",
        "S3_id": "Fokus pada arsitektur micro-frontend, aksesibilitas web standar internasional, dan optimasi kecepatan muat halaman.", "S3_en": "Focused on micro-frontend architecture, international web accessibility standards, and page speed optimization.",
        "S4_id": "Menguasai React, GraphQL, Progressive Web Apps (PWA), TypeScript, dan metrik Core Web Vitals.", "S4_en": "Proficient in React, GraphQL, Progressive Web Apps (PWA), TypeScript, and Core Web Vitals metrics."
    },

    # ---------------- 3. DATA ANALYST ----------------
    {
        "base_id": "P07", "role_group": "data_analyst", "level": "Junior", "exp_years": 1,
        "S1_id": "Analis Data Junior", "S1_en": "Junior Data Analyst",
        "S2_id": "memiliki pengalaman 1 tahun dalam pengolahan data dan penyusunan laporan operasional.", "S2_en": "with 1 year of experience in data processing and operational reporting.",
        "S3_id": "Terbiasa melakukan pembersihan data, ekstraksi kueri basis data, dan pembuatan dasbor visualisasi interaktif.", "S3_en": "Skilled in data cleaning, database query extraction, and building interactive visualization dashboards.",
        "S4_id": "Menguasai SQL, Microsoft Excel tingkat lanjut, Tableau, dan pemograman Python dasar.", "S4_en": "Proficient in SQL, advanced Microsoft Excel, Tableau, and basic Python programming."
    },
    {
        "base_id": "P08", "role_group": "data_analyst", "level": "Mid", "exp_years": 3,
        "S1_id": "Analis Data Tingkat Menengah", "S1_en": "Mid-level Data Analyst",
        "S2_id": "memiliki pengalaman 3 tahun dalam analisis statistik bisnis dan validasi metrik produk.", "S2_en": "with 3 years of experience in business statistical analysis and product metrics validation.",
        "S3_id": "Berpengalaman mengolah data mentah menjadi wawasan bisnis, merancang eksperimen A/B testing, dan analisis tren pasar.", "S3_en": "Experienced in transforming raw data into business insights, designing A/B test experiments, and market trend analysis.",
        "S4_id": "Menguasai Python, Power BI, PostgreSQL, Google Looker Studio, dan metode analisis statistik.", "S4_en": "Proficient in Python, Power BI, PostgreSQL, Google Looker Studio, and statistical analysis methods."
    },
    {
        "base_id": "P09", "role_group": "data_analyst", "level": "Senior", "exp_years": 5,
        "S1_id": "Analis Data Senior", "S1_en": "Senior Data Analyst",
        "S2_id": "memiliki pengalaman 5 tahun memimpin inisiatif intelijen bisnis dan strategi data enterprise.", "S2_en": "with 5 years of experience leading business intelligence initiatives and enterprise data strategy.",
        "S3_id": "Berpengalaman merancang arsitektur gudang data, pemodelan data bisnis, dan menyajikan rekomendasi strategis bagi pimpinan.", "S3_en": "Experienced in data warehouse architecture, business data modeling, and presenting strategic recommendations to executives.",
        "S4_id": "Menguasai Google BigQuery, dbt (data build tool), Python, arsitektur Data Warehouse, dan Product Analytics.", "S4_en": "Proficient in Google BigQuery, dbt (data build tool), Python, Data Warehouse architecture, and Product Analytics."
    },

    # ---------------- 4. DATA SCIENTIST ----------------
    {
        "base_id": "P10", "role_group": "data_scientist", "level": "Junior", "exp_years": 1,
        "S1_id": "Ilmuwan Data Junior", "S1_en": "Junior Data Scientist",
        "S2_id": "memiliki pengalaman 1 tahun dalam membangun model pembelajaran mesin prediktif.", "S2_en": "with 1 year of experience building predictive machine learning models.",
        "S3_id": "Terbiasa melakukan pra-pemrosesan data, rekayasa fitur, serta evaluasi performa algoritma klasifikasi.", "S3_en": "Skilled in data preprocessing, feature engineering, and classification algorithm evaluation.",
        "S4_id": "Menguasai bahasa Python, Scikit-Learn, Pandas, NumPy, dan analisis regresi.", "S4_en": "Proficient in Python, Scikit-Learn, Pandas, NumPy, and regression analysis."
    },
    {
        "base_id": "P11", "role_group": "data_scientist", "level": "Mid", "exp_years": 3,
        "S1_id": "Ilmuwan Data Tingkat Menengah", "S1_en": "Mid-level Data Scientist",
        "S2_id": "memiliki pengalaman 3 tahun dalam mengembangkan solusi pemrosesan bahasa alami dan visi komputer.", "S2_en": "with 3 years of experience developing natural language processing and computer vision solutions.",
        "S3_id": "Berpengalaman melakukan eksperimen pembelajaran mendalam, optimasi hiperparameter, dan penyebaran model via API.", "S3_en": "Experienced in deep learning experimentation, hyperparameter tuning, and model deployment via API.",
        "S4_id": "Menguasai PyTorch, TensorFlow, XGBoost, pustaka NLP, dan kontainerisasi Docker.", "S4_en": "Proficient in PyTorch, TensorFlow, XGBoost, NLP libraries, and Docker containerization."
    },
    {
        "base_id": "P12", "role_group": "data_scientist", "level": "Senior", "exp_years": 5,
        "S1_id": "Ilmuwan Data Senior", "S1_en": "Senior Data Scientist",
        "S2_id": "memiliki pengalaman 5 tahun merancang sistem kecerdasan buatan enterprise dan alur kerja MLOps.", "S2_en": "with 5 years of experience architecting enterprise AI systems and MLOps workflows.",
        "S3_id": "Fokus pada fine-tuning Large Language Models (LLM), pemodelan terdistribusi data skala besar, dan tata kelola model AI.", "S3_en": "Focused on Large Language Model (LLM) fine-tuning, large-scale distributed training, and AI governance.",
        "S4_id": "Menguasai PyTorch, HuggingFace Transformers, MLflow, Apache Spark, dan alur kerja MLOps.", "S4_en": "Proficient in PyTorch, HuggingFace Transformers, MLflow, Apache Spark, and MLOps pipelines."
    },

    # ---------------- 5. UI/UX DESIGNER ----------------
    {
        "base_id": "P13", "role_group": "uiux", "level": "Junior", "exp_years": 1,
        "S1_id": "Desainer UI/UX Junior", "S1_en": "Junior UI/UX Designer",
        "S2_id": "memiliki pengalaman 1 tahun dalam merancang antarmuka aplikasi seluler dan web.", "S2_en": "with 1 year of experience designing mobile and web application interfaces.",
        "S3_id": "Terbiasa membuat sketsa kawat (wireframe), alur pengguna, prototipe interaktif, dan pengujian ketergunaan dasar.", "S3_en": "Skilled in creating wireframes, user flows, interactive prototypes, and basic usability testing.",
        "S4_id": "Menguasai Figma, FigJam, prinsip-prinsip desain responsif, dan alat perancangan prototipe.", "S4_en": "Proficient in Figma, FigJam, responsive design principles, and prototyping tools."
    },
    {
        "base_id": "P14", "role_group": "uiux", "level": "Mid", "exp_years": 3,
        "S1_id": "Desainer UI/UX Tingkat Menengah", "S1_en": "Mid-level UI/UX Designer",
        "S2_id": "memiliki pengalaman 3 tahun dalam merancang sistem desain dan arsitektur informasi produk.", "S2_en": "with 3 years of experience in design system architecture and product information design.",
        "S3_id": "Berpengalaman melakukan riset pengguna kualitatif, peta perjalanan pengguna, dan kolaborasi erat dengan tim pengembang.", "S3_en": "Experienced in qualitative user research, user journey mapping, and close developer handoff collaboration.",
        "S4_id": "Menguasai Figma, komponen Design System, metode User Research, dan pengujian A/B testing.", "S4_en": "Proficient in Figma, Design System components, User Research methodologies, and A/B testing."
    },
    {
        "base_id": "P15", "role_group": "uiux", "level": "Senior", "exp_years": 5,
        "S1_id": "Desainer Produk UI/UX Senior", "S1_en": "Senior Product UI/UX Designer",
        "S2_id": "memiliki pengalaman 5 tahun memimpin strategi desain produk digital end-to-end.", "S2_en": "with 5 years of experience leading end-to-end digital product design strategy.",
        "S3_id": "Fokus pada penyelarasan tujuan bisnis dengan pengalaman pengguna, arsitektur UX aplikasi kompleks, dan kepemimpinan desain.", "S3_en": "Focused on aligning business vision with user experience, complex application UX architecture, and design leadership.",
        "S4_id": "Menguasai Strategi Produk Digital, Figma, Arsitektur UX, Riset Pengguna Lanjutan, dan Handoff Sistem.", "S4_en": "Proficient in Digital Product Strategy, Figma, UX Architecture, Advanced User Research, and System Handoff."
    },

    # ---------------- 6. DEVOPS ENGINEER ----------------
    {
        "base_id": "P16", "role_group": "devops", "level": "Junior", "exp_years": 1,
        "S1_id": "Insinyur DevOps Junior", "S1_en": "Junior DevOps Engineer",
        "S2_id": "memiliki pengalaman 1 tahun dalam mengelola server Linux dan otomasi alur kerja CI/CD.", "S2_en": "with 1 year of experience managing Linux servers and CI/CD workflow automation.",
        "S3_id": "Terbiasa mengonfigurasi kontainer aplikasi, pembuatan skrip automasi Shell, dan manajemen server web.", "S3_en": "Skilled in application container configuration, Shell automation scripting, and web server management.",
        "S4_id": "Menguasai sistem operasi Linux, Docker, GitLab CI/CD, Nginx, dan skrip Bash.", "S4_en": "Proficient in Linux OS, Docker, GitLab CI/CD, Nginx, and Bash scripting."
    },
    {
        "base_id": "P17", "role_group": "devops", "level": "Mid", "exp_years": 3,
        "S1_id": "Insinyur DevOps Tingkat Menengah", "S1_en": "Mid-level DevOps Engineer",
        "S2_id": "memiliki pengalaman 3 tahun dalam mengelola klaster Kubernetes dan infrastruktur komputasi awan.", "S2_en": "with 3 years of experience managing Kubernetes clusters and cloud infrastructure.",
        "S3_id": "Berpengalaman menerapkan Infrastructure as Code (IaC), pemantauan sistem otomatis, dan pemulihan bencana.", "S3_en": "Experienced in implementing Infrastructure as Code (IaC), automated system monitoring, and disaster recovery.",
        "S4_id": "Menguasai Kubernetes, Terraform, Amazon Web Services (AWS), Ansible, Prometheus, dan Grafana.", "S4_en": "Proficient in Kubernetes, Terraform, Amazon Web Services (AWS), Ansible, Prometheus, and Grafana."
    },
    {
        "base_id": "P18", "role_group": "devops", "level": "Senior", "exp_years": 5,
        "S1_id": "Insinyur Keandalan Situs Senior", "S1_en": "Senior Site Reliability Engineer (SRE)",
        "S2_id": "memiliki pengalaman 5 tahun merancang arsitektur multi-cloud dengan tingkat toleransi kesalahan tinggi.", "S2_en": "with 5 years of experience architecting fault-tolerant multi-cloud environments.",
        "S3_id": "Fokus pada operasional GitOps zero-downtime, keamanan infrastruktur cloud, dan optimasi efisiensi biaya komputasi.", "S3_en": "Focused on zero-downtime GitOps operations, cloud infrastructure security, and computing cost optimization.",
        "S4_id": "Menguasai Arsitektur Multi-Cloud, ArgoCD, Kubernetes Enterprise, Terraform, dan Keamanan Cloud.", "S4_en": "Proficient in Multi-Cloud Architecture, ArgoCD, Enterprise Kubernetes, Terraform, and Cloud Security."
    },

    # ---------------- 7. NETWORK ENGINEER ----------------
    {
        "base_id": "P19", "role_group": "network", "level": "Junior", "exp_years": 1,
        "S1_id": "Insinyur Jaringan Junior", "S1_en": "Junior Network Engineer",
        "S2_id": "memiliki pengalaman 1 tahun dalam mengonfigurasi dan memelihara infrastruktur jaringan LAN/WAN.", "S2_en": "with 1 year of experience configuring and maintaining LAN/WAN network infrastructure.",
        "S3_id": "Terbiasa melakukan pemecahan masalah konektivitas, konfigurasi perangkat keras router/switch, dan aturan firewall dasar.", "S3_en": "Skilled in connectivity troubleshooting, router/switch hardware configuration, and basic firewall rules.",
        "S4_id": "Menguasai perangkat Cisco, MikroTik, protokol TCP/IP, konfigurasi VLAN, dan analisis jaringan.", "S4_en": "Proficient in Cisco devices, MikroTik, TCP/IP protocols, VLAN configuration, and network analysis."
    },
    {
        "base_id": "P20", "role_group": "network", "level": "Mid", "exp_years": 3,
        "S1_id": "Insinyur Jaringan Tingkat Menengah", "S1_en": "Mid-level Network Engineer",
        "S2_id": "memiliki pengalaman 3 tahun mengelola routing dinamis enterprise dan keamanan perimeter jaringan.", "S2_en": "with 3 years of experience managing enterprise dynamic routing and network perimeter security.",
        "S3_id": "Berpengalaman mengonfigurasi koneksi VPN site-to-site, manajemen trafik jaringan, dan pencegahan intrusi.", "S3_en": "Experienced in configuring site-to-site VPN connections, network traffic management, and intrusion prevention.",
        "S4_id": "Menguasai sertifikasi CCNA, protokol BGP/OSPF, Fortinet Firewall, IPsec VPN, dan Wireshark.", "S4_en": "Proficient in CCNA certification, BGP/OSPF protocols, Fortinet Firewall, IPsec VPN, and Wireshark."
    },
    {
        "base_id": "P21", "role_group": "network", "level": "Senior", "exp_years": 5,
        "S1_id": "Arsitek Jaringan Senior", "S1_en": "Senior Network Architect",
        "S2_id": "memiliki pengalaman 5 tahun merancang jaringan data center enterprise dan otomasinya.", "S2_en": "with 5 years of experience designing enterprise data center networks and network automation.",
        "S3_id": "Fokus pada implementasi teknologi SD-WAN, arsitektur jaringan zero-trust, dan skrip otomasi perangkat jaringan.", "S3_en": "Focused on SD-WAN technology implementation, zero-trust network architecture, and device automation scripting.",
        "S4_id": "Menguasai sertifikasi CCNP, arsitektur SD-WAN, Palo Alto Networks, Python untuk Otomasi Jaringan, dan Ansible.", "S4_en": "Proficient in CCNP certification, SD-WAN architecture, Palo Alto Networks, Python for Network Automation, and Ansible."
    },

    # ---------------- 8. QA TESTER ----------------
    {
        "base_id": "P22", "role_group": "qa_tester", "level": "Junior", "exp_years": 1,
        "S1_id": "Penguji Kualitas Perangkat Lunak Junior", "S1_en": "Junior QA Tester",
        "S2_id": "memiliki pengalaman 1 tahun dalam pengujian manual aplikasi web dan seluler.", "S2_en": "with 1 year of experience in manual web and mobile application testing.",
        "S3_id": "Terbiasa menyusun dokumen skenario uji (test cases), eksekusi pengujian, dan pelaporan cacat perangkat lunak (bugs).", "S3_en": "Skilled in writing test case documentation, test execution, and software bug reporting.",
        "S4_id": "Menguasai Pengujian Manual, alur Jira Bug Tracking, Postman untuk pengujian API, dan skenario UI.", "S4_en": "Proficient in Manual Testing, Jira Bug Tracking workflows, Postman for API testing, and UI test cases."
    },
    {
        "base_id": "P23", "role_group": "qa_tester", "level": "Mid", "exp_years": 3,
        "S1_id": "Insinyur Otomasi QA Tingkat Menengah", "S1_en": "Mid-level QA Automation Engineer",
        "S2_id": "memiliki pengalaman 3 tahun dalam merancang skrip pengujian otomatis dan pengujian beban.", "S2_en": "with 3 years of experience designing automated test scripts and performance load testing.",
        "S3_id": "Berpengalaman mengembangkan kerangka kerja otomasi antarmuka web, pengujian API terintegrasi, dan siklus regresi otomatis.", "S3_en": "Experienced in developing web UI automation frameworks, integrated API testing, and automated regression cycles.",
        "S4_id": "Menguasai Selenium WebDriver, Cypress, Apache JMeter, skrip API Automation, dan JavaScript/Python.", "S4_en": "Proficient in Selenium WebDriver, Cypress, Apache JMeter, API Automation scripting, and JavaScript/Python."
    },
    {
        "base_id": "P24", "role_group": "qa_tester", "level": "Senior", "exp_years": 5,
        "S1_id": "Arsitek Otomasi QA Senior", "S1_en": "Senior QA Automation Architect",
        "S2_id": "memiliki pengalaman 5 tahun merancang strategi penjaminan kualitas enterprise dan integrasi CI/CD.", "S2_en": "with 5 years of experience designing enterprise quality assurance strategies and CI/CD integration.",
        "S3_id": "Fokus pada integrasi skrip pengujian otomatis ke dalam pipeline CI/CD, otomasi aplikasi seluler, dan metodologi TDD/BDD.", "S3_en": "Focused on integrating test suites into CI/CD pipelines, mobile application automation, and TDD/BDD methodologies.",
        "S4_id": "Menguasai Arsitektur Otomasi QA, Playwright, Appium untuk pengujian seluler, integrasi CI/CD, dan Cucumber BDD.", "S4_en": "Proficient in QA Automation Architecture, Playwright, Appium for mobile testing, CI/CD integration, and Cucumber BDD."
    }
]

# ----------------------------------------------------------------------------
# FUNSI RAKIT QUERY BERBASIS ATURAN KOMPONEN MODULAR
# ----------------------------------------------------------------------------
def assemble_query(profile, condition):
    if condition == "C0":     # 100% ID
        m1, m2, m3, m4 = profile["S1_id"], profile["S2_id"], profile["S3_id"], profile["S4_id"]
    elif condition == "C1":   # 75% ID / 25% EN
        m1, m2, m3, m4 = profile["S1_id"], profile["S2_id"], profile["S3_id"], profile["S4_en"]
    elif condition == "C2":   # 50% ID / 50% EN
        m1, m2, m3, m4 = profile["S1_en"], profile["S2_id"], profile["S3_id"], profile["S4_en"]
    elif condition == "C3":   # 25% ID / 75% EN
        m1, m2, m3, m4 = profile["S1_en"], profile["S2_en"], profile["S3_en"], profile["S4_id"]
    else:
        raise ValueError("Kondisi tidak valid!")

    # Gabungkan menjadi satu string query utuh
    full_text = f"{m1} {m2} {m3} {m4}".strip()
    words = re.findall(r'\b\w+\b', full_text)
    
    return {
        "profile_id": f"{profile['base_id']}_{condition}",
        "base_id": profile["base_id"],
        "role_group": profile["role_group"],
        "level": profile["level"],
        "exp_years": profile["exp_years"],
        "condition": condition,
        "query_text": full_text,
        "word_count": len(words)
    }

# ----------------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------------
def main():
    generated_profiles = []
    
    for base in BASE_PROFILES:
        for cond in ["C0", "C1", "C2", "C3"]:
            item = assemble_query(base, cond)
            generated_profiles.append(item)

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(generated_profiles, f, ensure_ascii=False, indent=2)

    print(f"=== PROSES SELESAI ===")
    print(f"Total profil berhasil dibuat: {len(generated_profiles)} item")
    print(f"Format penyimpanan: {OUT_FILE}")
    print(f"\nRincian per kondisi:")
    for cond in ["C0", "C1", "C2", "C3"]:
        count = sum(1 for p in generated_profiles if p["condition"] == cond)
        avg_words = sum(p["word_count"] for p in generated_profiles if p["condition"] == cond) / count
        print(f" - {cond}: {count} profil | Rata-rata panjang: {avg_words:.1f} kata")

if __name__ == "__main__":
    main()