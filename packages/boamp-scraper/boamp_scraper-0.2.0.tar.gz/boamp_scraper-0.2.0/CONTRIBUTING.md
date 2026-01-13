# Contributing to BOAMP Scraper

First off, thank you for considering contributing to BOAMP Scraper! 🎉

## 🤝 How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Describe the bug clearly
- Include steps to reproduce
- Add your environment details (Python version, OS)

### Suggesting Enhancements

- Open an issue with the label "enhancement"
- Describe your feature request
- Explain why it would be useful

### Pull Requests

1. **Fork the repo**
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Test your changes**: `python examples/basic.py`
5. **Commit**: `git commit -m "feat: add your feature"`
6. **Push**: `git push origin feature/your-feature`
7. **Open a PR** on GitHub

## 📝 Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions small and focused

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring
- `test:` for tests
- `chore:` for maintenance

**Examples:**
```bash
git commit -m "feat: add region filter"
git commit -m "fix: handle timeout errors"
git commit -m "docs: update README examples"
```

## 🧪 Testing

Before submitting a PR:

```bash
# Run examples to verify
python examples/basic.py
python examples/advanced_filters.py
python examples/export_csv.py

# (Future) Run tests
# pytest tests/
```

## 📚 Documentation

- Update README.md if you add features
- Add docstrings to new functions/classes
- Create examples for new features

## 🎯 Current Priorities (Week 1-4)

### High Priority
- [ ] Fix real BOAMP selectors (replace mock data)
- [ ] Add proper error handling
- [ ] Improve logging
- [ ] Add unit tests
- [ ] Add pytest setup

### Medium Priority
- [ ] Add more examples
- [ ] Improve documentation
- [ ] Add type checking (mypy)
- [ ] Add linting (ruff, black)

### Low Priority
- [ ] Add CI/CD (GitHub Actions)
- [ ] Add code coverage
- [ ] Performance optimizations

## 💡 Need Help?

- Open an issue with the label "help wanted"
- Join discussions on GitHub
- Check existing issues/PRs

## 📜 Code of Conduct

- Be respectful
- Be constructive
- Focus on what's best for the community

## 🚀 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/Ouailleme/boamp-scraper.git
   cd boamp-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Test it works**
   ```bash
   python examples/basic.py
   ```

4. **Make your changes**

5. **Test again**

6. **Submit PR**

## 📝 Questions?

Open an issue or start a discussion!

---

**Thank you for contributing!** 🙏

Every contribution makes this project better.

