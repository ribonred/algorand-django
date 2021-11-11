from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import AppUserManager,AccountManager
from algosdk.constants import address_len,hash_len
from core.utils.models import BaseTimeStampModel,UlidField
from algosdk import mnemonic
from algosdk.future.transaction import AssetTransferTxn

class User(AbstractBaseUser, PermissionsMixin):
    WAIT, APPROVED ,UNVERIFIED,VERIFIED= "in waiting list", "approved","unverified","verified"
    status_choices = (
        (UNVERIFIED, "unverified"),
        (VERIFIED, "verified"),
        (WAIT, "in waiting list"),
        (APPROVED, "approved"),
    )

    email = models.EmailField(("email address"),null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    current_status = models.CharField(max_length=255, null=True, blank=True, choices=status_choices, default=UNVERIFIED)
    is_joined = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    AUTH_FIELD_NAME = "email"
    objects = AppUserManager()


class Account(BaseTimeStampModel):
    """Base model class for Algorand accounts."""
    account_id = UlidField(primary_key=True,prefix="adr_",editable=False)
    name=models.CharField(max_length=255,blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="wallet")
    address = models.CharField(max_length=address_len)
    private_key = models.CharField(max_length=address_len + hash_len)
    objects = AccountManager()
    
    def balance(self):
        """Return this instance's balance in microAlgos."""
        if self.user.is_superuser:
            return self.algod_client.account_info(self.address)
        return self.check_holdings()
        # return self.algod_client.account_info(self.address)

    @property
    def passphrase(self):
        """Return account's mnemonic."""
        return mnemonic.from_private_key(self.private_key)
    
    def check_holdings(self):
        """
        Checks the asset balance for the specific address and asset id.
        """
        account_info = self.algod_client.account_info(self.address)
        # print(account_info)
        assets = account_info.get("assets")
        for asset in assets:
            if asset['asset-id'] == 44253981:
                amount = asset.get("amount")
                return self.balance_formatter(amount,asset_id=44253981)
        return 0
    
    def transfer(self,amount,receiver):
        """
        Creates an unsigned transfer transaction for the specified asset id, to the 
        specified address, for the specified amount.
        """
        params = self.algod_client.suggested_params()
        txn = AssetTransferTxn(sender=self.address, sp=params, receiver=receiver, amt=amount, index=44253981)
        txinfo = self.sign_and_send(txn, self.passphrase)
        formatted_amount = self.balance_formatter(amount)
        print("Transferred {} from {} to {}".format(formatted_amount, 
            self.address, receiver))
        print("Transaction ID Confirmation: {}".format(txinfo.get("tx")))