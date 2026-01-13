from .engine import CDDEngine

_engine = CDDEngine()


def init():
    _engine.init_project()


def run():
    _engine.execute_audit()
