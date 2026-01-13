# Jenkins Lockable Resources Plugin Library

[![Pipeline Status](https://gitlab.com/alexandre-perrin1/jenkins-lockable-resources/badges/master/pipeline.svg)](https://gitlab.com/alexandre-perrin1/jenkins-lockable-resources/-/commits/master)
[![codecov](https://codecov.io/gl/alexandre-perrin1/jenkins-lockable-resources/branch/master/graph/badge.svg)](https://codecov.io/gl/alexandre-perrin1/jenkins-lockable-resources/branch/master)

## About the library

This library and CLI utility was developped to access and control
[Jenkins Lockable-Resources plugin](https://plugins.jenkins.io/lockable-resources/)
because the current version of the plugin does not provide REST APIs.

## Prerequisite

As versions of python prior 3.6 are on their way to be deprecated, this tool was designed for
python 3.6 and onwards.

The command line interface has been written with [`click`](https://click.palletsprojects.com/).
An optionnal [`click-completion`](https://github.com/click-contrib/click-completion) 
package can also be installed in order to give shell completion feature.

## Install

The tool may be installed from sources with pip package manager from PyPi.

```
pip3 install jenkins-lockable-resources
```

## Example

The command line interface provides simple commands to show current status of
resources and to reserve or release resources.
Basic usage will prompt for username and API token.

```
lockable-resources --jenkins-url <your jenkins server url> <command>
Jenkins user: <your jenkins user name>
Jenkins token: 
...
```

All CLI options can be configured in a configuration file or by environment variables 
named after the option name in uppercase.

> **Warning:** 
>
> Be aware that storing credentials in clear is not safe.

**With configuration file:**

Create a `.lockable-resources.yml` local file or `~/.lockable-resources` user file and add the options:

```
jenkins_url: <your jenkins server url>
jenkins_user: <your jenkins user>
jenkins_token: <your jenkins api token>
```

**Environment variables:**

Example with a `.env` file:
```
JENKINS_URL=<your jenkins server url>
JENKINS_USER=<your jenkins user>
JENKINS_TOKEN=<your jenkins api token>
```

Then source the environment before running the command

```
source .env && lockable-resources <COMMAND>
```

### List resources

`list` command list all registered resources on jenkins lockable resources plugin.

### Get current resources info

`info` command list all the known information about the resources.

```
lockable-resources info
Resource1: FREE
Resource2: RESERVED by mr.bean@gmail.com
Resource3: RESERVED by mcgiver@gmail.com
Resource4: LOCKED by Nightly
...
```

### Reserve/Unreserve a resource

`reserve` command reserves a resource for your user name only. 
`unreserve` command releases the resource you own. 

```
lockable-resources reserve
Reserved Resource1

lockable-resources unreserve
Unreserved Resource1
```

### Listing what resources a user owns

`owned` command finds the current resource(s) reserved by a user (default to your user).

**Find the resource(s) you own**

```
lockable-resources owned
Resource1
```

**Find the resource(s) a user owns**

```
lockable-resources owned --user mcgiver@gmail.com
Resource3
```

## Testing

This package is tested using `pytest` framework. See `requirements-test.txt` for the
list of required packages.

Install requirements for testing:

```
pip3 install -r requirements-test.txt
```

The tests are held in `tests` directory.
Simply execute pytest from command line:

```
pytest tests
```

## Development

For development, install as editable:

```
pip3 install -e .
```

## License

The MIT License (MIT): Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
