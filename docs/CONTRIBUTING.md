# Contributing to Dynamic Scoliosis Credentials System

Thank you for your interest in contributing to this life-saving healthcare technology! This project enables emergency responders to access critical patient information and helps healthcare providers establish verifiable credentials.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Use configuration '...'
3. See error

**Expected behavior**
What you expected to happen.

**System Information:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.9.5]
- Package version: [e.g. 1.0.0]

**Configuration**
Include relevant configuration files (remove sensitive data).

**Error Output**
```
Complete error traceback
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description** of the enhancement
- **Step-by-step description** of the suggested enhancement
- **Explanation of why** this enhancement would be useful
- **Medical use case** if applicable - how does this save lives or improve healthcare?

### Contributing Code

#### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dynamic_scoliosis.git
   cd dynamic_scoliosis
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Run tests to verify setup**
   ```bash
   python -m pytest tests/ -v
   ```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guidelines
   - Add or update tests
   - Update documentation if needed

3. **Run tests and checks**
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Check code formatting
   black src/ tests/
   
   # Check imports
   isort src/ tests/
   
   # Run linting
   flake8 src/ tests/
   
   # Type checking (optional but recommended)
   mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add meaningful commit message"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Pull Request Guidelines

- **Clear title and description** of what the PR does
- **Link to related issues** using `Fixes #issue_number`
- **Include tests** for new functionality
- **Update documentation** if you're adding/changing functionality
- **Follow the code style** guidelines below
- **Medical validation** - if touching medical logic, explain the healthcare impact

## Code Style Guidelines

### Python Code Style

- **Use Black** for code formatting: `black src/ tests/`
- **Use isort** for import sorting: `isort src/ tests/`
- **Follow PEP 8** guidelines
- **Maximum line length**: 88 characters (Black default)

### Documentation Style

- **Use clear, concise language**
- **Include practical examples**
- **Focus on life-saving applications** where relevant
- **Follow markdown best practices**

### Commit Message Guidelines

Use conventional commit format:
```
type(scope): description

body (optional)

footer (optional)
```

**Types:**
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `test`: adding/updating tests
- `refactor`: code refactoring
- `style`: formatting changes
- `chore`: maintenance tasks

**Examples:**
```
feat(qr): add compression support for QR codes
fix(cli): resolve validation error for patient records  
docs(emergency): add cardiac arrest scenario
test(generator): add Kim practitioner credential tests
```

## Testing Guidelines

### Writing Tests

- **Use pytest** framework
- **Follow the Kim-centered approach** - use Kim Johnson as the example in tests
- **Test both success and failure cases**
- **Include medical scenarios** where applicable
- **Test with realistic medical data**

### Test Structure

```python
def test_kim_emergency_scenario():
    """Test Kim's emergency medical record generation."""
    # Given: Kim's medical configuration
    config = create_kim_patient_config()
    
    # When: Generate emergency credential
    generator = CredentialGenerator(config)
    credential = generator.generate_credential()
    
    # Then: Verify critical medical information
    assert credential["credentialSubject"]["bloodType"] == "B+"
    assert "Codeine" in credential["credentialSubject"]["allergies"]
```

### Test Categories

- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions  
- **Emergency scenario tests**: Test life-saving use cases
- **CLI tests**: Test command-line interface
- **Validation tests**: Test W3C compliance

## Medical Content Guidelines

### Medical Accuracy

- **Verify medical terminology** with healthcare professionals
- **Use realistic medical scenarios** (based on Kim examples)
- **Include proper medical disclaimers**
- **Validate emergency response procedures**

### Healthcare Privacy

- **Use only example/fictional data** in documentation
- **Follow HIPAA-aware design principles**
- **Include privacy considerations** in code comments
- **Document data handling practices**

### Emergency Response Focus

- **Prioritize life-saving information** in QR codes
- **Include time-critical medical alerts**
- **Test emergency scanning scenarios**
- **Validate with emergency medical professionals** if possible

## Documentation Contributions

### Types of Documentation

1. **User guides** - How to use the system
2. **Medical protocols** - Emergency response procedures
3. **API documentation** - Technical reference
4. **Real-world scenarios** - Practical use cases
5. **Security guides** - Implementation best practices

### Documentation Standards

- **Use clear headings** and table of contents
- **Include practical examples** with Kim-centered scenarios
- **Add code blocks** with syntax highlighting
- **Include emergency contact information** (fictional examples only)
- **Focus on actionable information**

## Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive to all contributors
- **Focus on constructive feedback**
- **Remember this is life-saving technology** - take medical accuracy seriously
- **Help newcomers** understand the healthcare context
- **Maintain professional standards** appropriate for medical software

### Getting Help

- **Check existing documentation** first
- **Search closed issues** for similar problems  
- **Ask specific questions** with relevant context
- **Include medical use case** if applicable
- **Be patient** - contributors volunteer their time

## Recognition

Contributors will be recognized in:
- **README acknowledgments**
- **Release notes**
- **Documentation credits**

Significant contributors may be invited to:
- **Medical advisory discussions**
- **Feature planning sessions**
- **Healthcare integration planning**

## Questions?

- **Open an issue** for general questions
- **Start a discussion** for broader topics
- **Email maintainers** for sensitive security issues

Thank you for helping save lives through technology!

---

**Remember: This system handles critical medical information. Always consider the life-saving impact of your contributions.** 