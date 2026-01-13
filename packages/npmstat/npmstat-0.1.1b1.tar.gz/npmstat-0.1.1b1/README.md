[![PyPI Version](https://img.shields.io/pypi/v/npmstat?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/npmstat/)
[![GitHub Release Version](https://img.shields.io/github/v/release/cssnr/npmstat?logo=github)](https://github.com/cssnr/npmstat/releases)
[![TOML Python Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcssnr%2Fnpmstat%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml&query=%24.project.requires-python&logo=python&logoColor=white&label=python)](https://github.com/cssnr/npmstat?tab=readme-ov-file#readme)
[![PyPI Downloads](https://img.shields.io/pypi/dm/npmstat?logo=pypi&logoColor=white)](https://pypistats.org/packages/npmstat)
[![Pepy Total Downloads](https://img.shields.io/pepy/dt/npmstat?logo=pypi&logoColor=white&label=total)](https://clickpy.clickhouse.com/dashboard/npmstat)
[![Codecov](https://codecov.io/gh/cssnr/npmstat/graph/badge.svg?token=A8NDHZ393X)](https://codecov.io/gh/cssnr/npmstat)
[![Workflow Lint](https://img.shields.io/github/actions/workflow/status/cssnr/npmstat/lint.yaml?logo=cachet&label=lint)](https://github.com/cssnr/npmstat/actions/workflows/lint.yaml)
[![Workflow Test](https://img.shields.io/github/actions/workflow/status/cssnr/npmstat/test.yaml?logo=cachet&label=test)](https://github.com/cssnr/npmstat/actions/workflows/test.yaml)
[![Deployment PyPi](https://img.shields.io/github/deployments/cssnr/npmstat/pypi?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/npmstat/)
[![Deployment Docs](https://img.shields.io/github/deployments/cssnr/npmstat/docs?logo=materialformkdocs&logoColor=white&label=docs)](https://cssnr.github.io/npmstat/)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/cssnr/npmstat?logo=github&label=updated)](https://github.com/cssnr/npmstat/pulse)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/cssnr/npmstat?logo=bookstack&logoColor=white&label=repo%20size)](https://github.com/cssnr/npmstat)
[![GitHub Top Language](https://img.shields.io/github/languages/top/cssnr/npmstat?logo=htmx&logoColor=white)](https://github.com/cssnr/npmstat?tab=readme-ov-file#readme)
[![GitHub Contributors](https://img.shields.io/github/contributors-anon/cssnr/npmstat?logo=github)](https://github.com/cssnr/npmstat/graphs/contributors)
[![GitHub Issues](https://img.shields.io/github/issues/cssnr/npmstat?logo=github)](https://github.com/cssnr/npmstat/issues)
[![GitHub Discussions](https://img.shields.io/github/discussions/cssnr/npmstat?logo=github)](https://github.com/cssnr/npmstat/discussions)
[![GitHub Forks](https://img.shields.io/github/forks/cssnr/npmstat?style=flat&logo=github)](https://github.com/cssnr/npmstat/forks)
[![GitHub Repo Stars](https://img.shields.io/github/stars/cssnr/npmstat?style=flat&logo=github)](https://github.com/cssnr/npmstat/stargazers)
[![GitHub Org Stars](https://img.shields.io/github/stars/cssnr?style=flat&logo=github&label=org%20stars)](https://cssnr.github.io/)
[![Discord](https://img.shields.io/discord/899171661457293343?logo=discord&logoColor=white&label=discord&color=7289da)](https://discord.gg/wXy6m2X8wY)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-72a5f2?logo=kofi&label=support)](https://ko-fi.com/cssnr)

# NPM Stat

<a title="NPM Stat" href="https://cssnr.github.io/npmstat/" target="_blank">
<img alt="NPM Stat" align="right" width="128" height="auto" src="https://cssnr.github.io/npmstat/assets/images/logo.svg"></a>

- [Install](#install)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

Get NPM Package Stats and Info from the command line or as a Python module.

## Install<a id="install"></a>

Install From PyPI: <https://pypi.org/p/npmstat>

```shell
pip install npmstat
```

```shell
uv tool install npmstat
```

From Homebrew: <https://github.com/cssnr/homebrew-tap>

```shell
brew install cssnr/tap/npmstat
```

From GitHub: https://github.com/cssnr/npmstat/releases/latest

```shell
curl https://i.jpillora.com/cssnr/npmstat! | bash
```

See [jpillora/installer](https://github.com/jpillora/installer) for more details.  
Alternatively, you can manually download a release for your system.

- [Windows x86_64](https://github.com/cssnr/npmstat/releases/latest/download/windows-amd64.zip) _amd64_
- [macOS Apple Intel](https://github.com/cssnr/npmstat/releases/latest/download/macos-amd64.zip) _amd64_
- [macOS Apple Silicon](https://github.com/cssnr/npmstat/releases/latest/download/macos-arm64.zip) _arm64_
- [Linux x86_64](https://github.com/cssnr/npmstat/releases/latest/download/linux-amd64.zip) _amd64_
- [Linux ARM](https://github.com/cssnr/npmstat/releases/latest/download/linux-arm64.zip) _arm64_

[![View Documentation](https://img.shields.io/badge/view_documentation-blue?style=for-the-badge&logo=googledocs&logoColor=white)](https://cssnr.github.io/npmstat/)

## Usage<a id="usage"></a>

To use run `npmstat` from your command line.

```text
 Usage: npmstat [OPTIONS] COMMAND [ARGS]...

 Example: npmstat -v stats @cssnr/vitepress-swiper

┌─ Options ──────────────────────────────────────────────────────────────────────────┐
│ --verbose             -v      INTEGER  Verbose Output (jq safe). [default: 0]      │
│ --version             -V               Show App Version.                           │
│ --clear-cache         -C               Clear Request Cache.                        │
│ --install-completion                   Install completion for the current shell.   │
│ --show-completion                      Show completion for the current shell, to   │
│                                        copy it or customize the installation.      │
│ --help                -h               Show this message and exit.                 │
└────────────────────────────────────────────────────────────────────────────────────┘
┌─ Commands ─────────────────────────────────────────────────────────────────────────┐
│ info    Get Package Information.                                                   │
│ stats   Get Package Download Stats.                                                │
└────────────────────────────────────────────────────────────────────────────────────┘
```

[![View Documentation](https://img.shields.io/badge/view_documentation-blue?style=for-the-badge&logo=googledocs&logoColor=white)](https://cssnr.github.io/npmstat/)

## Support<a id="support"></a>

If you run into any issues or need help getting started, please do one of the following:

- Report an Issue: <https://github.com/cssnr/npmstat/issues>
- Q&A Discussion: <https://github.com/cssnr/npmstat/discussions/categories/q-a>
- Request a Feature: <https://github.com/cssnr/npmstat/issues/new?template=1-feature.yaml>
- Chat with us on Discord: <https://discord.gg/wXy6m2X8wY>

[![Features](https://img.shields.io/badge/features-brightgreen?style=for-the-badge&logo=googleanalytics&logoColor=white)](https://github.com/cssnr/npmstat/issues/new?template=1-feature.yaml)
[![Issues](https://img.shields.io/badge/issues-red?style=for-the-badge&logo=southwestairlines&logoColor=white)](https://github.com/cssnr/npmstat/issues)
[![Discussions](https://img.shields.io/badge/discussions-blue?style=for-the-badge&logo=rocketdotchat&logoColor=white)](https://github.com/cssnr/npmstat/discussions)
[![Discord](https://img.shields.io/badge/discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/wXy6m2X8wY)

## Contributing<a id="contributing"></a>

If you would like to submit a PR, please review the [CONTRIBUTING.md](#contributing-ov-file).

Please consider making a donation to support the development of this project
and [additional](https://cssnr.com/) open source projects.

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cssnr)

For a full list of current projects visit: [https://cssnr.github.io/](https://cssnr.github.io/)
