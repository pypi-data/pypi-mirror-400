# LightChat

**LightChat** is a lightweight, high-performance runtime and orchestration framework for managing multiple local processes, including AI/LLM models. It provides safe process execution, resource monitoring, structured logging, and real-time metrics collection. Designed for developers and researchers working with multiple local models or scripts, LightChat makes managing and observing processes simple and reliable.

---

## **Features**

- Lightweight and efficient process management.
- Safe multi-process orchestration with graceful and hard termination.
- CPU, memory, and execution-time monitoring for each process.
- Structured logging with correlation IDs for easy tracing.
- Metrics collection and reporting for debugging and optimization.
- Compatible with Python 3.10+.
- Designed for testing local AI/ML/LLM models or any custom scripts safely.

---

## **Installation**

```bash
# Clone the repository
git clone https://github.com/yourusername/lightchat.git
cd lightchat

# Optional: create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
Quick Start
python
Copy code
import time
from lightchat.api.runtime import Runtime
from lightchat.config.core import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
config = config_loader.get()

# Initialize runtime
runtime = Runtime(config=config)

# Create a process
proc = runtime.create_process(
    name="hello_world",
    command=["python", "-c", "print('Hello, LightChat!')"]
)

# Start and wait
proc.start()
proc.wait()

# Get metrics
print(proc.metrics())
print(proc.status())
API Overview
Runtime
Create, start, and manage multiple processes.

Query all process statuses and metrics.

Stop or kill processes individually.

ProcessHandle
Represents a single process with monitoring.

Methods:

start(), stop(), kill()

wait(timeout=None) – Waits for completion.

status() – Returns current process state.

metrics() – Returns CPU, memory usage, and process state.

LightChatLogger
Structured logging with correlation IDs.

Thread and multi-process safe.

MetricsCollector
Collects CPU, memory, execution-time metrics for processes.

Useful for optimization and monitoring experiments.

Use Case
LightChat is ideal for:

Testing multiple LLM or AI models locally.

Running resource-heavy scripts with monitoring.

Debugging and profiling Python processes.

Building experimental ML pipelines safely.

Example: Running multiple small LLM models locally and observing resource consumption in real-time.

Acknowledgements
This project leverages the following Python libraries and tools:

psutil – For process and system resource monitoring.

uuid – For generating unique correlation IDs.

Python logging module – Structured logging for observability.

contextvars – Context-aware correlation IDs for multi-process logging.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

Bug reports, performance improvements, and new features are encouraged.

Follow PEP-8 and Python 3.10+ compatibility.