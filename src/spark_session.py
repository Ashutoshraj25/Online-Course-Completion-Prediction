"""Spark Session initialization and configuration module.

Configured for robust execution on Windows with PySpark and local execution.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from pyspark.sql import SparkSession


def configure_windows_environment() -> None:
    """Ensure environment variables are properly configured across OS platforms."""
    if sys.platform.startswith("win"):
        # Configure JAVA_HOME (Spark 4.x requires Java 17+; C:\oracleJdk-26 is available)
        candidate_java_homes = [
            r"C:\oracleJdk-26",
            os.environ.get("JAVA_HOME"),
            r"C:\Program Files\Java\jdk-11",
            r"C:\jdk-11",
        ]
        for java_path in candidate_java_homes:
            if java_path and Path(java_path).exists():
                os.environ["JAVA_HOME"] = java_path
                java_bin = Path(java_path) / "bin"
                if java_bin.exists() and str(java_bin) not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = f"{java_bin};" + os.environ.get("PATH", "")
                break

        # Configure HADOOP_HOME if not already set or pointing to valid path
        candidate_hadoop_homes = [
            os.environ.get("HADOOP_HOME"),
            r"C:\hadoop\hadoop-3.4.3",
        ]
        for hadoop_path in candidate_hadoop_homes:
            if hadoop_path and Path(hadoop_path).exists():
                os.environ["HADOOP_HOME"] = hadoop_path
                hadoop_bin = Path(hadoop_path) / "bin"
                if hadoop_bin.exists() and str(hadoop_bin) not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = f"{hadoop_bin};" + os.environ.get("PATH", "")
                break

    # Ensure PySpark uses the running Python interpreter
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def get_spark_session(app_name: str = "OnlineCourseCompletion") -> SparkSession:
    """Initialize or retrieve a local SparkSession with optimized configurations.

    Args:
        app_name: Name of the Spark application.

    Returns:
        SparkSession instance.
    """
    configure_windows_environment()

    # Check for an existing active session
    active_session: Optional[SparkSession] = SparkSession.getActiveSession()
    if active_session is not None:
        return active_session

    mem_limit = "2g" if sys.platform.startswith("win") else "1g"

    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", mem_limit)
        .config("spark.executor.memory", mem_limit)
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.adaptive.enabled", "true")
    )

    spark = builder.getOrCreate()
    # Suppress verbose INFO logs for clean console output
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def stop_spark_session() -> None:
    """Gracefully stop the active SparkSession if present."""
    active_session = SparkSession.getActiveSession()
    if active_session is not None:
        active_session.stop()


if __name__ == "__main__":
    print("Testing Spark Session initialization...")
    session = get_spark_session()
    print(f"Spark version: {session.version}")
    print(f"Spark app name: {session.sparkContext.appName}")
    print(f"Spark master: {session.sparkContext.master}")
    df = session.createDataFrame([(1, "Test")], ["id", "val"])
    df.show()
    stop_spark_session()
    print("Spark Session test completed successfully.")
