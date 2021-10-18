from dataclasses import dataclass
import json

@dataclass
class AssetInventory:
    creator:str
    asset_name:str
    unit_name:str
    total:int
    decimals:int
    default_frozen:bool
    url:str
    metadata_hash:bytes
    manager:str
    reserve:str
    freeze:str
    clawback:str

    def __repr__(self):
        return json.dumps(self.__dict__)

