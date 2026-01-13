import os
import json
import pickle
import logging
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict


def _freeze(obj: Any) -> Any:
    if isinstance(obj, (MappingProxyType, dict)):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(_freeze(v) for v in obj)
    if isinstance(obj, (frozenset, set)):
        return frozenset(_freeze(v) for v in obj)
    return obj


def _release(obj: Any) -> Any:
    if isinstance(obj, (MappingProxyType, dict)):
        return {k: _release(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [_release(v) for v in obj]
    if isinstance(obj, (frozenset, set)):
        return set(_release(v) for v in obj)
    return obj


class VXSchedConfig:
    def __init__(
        self,
        **config_item: Any,
    ) -> None:
        for k, v in config_item.items():
            self.__dict__[k] = _freeze(v)
            if k == "env":
                for env_name, env_value in v.items():
                    os.environ[env_name] = env_value
                    logging.debug(f"Set Enviornment Variable `{env_name}` to *********")

    @classmethod
    def load(cls, config_file: str = "vxsched.json") -> Dict[str, Any]:
        config_file = Path(config_file)
        if not config_file.exists():
            logging.error(f"File {config_file} not found")
            return cls()

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return cls(**config)

    def save(self, config_file: str = "vxsched.json") -> None:
        config_file = Path(config_file)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(_release(self.__dict__), f, ensure_ascii=False, indent=4)

    def get(self, key: str, default: any = None) -> any:
        return self.__dict__.get(key, default)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __setitem__(self, key: str, value: any) -> None:
        raise RuntimeError(f"Key {key} is not allowed")

    def __getitem__(self, key: str) -> any:
        return self.__dict__[key]

    def __setattr__(self, name: str, value: any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            raise RuntimeError(f"Key '{name}' is Readonly")

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return self.__str__()


class VXSchedParams:
    def __init__(self) -> None:
        self.__save_params__ = {}

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__save_params__.copy()
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__: Dict[str, Any] = {}
        self.__dict__.update(state)

        self.__save_params__: Dict[str, Any] = {}
        self.__save_params__.update(state)

    def __getitem__(self, key: str) -> any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"Key {key} not found")

    def set_params(self, name: str, value: Any, saveable: bool = False) -> None:
        if saveable:
            self.__save_params__[name] = value
        setattr(self, name, value)


if __name__ == "__main__":
    config = VXSchedConfig(test="init")
    print(config)
    config.save("test2.json")
    config2 = VXSchedConfig.load("test2.json")
    print(config2)

    params = VXSchedParams()
    # params.set_params("test", "init", saveable=True)
    # print("params", params.test)
    pickle.dump(params, open("test.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    params2 = pickle.load(open("test.pkl", "rb"))
    print("params2", params2)

    # params.test = "test"
    # params.test2 = "test2"
    # params.save("test.json")
