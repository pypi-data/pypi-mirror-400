class JupyterPlugin:
    name: str = "base"

    def pre_initialize(self, config: dict) -> None:
        pass

    def post_initialize(self, server_app) -> None:
        pass

    def pre_start(self, server_app) -> None:
        pass

    def post_start(self, server_app) -> None:
        pass

    def shutdown(self, server_app) -> None:
        pass
