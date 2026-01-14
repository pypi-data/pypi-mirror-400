from typing import Optional, Dict, Union, List
from lightchat.api.process import ProcessHandle
from lightchat.config.core import ConfigLoader, ConfigSchema
from lightchat.observability.core import LightChatLogger
from lightchat.exceptions import LightChatError

logger = LightChatLogger(__name__)


class Runtime:
    """
    High-level user-facing LightChat runtime.
    Manages multiple processes safely.
    """

    def __init__(self, config: Optional[Union[ConfigLoader, ConfigSchema]] = None):
        if isinstance(config, ConfigLoader):
            self.config: Optional[ConfigSchema] = config.get()
        elif isinstance(config, ConfigSchema):
            self.config = config
        else:
            self.config = ConfigLoader().get()

        self.processes: Dict[str, ProcessHandle] = {}
        logger.info("LightChat Runtime initialized")

    def create_process(
        self, name: str, command: Union[str, List[str]]
    ) -> ProcessHandle:
        if name in self.processes:
            raise ValueError(f"Process with name '{name}' already exists")

        handle = ProcessHandle(
            name=name,
            command=command,
            config=self.config
        )
        self.processes[name] = handle
        logger.info(f"Process '{name}' created")
        return handle

    def run(
        self,
        name: str,
        command: Union[str, List[str]],
        wait: bool = False,
        auto_cleanup: bool = True
    ) -> ProcessHandle:
        """
        Convenience method for users.
        Creates, starts, and optionally waits for a process.
        """
        proc = self.create_process(name, command)
        proc.start()

        if wait:
            proc.wait()
            if auto_cleanup:
                self.processes.pop(name, None)
                logger.info(f"Process '{name}' auto-cleaned")

        return proc

    def start_all(self) -> None:
        for handle in self.processes.values():
            handle.start()
        logger.info("All processes started")

    def stop_all(self) -> None:
        for handle in self.processes.values():
            handle.stop()
        logger.info("All processes stopped")

    def kill_all(self) -> None:
        for handle in self.processes.values():
            handle.kill()
        logger.warning("All processes killed")

    def status_all(self) -> Dict[str, str]:
        return {name: handle.status() for name, handle in self.processes.items()}

    def metrics_all(self) -> Dict[str, Dict]:
        return {name: handle.metrics() for name, handle in self.processes.items()}
