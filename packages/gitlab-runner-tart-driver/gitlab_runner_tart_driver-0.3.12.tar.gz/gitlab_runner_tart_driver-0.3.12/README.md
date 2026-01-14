# Gitlab Runner Custom Tart Driver

- [Gitlab Runner Custom Tart Driver](#gitlab-runner-custom-tart-driver)
  - [About](#about)
  - [Setup](#setup)
    - [GitLab Runner Configuration](#gitlab-runner-configuration)
  - [GitLab CI](#gitlab-ci)
    - [Supported Environment Variables](#supported-environment-variables)
    - [Private OCI Registries](#private-oci-registries)
    - [Configuring the SSH Credentials](#configuring-the-ssh-credentials)
  - [Advanced Configuration](#advanced-configuration)
    - [GitLab Runner Installation](#gitlab-runner-installation)
    - [Concurrency](#concurrency)
    - [Host Cache and Builds directories](#host-cache-and-builds-directories)
    - [Volume Mounts](#volume-mounts)
    - [Auto Host Resource Distribution](#auto-host-resource-distribution)
    - [Custom `shell`](#custom-shell)
    - [Custom `pull_policy`](#custom-pull_policy)
    - [Excluding Images with `--exclude-image-expr`](#excluding-images-with---exclude-image-expr)
  - [CLI](#cli)
    - [CLI Parameters for `config.toml`](#cli-parameters-for-configtoml)
    - [Command `config`](#command-config)
    - [Command `prepare`](#command-prepare)
    - [Command `run`](#command-run)
    - [Command `cleanup`](#command-cleanup)

## About

[Tart](https://tart.run) is a virtualization toolset to build, run and manage macOS and Linux virtual machines on Apple Silicon. Tart is using Apple’s native Virtualization.Framework that was developed along with architecting the first M1 chip. This seamless integration between hardware and software ensures smooth performance without any drawbacks.

For storing virtual machine images Tart integrates with **OCI-compatible container registries**. This allows you to work with virtual machines as you used to with Docker containers.

This Custom GitLab Runner Extension integrates [Tart](https://tart.run) semlessly into the GitLabCI ecosystem with similar functionality as the well `docker-runner`

| *Executor*                                       | *Tart* | *Docker* |
| ------------------------------------------------ | ------ | -------- |
| Clean build environment for every build          | ✓      | ✓        |
| Reuse previous clone if it exists                | ✓      | ✓        |
| Runner file system access protected              | ✓      | ✓        |
| Migrate runner machine                           | ?      | ✓        |
| Zero-configuration support for concurrent builds | ✓      | ✓        |
| Complicated build environments                   | ✗      | ✓        |
| Debugging build problems                         | easy   | medium   |

## Setup

> **ATTENTION** This setup will only work on an Apple Silicon based machine

To setup the `gitlab-runner-tart-driver` you will need to go through the following steps

1. Install [Homebrew](https://brew.sh)
2. Install `python3`
3. Install `tart`
4. Install `gitlab-runner`
4. Install `gitlab-runner-tart-driver`
5. Configure and register a `custom` `gitlab-runner` with your GitLab Instance
6. Update `config.toml`

To install [Homebrew](https://brew.sh) simply execute the command

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Next we need to install `tart` by executing

```bash
brew install cirruslabs/cli/tart
```

We can verify to virtualization functionality by pulling an image for the official [tart managed images](https://github.com/orgs/cirruslabs/packages?tab=packages&q=macos)

```bash
tart clone ghcr.io/cirruslabs/macos-ventura-base:latest ventura-base
tart run ventura-base
```

After the image has been downloaded you will see a window come up with a virtualized OSX Ventura running

To run the `gitlab-runner-tart-driver` we will need a valid `python3` installation as well as the `gitlab-runner`

```bash
brew install python3 gitlab-runner
```

Finally we will need to install `gitlab-runner-tart-driver`.

```bash
pip install gitlab-runner-tart-driver
```

### GitLab Runner Configuration

Follow the guide [Install GitLab Runner on macOS](https://docs.gitlab.com/runner/install/osx.html#homebrew-installation-alternative).

1. [Register](https://docs.gitlab.com/runner/register/index.html#macos) your GitLab Runner and use the `custom` executor

```bash
gitlab-runner register
```

2. Install the service with `gitlab-runner install`

> **ATTENTION** The GitLab Runner currently fails to properly setup the LaunchAgent. The workaround described can be omitted as soon the the [Bug](https://gitlab.com/gitlab-org/gitlab-runner/-/issues/29324) has been resolved

```bash
# Fix missing log path issue
sudo mkdir -p /usr/local/var/log
sudo chmod a+rw /usr/local/var/log

gitlab-runner uninstall
gitlab-runner install
gitlab-runner start
```

3. Configure the `config.toml` for the tart custom driver

The `config.toml` should be located at `~/.gitlab-runner/config.toml`. Open it and add the following content

**config.toml**

```ini
[runners.custom]
    config_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    config_args = [ "config", '-x', '/opt/homebrew/bin/tart' ]
    config_exec_timeout = 200

    prepare_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    prepare_args = [ "prepare", '-x', '/opt/homebrew/bin/tart' ]
    prepare_exec_timeout = 200

    run_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    run_args = [ "run", '-x', '/opt/homebrew/bin/tart' ]

    cleanup_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    cleanup_args = [ "cleanup", '-x', '/opt/homebrew/bin/tart' ]
    cleanup_exec_timeout = 200
```

Now restart the gitlab-runner with `gitlab-runner restart`

## GitLab CI

One of the great advantages in using [Tart](https://tart.run) is that it gives almost all functionality to we are used from the standard `docker` executors allowing us to write GitLabCI piplines that do not need any or minimal adaptions for OSX.

> **ATTENTION:** The driver will always automatically login to your GitLab Registry using `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` and `CI_REGISTRY`

```yaml
stages:
 - build

run-on-tart:
  image: ghcr.io/cirruslabs/macos-ventura-base:latest
  stage:
    - build
  tags:
    - tart
  before_script:
    - brew install gitlab-runner # you will need to make sure `gitlab-runner` executable is available to be able to upload artifacts
  script:
    - echo "This is brought to you by tart" >> artifact.txt
  artifacts:
    paths:
      - artifact.txt
```

### Supported Environment Variables

| **Name**                              | **Default**    | **Description**                                                                                               |
| ------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------- |
| `TART_REGISTRY_USERNAME`              |                | Username to login to private OCI registry                                                                     |
| `TART_REGISTRY_PASSWORD`              |                | Password to login to private OCI registry                                                                     |
| `TART_REGISTRY`                       |                | Private OCI registry                                                                                          |
| `TART_PULL_POLICY`                    | if-not-present | define how runners pull tart images from registries. Options are `always`,`if-not-present`,`never`            |
| `TART_SSH_USERNAME`                   | admin          | Username to use to login to VM                                                                                |
| `TART_SSH_PASSWORD`                   | admin          | Password to use to login to VM                                                                                |
| `TART_EXECUTOR_HEADLESS`              | true           | Don't open a UI window.                                                                                       |
| `TART_EXECUTOR_SOFTNET_ENABLED`       | false          | Use software networking instead of the default shared (NAT) networking                                        |
| `TART_EXECUTOR_VNC_ENABLED`           | false          | Use screen sharing instead of the built-in UI. Note that Remote Login option should be enabled inside the VM. |
| `TART_EXECUTOR_INSTALL_GITLAB_RUNNER` | false          | Install a GitLabRunner into the VM to ensure full CI/CD functionality                                         |
| `TART_EXECUTOR_SHELL`                 | /bin/zsh       | The shell that should be used when running commands                                                           |
| `TART_EXECUTOR_TIMEOUT`               | 60             | Timeout for `tart ip` to respond with a valid IP                                                              |
| `TART_EXECUTOR_DISPLAY`               | 1920x1200      | Display resolution in format `WxH`                                                                            |

### Private OCI Registries

Oftentimes you might want to provide your own OCI-compliant images created with [Packer](https://www.packer.io) and the official [Tart Builder](https://developer.hashicorp.com/packer/plugins/builders/tart). If you push your images to a private registry you will need to provide the credentials for the `gitlab-runner-tart-driver` to login there first.

You can provide a default login registry using the `CLI` parameters (see **Command `prepare`**) but also provide the credentials from with each job variable definition

```yaml
stages:
 - build

variables:
    TART_REGISTRY_USERNAME: myuser@myregistry.com
    TART_REGISTRY_PASSWORD: <some_secret>
    TART_REGISTRY: private.registry.io

job1:
  image: private.registry.io/tart/xcode14:latest
  stage:
    - build
  tags:
    - tart
  before_script:
    - brew install gitlab-runner # you will need to make sure `gitlab-runner` executable is available to be able to upload artifacts
  script:
    - echo "This is brought to you by tart" >> artifact.txt
  artifacts:
    paths:
      - artifact.txt

job2:
  image: private.other.io/tart/xcode14:latest
  variables:
    # override the OCI login information for this job only
    TART_REGISTRY_USERNAME: myuser@other.com
    TART_REGISTRY_PASSWORD: <some_secret>
    TART_REGISTRY: private.other.io
  stage:
    - build
  tags:
    - tart
  before_script:
    - brew install gitlab-runner # you will need to make sure `gitlab-runner` executable is available to be able to upload artifacts
  script:
    - echo "This is brought to you by tart" >> artifact.txt
  artifacts:
    paths:
      - artifact.txt
```

### Configuring the SSH Credentials

The [Tart managed images](https://tart.run) come with a default user `admin` and password `admin` which will be used to establish an ssh connection. If you decide to provide your own images, you might opt for a different user and password. You can provide the default user and password using the `config.toml` within the `run` section using `--default-ssh-user` and `--default-ssh-password` or provide it from within your job

```yaml
job2:
  image: private.other.io/tart/xcode14:latest
  variables:
    # override the OCI login information for this job only
    TART_REGISTRY_USERNAME: myuser@other.com
    TART_REGISTRY_PASSWORD: <some_secret>
    TART_REGISTRY: private.other.io
    TART_SSH_USERNAME: gitlab
    TART_SSH_PASSWORD: gitlab
  stage:
    - build
  tags:
    - tart
  before_script:
    - brew install gitlab-runner # you will need to make sure `gitlab-runner` executable is available to be able to upload artifacts
  script:
    - echo "This is brought to you by tart" >> artifact.txt
  artifacts:
    paths:
      - artifact.txt
```

## Advanced Configuration

### GitLab Runner Installation

To have the full GitLabCI functionality in your pipelines like the capabilties to upload artifacts, you will need to *ensure* that the `gitlab-runner` is available within your VM. The `prepare` script can help you to ensure the presence and even install a specific version for you.
Use `--install-gitlab-runner` to tell the driver to check for a valid runner installation. Per default, if an installation is found that version is used. If you want to ensure that you have always the `latest` or a specific version you can use `--force-install-gitlab-runner` and `--gitlab-runner-version` to indicate your concrete setup.

The installation will follow these simple steps to ensure the proper `gitlab-runner` setup.

1. Check if gitlab-runner is already installed by trying to execute it
2. If the runner is not present or force install is enabled
   1. Check if `curl` can be used to download and install the version specified to `/usr/local/bin`
   2. Check if `wget` can be used to download and install the version specified to `/usr/local/bin`
   3. Check if `brew` can be used to install the version specified
   4. Fail if none of the tools is available

### Concurrency

Currently `tart` only supports two executions of VMs at the same time. This limits the scalability of the solution on a single host. Please ensure you are setting the `concurrent` setting to a maximum of `2` in your `config.toml`.

```ini
concurrent = 2 # <-- ATTENTION: ensure not sure go higher than '2'
check_interval = 0
shutdown_timeout = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "macos-tart-driver1"
  url = "https://gitlab.com/"
  id = 11111111
  token = "XXXXXXXXXXXX"
  token_obtained_at = 2023-04-03T07:21:42Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "custom"
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.custom]
    config_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    config_args = [ "config" ]

    prepare_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    prepare_args = [ "prepare", '-x', '/opt/homebrew/bin/tart', '--concurrency', '2', '--auto-resources' ]

    run_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    run_args = [ "run", '-x', '/opt/homebrew/bin/tart' ]

    cleanup_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
    cleanup_args = [ "cleanup", '-x', '/opt/homebrew/bin/tart' ]
```

### Host Cache and Builds directories

With `tart` it is possible to mount local directories into the VM. Mounting local directories brings a number of benefits like up tp 30% higher IO performance as well as a correct caching mechanism.
To enable Host-local caching and builds, simply pass `--builds-dir` and `--cache-dir` to the `prepare` command

```ini
prepare_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
prepare_args = [ "prepare", '-x', '/opt/homebrew/bin/tart', '--concurrency', '2', '--auto-resources', '--cache-dir', '/Users/gitlab/gitlab-runner/cache', '--builds-dir', '/Users/gitlab/gitlab-runner/builds']
```

### Volume Mounts

Just like with `docker` the `gitlab-runner-tart-driver` allows you to mount any arbitrary host path into your VM. This can be especially useful if you have to mount runner-local resources like shared test-data or additional caches into the executor. You can follow the standard docker syntax for *volume mounts* `--volume /my/local/dir:/opt/remote/dir`. Additionally you can also pass the `ro` flag to make the mount *read-only* i.e.  `--volume /my/local/dir:/opt/remote/dir:ro`.

```ini
[runners.custom]
  config_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
  config_args = [ "config" ]

  prepare_exec = "/opt/homebrew/bin/gitlab-runner-tart-driver"
  prepare_args = [ "prepare",
    '-x', '/opt/homebrew/bin/tart',
    '--concurrency', '2',
    '--auto-resources',
    '--volume /data/models/:/opt/data/models:ro']
```
### Auto Host Resource Distribution

`tart` images come with a pre-defined number of CPUs and Memory allocation. Typical numbers for default images are `cpu_count=4` and `memory=8192`. With the concurrency limitation of two VMs/images running at the same time this might not utilize your host system completely.
Per default, `--auto-resources` is enable for the `gitlab-runner-tart-driver` which will split the host resources equally to the VMs defined by `--concurrency`. The default concurrency is `1` and therefore will assign all host resources to the VM.

> **ATTENTION** make sure your `gitlab-runner` concurrency setting is the same as the `--concurrency` parameter you are passing to the `prepare` command

### Custom `shell`

You can use a custom shell to execute your commands. The default ist `/bin/zsh`

see **Command `run`**

### Custom `pull_policy`

You can use a custom `pull_policy`. The default policy is `if-not-present`. Use `TART_PULL_POLICY` to override the default pull policy

### Excluding Images with `--exclude-image-expr`

You can use the `--exclude-image-expr` option with the `prepare` command to prevent certain images from being used. This option can be specified multiple times, each with a Python regular expression. If the image name matches any of the provided expressions, the command will exit with an error.

**Example:**

```bash
gitlab-runner-tart-driver prepare --exclude-image-expr 'xcode:15.*' --exclude-image-expr 'ubuntu:.*-beta'
```

This will exclude any image matching `xcode:15.*` or `ubuntu:.*-beta`.

- The matching uses Python's `re.search`, so even substrings can match the pattern.
- Useful for preventing the use of unwanted or unsupported images in your CI pipeline.

## CLI

### CLI Parameters for `config.toml`

The `gitlab-runner-tart-driver` gives a number of advanced configuration options. Use `gitlab-runner-tart-driver [stage] --help` to get a full list of options that you can pass to the exectuable using your `config.toml` file.

```
Usage: gitlab-runner-tart-driver [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --version  Show the version and exit.
  --help         Show this message and exit.

Commands:
  cleanup  Command to greet a user.
  config   Implementation of the CONFIG stage of the Custom Executor.
  prepare  Prepare the environment and start the tart VM.
  run      Run commands.
```

### Command `config`

```
Usage: gitlab-runner-tart-driver config [OPTIONS]

  Implementation of the CONFIG stage of the Custom Executor. Details on how to
  use this command can be found at
  https://docs.gitlab.com/runner/executors/custom.html#config.

Options:
  --help                      Show this message and exit.
```

### Command `prepare`

```
Usage: gitlab-runner-tart-driver prepare [OPTIONS]

  Prepare the environment and start the tart VM.

Options:
  --cpu INTEGER                   Number of CPUs associated to VM
  --memory INTEGER                VM memory size in megabytes associated to VM
  --display TEXT                  VM display resolution in a format of
                                  <width>x<height>. For example, 1200x800
  --auto-resources / --no-auto-resources
                                  If enabled, the driver will divide system
                                  resources equally to the concurrent VMs.
  --concurrency INTEGER           Number of concurrent processes that are
                                  supported. ATTENTION tart currently only
                                  support two concurrent VMs
  --cache-dir TEXT                Caching dir to be used.
  --builds-dir TEXT               Path to the builds directory.
  --timeout INTEGER               Timeout in seconds for the VM to be
                                  reachable via SSH.
  --volume TEXT                   Volume mount definition with docker syntax.
                                  <host_dir>:<vm_dir>[:ro]
  --install-gitlab-runner         Will install the gitlab-runner if not
                                  present.
  --force-install-gitlab-runner   This will force the installation of the
                                  GitLab Runner independent of a previously
                                  installed version
  --gitlab-runner-version TEXT    The version of the GitLab Runner to be
                                  installed. Example '15.11.0'
  -x, --tart-executable TEXT      Path to the tart executable.
  --exclude-image-expr TEXT      Exclude images matching the given Python
                                  regular expression.
  --help                          Show this message and exit.
```

### Command `run`

```
Usage: gitlab-runner-tart-driver run [OPTIONS] SCRIPT STAGE

  Run commands.

Options:
  --timeout INTEGER            SSH connection timeout in seconds
  -x, --tart-executable TEXT   Path to the tart executable.
  --shell TEXT                 Path to the shell to be used for commands over
                               ssh.
  --help                       Show this message and exit.
```

### Command `cleanup`

```
Usage: gitlab-runner-tart-driver cleanup [OPTIONS]

  Command to greet a user.

Options:
  -x, --tart-executable TEXT  Path to the tart executable.
  --help                      Show this message and exit.
```