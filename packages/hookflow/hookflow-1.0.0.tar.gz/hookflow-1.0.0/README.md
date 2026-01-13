![Build Status](https://github.com/tekintian/hookflow/actions/workflows/test.yml/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/tekintian/hookflow/graph/badge.svg?token=d93ya8MfmB)](https://codecov.io/gh/tekintian/hookflow)

# Hookflow

> The fastest polyglot Git hooks manager out there

<img align="right" width="147" height="100" title="Hookflow logo"
     src="https://raw.githubusercontent.com/tekintian/hookflow/refs/heads/master/logo_sign.svg">

A Git hooks manager for Node.js, Ruby and many other types of projects.

* **Fast.** It is written in Go. Can run commands in parallel.
* **Powerful.** It allows to control execution and files you pass to your commands.
* **Simple.** It is single dependency-free binary which can work in any environment.

📖 [Read the introduction post](https://tekintian.com/chronicles/hookflow-knock-your-teams-code-back-into-shape?utm_source=hookflow)

<a href="https://tekintian.com/?utm_source=hookflow">
<img src="https://tekintian.com/badges/sponsored-by-tekintian.svg" alt="Sponsored by Tekintian" width="236" height="54"></a>

## Install

```bash
pip install hookflow
```

## Usage

Configure your hooks, install them once and forget about it: rely on the magic underneath.

#### TL;DR

```bash
# Configure your hooks
vim hookflow.yml

# Install them to the git project
hookflow install

# Enjoy your work with git
git add -A && git commit -m '...'
```

#### More details

- [**Configuration**](https://github.com/tekintian/hookflow/blob/master/docs/configuration.md) for `hookflow.yml` config options.
- [**Usage**](https://github.com/tekintian/hookflow/blob/master/docs/usage.md) for **hookflow** CLI options, supported ENVs, and usage tips.
- [**Discussions**](https://github.com/tekintian/hookflow/discussions) for questions, ideas, suggestions.
<!-- - [**Wiki**](https://github.com/tekintian/hookflow/wiki) for guides, examples, and benchmarks. -->
