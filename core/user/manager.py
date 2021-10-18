from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid
from django.db import models
from algosdk import account
import hashlib
import base64
from django.conf import settings
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn,AssetTransferTxn
from algosdk.future.transaction import write_to_file
from algosdk import mnemonic







class AppUserManager(BaseUserManager):

    def create_unique_username(self, email):
        strip = email.replace('@', '_').replace(
            '.com', '').replace('.', '_')
        unique_usr = "%s%s" % (uuid.uuid4().hex[:8], strip)
        return unique_usr

    def create_user(self, email=None, username=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('Users must have an username'))
        if username == '' or not username:
            user = self.model(username=self.create_unique_username(
                email), email=email, **extra_fields)
        else:
            user = self.model(username=username, email=email, **extra_fields)
        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password,email=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        if not username:
            strip = email.replace('@', '_').replace(
                '.com', '').replace('.', '_')
            unique_usr = "%s%s" % (uuid.uuid4().hex[:8], strip)
            username = unique_usr
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, username, password, **extra_fields)



class AlgorandManager(models.Manager):
    
    algod_client = algod.AlgodClient(settings.ALGO_TOKEN, settings.NODE)

    def wait_for_confirmation(self, transaction_id, timeout):
        start_round = self.algod_client.status()["last-round"] + 1
        current_round = start_round

        while current_round < start_round + timeout:
            try:
                pending_txn = self.algod_client.pending_transaction_info(transaction_id)
            except Exception:
                return 
            if pending_txn.get("confirmed-round", 0) > 0:
                return pending_txn
            elif pending_txn["pool-error"]:  
                raise Exception(
                    'pool error: {}'.format(pending_txn["pool-error"]))
            self.algod_client.status_after_block(current_round)                   
            current_round += 1
        raise Exception(
            'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

    def sign_and_send(self,txn, passphrase):
        """
        Signs and sends the transaction to the network.
        Returns transaction info.
        """
        private_key = mnemonic.to_private_key(passphrase)
        stxn = txn.sign(private_key)
        txid = stxn.transaction.get_txid()
        self.algod_client.send_transaction(stxn)
        self.wait_for_confirmation(txid, 5)
        print('Confirmed TXID: {}'.format(txid))
        txinfo = self.algod_client.pending_transaction_info(txid)
        return txinfo

    
    def create_coin(self,passphrase=None,asset_name=None):
        """
        Returns an unsigned txn object and writes the unsigned transaction
        object to a file for offline signing. Uses current network params.
        """
        try:
            model = super().get(asset_name=asset_name)
        except self.model.DoesNotExist:
            raise Exception('model not exist')
        params = self.algod_client.suggested_params()
        txn = AssetConfigTxn(model.creator, params, **model.serialized_properties)

        if passphrase:
            txinfo = self.sign_and_send(txn, passphrase)
            asset_id = txinfo.get('asset-index')
            print("Asset ID: {}".format(asset_id))
            model.coind=asset_id
            model.is_created = True
            model.save()
            return model
        else:
            write_to_file([txn], "create_coin.txn")





class AccountManager(AlgorandManager):

    def opt_in(self,client_address):

        params = self.algod_client.suggested_params()
        asset_account =super().get(address=client_address)
        txn = AssetTransferTxn(client_address, params, receiver=client_address, amt=0, index=2)
        passphrase = asset_account.passphrase
        txinfo = self.sign_and_send(txn,passphrase)


    def create_wallet(self,user_id=None,name=None,main=False):
        if user_id:
            private_key, public_address = account.generate_account()
            wallet =self.model(user=user_id,address=public_address,private_key=private_key,name=name)
            if not main:
                params = self.algod_client.suggested_params()
                txn = AssetTransferTxn(public_address, params, receiver=public_address, amt=0, index=2)
                passphrase = wallet.passphrase
                if passphrase:
                    txinfo = self.sign_and_send(txn,passphrase)
                    print("Opted in to asset ID: {}".format(2))
            wallet.save()
            return wallet
        return None



class AssetManager(AlgorandManager):

    def create_asset(self,**kwargs):
        img = kwargs.get('asset_image',None)
        if img:
            filebytes = img.read()
            h = hashlib.sha256()
            h.update(filebytes)
            kwargs['metadata_hash']=h.digest()
            kwargs['metadata_64']=base64.b64encode(h.digest())
            return self.create(**kwargs)

        





