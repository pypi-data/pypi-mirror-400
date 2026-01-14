from typing import Type

from hatchling.plugin import hookimpl

from .publisher import TGZRAssetPublisher

# from .metadata_hook import TGZRAssetMetadataHook


# @hookimpl
# def hatch_register_metadata_hook() -> Type[TGZRAssetMetadataHook]:
#     return TGZRAssetMetadataHook


@hookimpl
def hatch_register_publisher() -> Type[TGZRAssetPublisher]:
    return TGZRAssetPublisher
