# Amazon Bedrock Hands-On Guides 🚀

![Amazon Bedrock](https://img.shields.io/badge/Amazon-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AWS CDK](https://img.shields.io/badge/AWS-CDK-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A comprehensive collection of hands-on guides for mastering Amazon Bedrock with Infrastructure as Code (IaC) using AWS CDK. This repository provides practical, real-world examples to help you learn and implement Amazon Bedrock's powerful AI/ML capabilities.

## 📋 Table of Contents

- [About](#about)
- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Available Guides](#available-guides)
- [Upcoming Guides](#upcoming-guides)
- [Usage](#usage)
- [Contributing](#contributing)
- [Cost Considerations](#cost-considerations)
- [Support](#support)
- [License](#license)

## 🎯 About

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies through a single API. This repository provides step-by-step hands-on guides to help you:

- **Learn by doing** with practical, deployable examples
- **Understand core concepts** through real-world implementations  
- **Deploy infrastructure** using AWS CDK for reproducible environments
- **Explore different AI models** and their capabilities
- **Build production-ready solutions** with best practices

### 🎯 Target Audience

- **Developers** looking to integrate AI capabilities into applications
- **DevOps Engineers** wanting to deploy AI infrastructure as code
- **Solutions Architects** designing AI-powered systems
- **Students and Learners** exploring Amazon Bedrock capabilities
- **AI Enthusiasts** interested in hands-on AWS AI services

## ✅ Prerequisites

Before starting with these guides, ensure you have:

### Required Tools
```bash
# AWS CLI v2
aws --version

# AWS CDK
npm install -g aws-cdk
cdk --version

# Python 3.8+
python --version

# Git
git --version
```

### AWS Account Setup
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI configured with credentials
- ✅ Amazon Bedrock model access enabled
- ✅ Basic understanding of AWS services

### Knowledge Prerequisites
- Basic AWS concepts (IAM, Lambda, S3, API Gateway)
- Python programming fundamentals
- Command line interface familiarity
- Infrastructure as Code concepts

## 📁 Repository Structure

```
amazon-bedrock/
├── 01-fundamentals/           # Bedrock basics and core concepts
├── 02-image-generation/       # AI image generation with Titan
├── 03-background-removal/     # Image editing and manipulation
├── 04-generate-embedding/     # Text embeddings and vector operations
├── docs/                      # Additional documentation
├── scripts/                   # Utility scripts
├── LICENSE                    # MIT License
└── README.md                  # This file
```

Each guide directory contains:
```
guide-name/
├── README.md                  # Guide-specific instructions
├── app.py                     # CDK app entry point
├── requirements.txt           # Python dependencies
├── lambda/                    # Lambda function code
│   └── index.py
├── guide-name/                # CDK stack definitions
│   └── stack.py
└── tests/                     # Unit tests (where applicable)
```

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock
```

### 2. Set Up Your Environment
```bash
# Create virtual environment (recommended)
python -m venv bedrock-env
source bedrock-env/bin/activate  # On Windows: bedrock-env\Scripts\activate

# Install global dependencies
pip install -r requirements.txt
```

### 3. Bootstrap CDK (First Time Only)
```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### 4. Enable Bedrock Model Access
1. Navigate to Amazon Bedrock Console
2. Go to "Model access" in the left sidebar
3. Click "Enable specific models"
4. Enable required models for your chosen guide
5. Wait for approval (usually immediate for most models)

### 5. Choose Your First Guide
Start with `01-fundamentals` for beginners or jump to any specific use case that interests you!

## 📚 Available Guides

### 🎓 01. Fundamentals
**Level:** Beginner | **Duration:** 30 minutes | **Cost:** ~$0.50

Learn the basics of Amazon Bedrock, understand different models, and make your first API calls.

**What you'll build:**
- Simple Bedrock API integration
- Text generation with Claude
- Basic Lambda function setup

**Key concepts:** Foundation models, API calls, text generation

---

### 🎨 02. Image Generation
**Level:** Intermediate | **Duration:** 45 minutes | **Cost:** ~$2.00

Build a complete image generation API using Amazon Titan Image Generator.

**What you'll build:**
- REST API for image generation
- S3 storage integration
- Presigned URL generation
- CORS-enabled API Gateway

**Key concepts:** Image generation, API Gateway, S3 integration, presigned URLs

---

### 🖼️ 03. Background Removal
**Level:** Intermediate | **Duration:** 40 minutes | **Cost:** ~$1.50

Create an intelligent background removal service for images.

**What you'll build:**
- Image upload and processing pipeline
- Background removal using AI models
- Before/after image comparison
- Batch processing capabilities

**Key concepts:** Image manipulation, computer vision, batch processing

---

### 🔤 04. Generate Embedding
**Level:** Advanced | **Duration:** 60 minutes | **Cost:** ~$1.00

Implement text embeddings for semantic search and similarity matching.

**What you'll build:**
- Text embedding generation
- Vector similarity search
- Semantic search API
- Document clustering

**Key concepts:** Vector embeddings, semantic search, similarity matching, NLP

---

## 🔮 Upcoming Guides

We're continuously adding new guides! Here's what's coming next:

| Guide | Level | Status |
|-------|-------|--------|
| **RAG Implementation** | Advanced | 🏗️ In Progress |
| **Chatbot with Memory** | Intermediate | 📋 Planned |
| **Document Analysis** | Advanced | 📋 Planned |
| **Multi-Modal AI** | Expert | 📋 Planned |
| **Model Fine-Tuning** | Expert | 📋 Planned |
| **Production Monitoring** | Advanced | 📋 Planned |

**Want to suggest a guide?** [Open an issue](https://github.com/anveshmuppeda/amazon-bedrock/issues) with the tag `guide-request`.

## 💻 Usage

### Quick Start for Any Guide

1. **Navigate to the guide directory:**
   ```bash
   cd 02-image-generation  # Replace with your chosen guide
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Review the guide README:**
   ```bash
   cat README.md
   ```

4. **Deploy the infrastructure:**
   ```bash
   cd image-generation  # Adjust path as needed
   cdk deploy
   ```

5. **Test the deployment:**
   Follow the testing instructions in each guide's README.

6. **Clean up resources:**
   ```bash
   cdk destroy
   ```

### Best Practices

- 🔒 **Security:** Always follow AWS security best practices
- 💰 **Cost:** Monitor your AWS costs and clean up resources after testing
- 🏷️ **Tagging:** Use consistent resource tagging for organization
- 📝 **Documentation:** Read each guide's README thoroughly before starting
- 🧪 **Testing:** Test in a development environment first

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs** by opening an issue
- 💡 **Suggest improvements** or new guide ideas
- 📝 **Improve documentation** with clearer explanations
- 🔧 **Submit code improvements** via pull requests
- ⭐ **Share the repository** to help others learn

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-guide`
3. **Follow the existing code style and structure**
4. **Test your changes thoroughly**
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

### Guide Contribution Template

When contributing a new guide, please include:
- Clear README with step-by-step instructions
- Working CDK code with proper error handling
- Cost estimates and time requirements
- Prerequisites and learning objectives
- Testing instructions with sample inputs/outputs

## 💰 Cost Considerations

### Estimated Costs per Guide

*\*Costs are estimates for testing/learning purposes and may vary based on usage*

### Cost Optimization Tips

- 🕐 **Clean up resources** immediately after testing
- 📊 **Monitor AWS billing** dashboard regularly
- 🎯 **Use AWS Free Tier** where applicable
- 📈 **Set billing alerts** for cost control
- 🗑️ **Implement lifecycle policies** for S3 storage

## 🆘 Support

### Getting Help

- 📖 **Documentation:** Start with the specific guide's README
- 🐛 **Issues:** [GitHub Issues](https://github.com/anveshmuppeda/amazon-bedrock/issues) for bugs and questions
- 💬 **Discussions:** [GitHub Discussions](https://github.com/anveshmuppeda/amazon-bedrock/discussions) for general questions
- 📧 **Email:** [your-email@domain.com] for private inquiries

### Common Issues

| Issue | Solution |
|-------|----------|
| CDK Bootstrap Failed | Ensure AWS credentials are configured correctly |
| Model Access Denied | Enable specific models in Bedrock console |
| Lambda Timeout | Increase timeout duration in CDK stack |
| CORS Issues | Check API Gateway CORS configuration |
| High Costs | Review resource usage and implement cleanup |

### Troubleshooting Resources

- [AWS CDK Troubleshooting Guide](https://docs.aws.amazon.com/cdk/v2/guide/troubleshooting.html)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Support Center](https://console.aws.amazon.com/support/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

## 🌟 Acknowledgments

- **AWS Team** for creating Amazon Bedrock
- **CDK Community** for excellent documentation and examples
- **Contributors** who help improve these guides
- **Open Source Community** for inspiration and best practices

## 📈 Repository Stats

![GitHub stars](https://img.shields.io/github/stars/anveshmuppeda/amazon-bedrock?style=social)
![GitHub forks](https://img.shields.io/github/forks/anveshmuppeda/amazon-bedrock?style=social)
![GitHub issues](https://img.shields.io/github/issues/anveshmuppeda/amazon-bedrock)
![GitHub last commit](https://img.shields.io/github/last-commit/anveshmuppeda/amazon-bedrock)

---

### 🚀 Ready to Start Learning?

Choose your first guide and start building with Amazon Bedrock today!

**Beginner?** → Start with [01-fundamentals](./01-fundamentals/)  
**Want to generate images?** → Jump to [02-image-generation](./02-image-generation/)  
**Interested in embeddings?** → Try [04-generate-embedding](./04-generate-embedding/)

---

**Happy Learning! 🎓✨**

*If you find this repository helpful, please consider giving it a star ⭐ and sharing it with others who might benefit from these hands-on guides.*