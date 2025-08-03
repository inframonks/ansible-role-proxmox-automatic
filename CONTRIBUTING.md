# Ansible Role: proxmox_automatic - Contributing Guide

Thank you for your interest in contributing! This guide helps you contribute to this project.

## 🚀 Types of Contributions

We welcome all kinds of contributions:

- 🐛 **Bug Reports** - Report issues or bugs
- ✨ **Feature Requests** - Suggest new features
- 📖 **Documentation** - Improve or extend the docs
- 🔧 **Code Contributions** - Fix bugs or implement features
- 🧪 **Tests** - Add tests or improve existing ones
- 💬 **Discussions** - Share ideas and best practices

## 📋 Before You Start

1. **Search for existing issues** - Someone might already be working on the problem
2. **Create an issue** - For larger changes, discuss your idea first
3. **Read the documentation** - Understand the current functionality

## 🔧 Development Setup

### Prerequisites

```bash
# Install Ansible and tools
pip install ansible ansible-lint yamllint

# Clone repository
git clone https://github.com/inframonks/ansible-role-proxmox-automatic.git
cd ansible-role-proxmox-automatic

# Install dependencies
ansible-galaxy collection install community.general ansible.posix
```

### Development Environment

```bash
# Run linting
yamllint .
ansible-lint

# Run tests
ansible-playbook tests/test.yml -i tests/inventory/hosts.yml --syntax-check
ansible-playbook tests/test.yml -i tests/inventory/hosts.yml --check
```

## 📝 Pull Request Process

### 1. Fork and Create Branch

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/ansible-role-proxmox-automatic.git
cd ansible-role-proxmox-automatic

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Development

- **Code Style**: Follow Ansible best practices
- **Commits**: Use meaningful commit messages
- **Tests**: Add tests for new functionality
- **Documentation**: Update README.md if needed

### 3. Testing

```bash
# Linting
yamllint .
ansible-lint

# Syntax Check
ansible-playbook tests/test.yml --syntax-check

# Dry Run Test
ansible-playbook tests/test.yml --check
```

### 4. Create Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Create a Pull Request on GitHub
3. Fill out the PR template completely
4. Wait for review and feedback

## 🎯 Code Standards

### Ansible Best Practices

- Use meaningful task names
- Use tags for all tasks
- Follow YAML indentation (2 spaces)
- Use `ansible.builtin.*` for core modules
- Document complex logic with comments

### Variable Naming Convention

```yaml
# Prefix for all variables
proxmox_automatic_*

# Examples
proxmox_automatic_memory: 2048
proxmox_automatic_storage_config: []
proxmox_automatic_networks: []
```

### Commit Message Format

```
type(scope): short description

Longer description if needed.

Fixes #123
```

**Types:** feat, fix, docs, style, refactor, test, chore

## 🧪 Testing

### Local Tests

```bash
# Complete test run
make test  # if Makefile exists

# Or manually:
yamllint .
ansible-lint
ansible-playbook tests/test.yml --syntax-check
```

### Test Environment

For comprehensive tests you need:
- Proxmox VE test environment
- Ansible Controller (Linux/macOS)
- Test inventory with at least one host

## 📖 Documentation

### README Updates

When changing:
- Variables → Update variable tables
- Features → Add to feature list
- Configuration → Add examples
- Dependencies → Update requirements

### Adding Examples

New features should always include examples:

```yaml
# Example for new storage option
proxmox_automatic_storage_config:
  - name: virtio0
    size: "20"
    new_option: "example_value"  # New option explained
```

## 🐛 Bug Reports

Good bug reports contain:
- **Clear description** of the problem
- **Reproduction steps**
- **Expected vs. actual behavior**
- **Environment details** (OS, Ansible version, etc.)
- **Relevant logs** (without sensitive data!)
- **Minimal reproduction configuration**

## ✨ Feature Requests

Good feature requests contain:
- **Use case description** - Why is this feature useful?
- **Proposed API** - How should it be configured?
- **Alternatives** - Other approaches considered?
- **Backwards compatibility** - Avoid breaking changes

## 📞 Getting Help

- 🐛 **Bugs**: Create an issue with the Bug Report template
- ❓ **Questions**: Use GitHub Discussions or Question template
- 💬 **Chat**: [If Discord/Slack available]
- 📧 **Email**: [Maintainer email if available]

## 📄 License

By contributing, you agree that your work will be published under the same license as the project.

---

**Thank you for your contribution! 🎉**
