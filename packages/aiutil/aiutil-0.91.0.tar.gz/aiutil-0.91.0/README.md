# AI/ML Utils  |  [@GitHub](https://github.com/legendu-net/aiutil)  |  [@PyPI](https://pypi.org/project/aiutil/)

This is a Python pacakage that contains misc utils for AI/ML.

1. Misc enhancement of Python's built-in functionalities.
    - string
    - collections
    - pandas DataFrame
    - datetime
2. Misc other tools
    - `aiutil.filesystem`: misc tools for querying and manipulating filesystems; convenient tools for manipulating text files.
    - `aiutil.url`: URL formatting for HTML, Excel, etc.
    - `aiutil.sql`: SQL formatting
    - `aiutil.cv`: some more tools (in addition to OpenCV) for image processing
    - `aiutil.shell`: parse command-line output to a pandas DataFrame
    - `aiutil.shebang`: auto correct SheBang of scripts
    - `aiutil.pydev`: tools for making it even easier to manage Python project
    - `aiutil.pdf`: easy and flexible extracting of PDF pages
    - `aiutil.memory`: query and consume memory to a specified range
    - `aiutil.notebook`: Jupyter/Lab notebook related tools
    - `aiutil.dockerhub`: managing Docker images on DockerHub in batch mode using Python
    - `aiutil.hadoop`: 
        - A Spark application log analyzing tool for identify root causes of failed Spark applications.
        - Pythonic wrappers to the `hdfs` command.
        - A auto authentication tool for Kerberos.
        - An improved version of `spark_submit`.
        - Other misc PySpark functions. 
    
## Installation

```bash
pip3 install --user -U aiutil
```
Use the following commands if you want to install all components of aiutil. 
Available additional components are `cv`, `docker`, `pdf`, `jupyter`, `admin` and `all`.
```bash
pip3 install --user -U aiutil[all]
```

## Executable Scripts

- snb: Search for content in Jupyter notebooks.
- logf: A Spark application log analyzing tool for identify root causes of failed Spark applications.
- pyspark_submit: Makes it easy to run Scala/Python Spark job.
- pykinit: Make it easier to authenticate users' personal accounts on Hadoop.
- match_memory: Query and consume memory.

You can run those executable scripts using uv 
(so that you don't have to manually install this Python package)
.
For example,

    uvx --from aiutil snb -h
