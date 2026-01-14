# th2 gRPC codec library (0.2.0)

This library contains proto messages and `Codec` service with RPC methods that are used in [th2 codec](https://github.com/th2-net/th2-codec "th2-codec"). See [codec.proto](src/main/proto/th2_grpc_codec/codec.proto "codec.proto") file for details. <br>
Tool generates code from `.proto` files and uploads built packages (`.proto` files and generated code) to the specified repositories.

## How to maintain a project
1. Perform the necessary changes.
2. Update the package version of Java in `gradle.properties` file.
3. Update the package version of Python in `package_info.json` file.
4. Commit everything.

### Java
If you wish to manually create and publish a package for Java, run the following command:
```
gradle --no-daemon clean build publish artifactoryPublish \
       -Purl=${URL} \ 
       -Puser=${USER} \
       -Ppassword=${PASSWORD}
```
`URL`, `USER` and `PASSWORD` are parameters for publishing.

### Python
If you wish to manually create and publish a package for Python:
1. Generate services with `Gradle`:
    ```
       gradle --no-daemon clean generateProto
    ```
   You can find the generated files by following path: `src/gen/main/services/python`
2. Generate code from `.proto` files and publish everything using `twine`:
    ```
    pip install -r requirements.txt
    pip install twine
    python setup.py generate
    python setup.py sdist
    twine upload --repository-url ${PYPI_REPOSITORY_URL} --username ${PYPI_USER} --password ${PYPI_PASSWORD} dist/*
    ```
    `PYPI_REPOSITORY_URL`, `PYPI_USER` and `PYPI_PASSWORD` are parameters for publishing.

## Release notes

### 0.2.0

+ Migrated to th2 gradle plugin: `0.0.6` based on bom: `4.6.1`
+ Updated grpc-common: `4.5.0-dev`

### 0.1.0

+ Updated grpc-common 4.3.0

### 0.0.2

+ Added 'encode' method
+ Updated serviceGeneratorVersion and grpcCommonVersion to support gRPC pins filters.

### 0.0.1

+ 'decode' method
