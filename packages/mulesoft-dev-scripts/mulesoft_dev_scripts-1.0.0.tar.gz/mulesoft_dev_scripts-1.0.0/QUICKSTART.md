# 🚀 Quick Start Guide

Get started with MuleSoft Developer Scripts in minutes!

## 📦 What's Included

This repository contains **9 independent projects**, each solving specific MuleSoft problems:

1. **config-validator** - Validate properties and configuration files ✅ **READY**
2. **runtime-diagnostics** - Check runtime compatibility and issues ✅ **READY**
3. **log-analyzer** - Analyze logs for common issues ✅ **READY**
4. **security-scanner** - Scan for security vulnerabilities ✅ **READY**
5. **api-validator** - Validate API configurations ✅ **READY**
6. **munit-analyzer** - Analyze MUnit test coverage ✅ **READY**
7. **architecture-analyzer** - Static analysis for architecture issues (coming soon)
8. **cloudhub-readiness** - CloudHub deployment readiness (coming soon)
9. **project-health** - Project health scoring (coming soon)

## 🎯 Start Here: Most Common Issues

### 1. Configuration Issues (Most Common!)

**Problem:** Properties not resolving, missing placeholders

```bash
# With your project
cd config-validator
python validate-properties.py /path/to/your/mule/project

# Or test with example project
python validate-properties.py ../examples/sample-mule-project
```

### 2. Runtime Issues

**Problem:** App won't start, Java version issues, port conflicts

```bash
cd runtime-diagnostics
./mule-runtime-check.sh /path/to/your/mule/project
```

### 3. Security Issues

**Problem:** Hardcoded secrets, insecure configurations

```bash
cd security-scanner
python secret-scan.py --path /path/to/your/mule/project
```

### 4. Log Analysis

**Problem:** Can't find issues in logs, missing correlation IDs

```bash
# With your logs
cd log-analyzer
python analyze-logs.py /path/to/your/logs/application.log

# Or test with sample logs
python analyze-logs.py ../examples/sample-logs/application.log
```

## 📝 Example Workflow

### Before Deployment

```bash
# 1. Validate configuration
cd config-validator && python validate-properties.py ../my-mule-app

# 2. Check runtime compatibility
cd ../runtime-diagnostics && ./mule-runtime-check.sh ../my-mule-app

# 3. Security scan
cd ../security-scanner && python secret-scan.py --path ../my-mule-app --fail-on high
```

### After Deployment (Troubleshooting)

```bash
# Analyze logs for issues
cd log-analyzer && python analyze-logs.py ../logs/application.log --verbose
```

## 🧪 Testing Without Real Projects

**Don't have MuleSoft projects?** No problem! We've included example projects for testing:

```bash
# Test all scripts with example projects
cd examples
./test-all-scripts.sh

# Or test individual scripts
cd config-validator
python validate-properties.py --project-path ../examples/sample-mule-project
```

See [examples/README.md](./examples/README.md) for details on the sample projects.

## 🔧 Requirements

- **Python 3.7+** (for Python scripts)
- **Bash 4.0+** (for shell scripts)
- **MuleSoft project** or log files (or use the example projects!)

## 💡 Tips

1. **Run in CI/CD**: Add scripts to your build pipeline
2. **Pre-commit hooks**: Validate before committing
3. **Combine scripts**: Chain multiple validators together
4. **JSON output**: Use `--format json` for CI/CD integration

## 🆘 Need Help?

Each project has its own detailed README with:
- Problem descriptions
- Usage examples
- Error scenarios
- Troubleshooting tips

Navigate to any project folder and read its README.md!

## 🤝 Contributing

Found a bug or want to add a feature? Each project is maintained independently - check the project's README for contribution guidelines.

---

**Ready to solve MuleSoft problems? Pick a script and run it!** 🚀

