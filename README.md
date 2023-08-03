# Argos-adf

## Warning
There're some variables in the code named **async**, but it is a reserved keyword in newer Python version, so be careful about Python version.

## How to run with Docker

```sh
docker build -t argos-adf .
docker run -d -v $PWD:/usr/src argos-adf
```
