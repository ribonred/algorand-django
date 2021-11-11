from django.db import models
from core.utils.models import BaseTimeStampModel,UlidField
from algosdk.constants import address_len,hash_len,metadata_length,max_asset_decimals
from django.core.validators import MaxValueValidator, MinValueValidator
from core.utils.validator import AssetInventory
from core.user.manager import AssetManager





class Asset(BaseTimeStampModel):
    asset_id = UlidField(primary_key=True,prefix="cnx_",editable=False)
    creator = models.CharField(max_length=address_len, blank=False)
    asset_name = models.CharField(max_length=hash_len, blank=True)
    unit_name = models.CharField(max_length=8, blank=True)
    total = models.BigIntegerField(
        blank=False,
        validators=[MinValueValidator(1)],
    )
    decimals = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(0), MaxValueValidator(max_asset_decimals)],
    )
    default_frozen = models.BooleanField(blank=False, default=False)
    url = models.URLField(blank=True)
    metadata_hash = models.BinaryField(blank=True,null=True,editable=False)
    manager = models.CharField(max_length=address_len, blank=True)
    reserve = models.CharField(max_length=address_len, blank=True)
    freeze = models.CharField(max_length=address_len, blank=True)
    clawback = models.CharField(max_length=address_len, blank=True)
    asset_image = models.ImageField(null=True, blank=True)
    metadata_64 =models.CharField(max_length=500, blank=True,null=True)
    coind=models.CharField(max_length=255, blank=True,null=True)
    is_created = models.BooleanField(default=False)
    objects =AssetManager()

    @property
    def serialized_properties(self):
        props =AssetInventory(
            creator=self.creator,
            asset_name=self.asset_name,
            unit_name=self.unit_name,
            total=self.total,
            decimals=self.decimals,
            default_frozen=self.default_frozen,
            url=f'https://asklora.ai{self.asset_image.url}',
            metadata_hash=self.metadata_hash.tobytes(),
            manager=self.manager,
            reserve=self.reserve,
            freeze=self.freeze,
            clawback=self.clawback
        )
        data = props.__dict__
        data.pop('creator')
        return data