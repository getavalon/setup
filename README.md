# setup

Vanilla distribution, including example projects and dependencies

<br>

### Development

To use latest up-to-date repositories alongside avalon-setup while developing, you can override the submodules used internally via environment variables.

**avalon-local.bat**

```bat
@echo off

set AVALON_CORE=<path/to/avalon-core>
set AVALON_LAUNCHER=<path/to/avalon-launcher>
set AVALON_PROJECTS=<path/to/avalon-examples>
set AVALON_CONFIG=<my_config>
set AVALON_LABEL=<my label>
set AVALON_SENTRY=<replace me>
set AVALON_MONGO=mongodb://<mongodb-address>

set PYTHONPATH=<path/to/config>;%PYTHONPATH%

python <path/to/avalon-setup>/avalon.py %*
```