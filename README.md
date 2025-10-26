# PediAssist - AI-Powered Pediatric Subspecialty Treatment Assistant

**Empowering general pediatricians with instant access to subspecialty-level treatment planning.**

## 🎯 Vision

"Every pediatrician deserves a team of subspecialist consultants in their pocket"

PediAssist eliminates fragmented care and enables comprehensive pediatric healthcare delivery without unnecessary referrals.

## 🏥 Problem Solved

- General pediatricians lack immediate subspecialty guidance for complex conditions
- Patient experience becomes fragmented with multiple referrals  
- Delays in treatment initiation due to referral wait times
- Knowledge gaps in managing conditions outside core pediatric training
- Limited access to subspecialists in underserved areas

## ✨ Key Features

### Comprehensive Subspecialty Coverage
- **Neurodevelopmental & Behavioral**: ADHD, ASD, learning disabilities, anxiety, depression
- **ENT**: Recurrent otitis media, adenotonsillar hypertrophy, OSA
- **Allergy & Immunology**: Food allergies, asthma, atopic dermatitis
- **Dermatology**: Eczema, acne, warts, molluscum
- **Dental & Oral Health**: Caries prevention, fluoride protocols
- **Plus**: Gastroenterology, Endocrinology, Cardiology, Pulmonology, Nephrology, Orthopedics

### Three Levels of Detail
1. **Quick Summary** (30 seconds): Red flags, first-line treatment, timeline
2. **Detailed Protocol** (5 minutes): Complete pharmacological, non-pharmacological, monitoring
3. **Subspecialist Deep Dive** (15 minutes): Pathophysiology, evidence base, refractory cases

### Patient Communication System
- **Steve Jobs Simplicity**: 5th-grade reading level
- **Age-Adapted Explanations**: 3-5 (pictures), 6-10 (stories), 11-14 (simple science), 15-18 (respectful)
- **Multiple Formats**: Printable handouts, text reminders, email summaries

### Privacy-First Architecture
- **BYOK (Bring Your Own Key)**: Use your own AI provider API keys
- **Local Deployment**: All data stays on your infrastructure
- **HIPAA Compliant**: No PHI storage, encrypted communication
- **Cost Control**: Token usage tracking, budget limits

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- 8GB RAM minimum
- Your own AI provider API key (OpenAI, Anthropic, Azure, etc.)

### Installation
```bash
# Clone repository
git clone https://github.com/yourorg/pediassist.git
cd pediassist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API credentials

# Start services
docker-compose up -d

# Run CLI
python pediassist.py
```

### Quick Test
```bash
# Test the web interface
open http://localhost:8000/simple

# Test API endpoints
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"age": 5, "chief_complaint": "cough and fever"}'
```

### Usage Examples
```bash
# Quick consultation
python pediassist.py --diagnosis "ADHD combined presentation" --age 8 --level quick

# Detailed protocol
python pediassist.py --diagnosis "recurrent otitis media" --age 4 --context "3 episodes in 6 months" --level detailed

# With patient communication
python pediassist.py --diagnosis "atopic dermatitis" --age 2 --include-parent-handout --include-child-explanation
```

## 🏗️ Architecture

```
Frontend Layer (CLI + Web)
    ↓
Application Logic (Diagnosis Parser, Treatment Generator)
    ↓
AI/LLM Integration (BYOK Support - OpenAI, Anthropic, Local)
    ↓
Knowledge Base (PostgreSQL + Vector DB + Clinical Guidelines)
    ↓
Security & Privacy (Encryption, Audit Logging, License Management)
```

## 🚀 Deployment

### Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Cloud platforms (Render, Railway, DigitalOcean)
- Self-hosted solutions
- Production considerations

## 📋 Development Roadmap

- **Phase 1** (Months 1-2): MVP CLI Tool - 5 core subspecialties
- **Phase 2** (Months 3-4): Comprehensive Coverage - All 10 categories
- **Phase 3** (Months 5-6): Team Features - Delegation protocols
- **Phase 4** (Months 7-8): Enterprise & Scale - API, EMR integration

## 💳 Licensing

- **Free Tier**: 50 queries/month, basic protocols, CLI only
- **Professional** ($99/month): Unlimited queries, full coverage, web interface
- **Enterprise**: Custom pricing, multi-location, API access, SSO

## 🔒 Privacy & Compliance

- No patient identifiers stored
- Local deployment keeps data on your infrastructure
- HIPAA compliant architecture
- Audit logging without PHI
- Right to data deletion

## 🤝 Contributing

We welcome contributions from pediatricians, developers, and healthcare professionals. Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourorg/pediassist/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/pediassist/discussions)
- **Email**: support@pediassist.com

## ⚠️ Medical Disclaimer

PediAssist is a clinical decision support tool and does not provide medical advice. Always use your clinical judgment and consult with appropriate specialists when needed. This tool is intended for licensed healthcare providers only.