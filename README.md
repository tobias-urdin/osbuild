# OSBuild

Build-Pipelines for Operating System Artifacts

OSBuild is a pipeline-based build system for operating system artifacts. It
defines a universal pipeline description and a build system to execute them,
producing artifacts like operating system images, working towards an image
build pipeline that is more comprehensible, reproducible, and extendable.

See the `osbuild(1)` man-page for details on how to run osbuild, the definition
of the pipeline description, and more.

## Project

 * **Website**: <https://www.osbuild.org>
 * **Bug Tracker**: <https://github.com/osbuild/osbuild/issues>
 * **Matrix**: #image-builder on [fedoraproject.org](https://matrix.to/#/#image-builder:fedoraproject.org)
 * **Mailing List**: image-builder@redhat.com
 * **Changelog**: <https://github.com/osbuild/osbuild/releases>

### Contributing

Please refer to the [developer guide](https://www.osbuild.org/guides/developer-guide/index.html) to learn about our workflow, code style and more.

## Requirements

The requirements for this project are:

 * `bubblewrap >= 0.4.0`
 * `python >= 3.6`

Additionally, the built-in stages require:

 * `bash >= 5.0`
 * `coreutils >= 8.31`
 * `curl >= 7.68`
 * `qemu-img >= 4.2.0`
 * `rpm >= 4.15`
 * `tar >= 1.32`
 * `util-linux >= 235`
 * `skopeo`

At build-time, the following software is required:

 * `python-docutils >= 0.13`
 * `pkg-config >= 0.29`

Testing requires additional software:

 * `pytest`

## Build

Osbuild is a python script so it is not compiled.
To verify changes made to the code use included makefile rules:

 * `make lint` to run linter on top of the code
 * `make test-all` to run base set of tests
 * `sudo make test-run` to run extended set of tests (takes long time)

## Installation

Installing `osbuild` requires to not only install the `osbuild` module, but also
additional artifacts such as tools (i.e: `osbuild-mpp`) sources, stages, schemas
and SELinux policies.

For this reason, doing an installation from source is not trivial and the easier
way to install it is to create the set of RPMs that contain all these components.

This can be done with the `rpm` make target, i.e:

```sh
make rpm
```

A set of RPMs will be created in the `./rpmbuild/RPMS/noarch/` directory and can
be installed in the system using the distribution package manager, i.e:

```sh
sudo dnf install ./rpmbuild/RPMS/noarch/*.rpm
```

## Repository

 - **web**:   <https://github.com/osbuild/osbuild>
 - **https**: `https://github.com/osbuild/osbuild.git`
 - **ssh**:   `git@github.com:osbuild/osbuild.git`

## License

 - **Apache-2.0**
 - See LICENSE file for details.
