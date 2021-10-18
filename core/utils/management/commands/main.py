from django.core.management.base import BaseCommand
from core.user.models import User,Account
from core.assets.models import Asset
from core.utils.validator import AssetInventory
from django.core.files import File
from django.core.files.images import ImageFile
# image_model.image_field('path', File().read())

class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        user = User.objects.get(username='hanabi')
        user_b = User.objects.get(username='ribonred')
        # account = Account.objects.create_wallet(user_id=user,name='regular')
        # account = Account.objects.create_wallet(user_id=user,name='regular')
        wallet = Account.objects.get(user=user)
        # Account.objects.opt_in(wallet.address)
        # bank = Account.objects.get(user=user_b)
        # bank.transfer(5000,wallet.address)
        # print(account.balance())
        print(wallet.balance())

        # props=AssetInventory(
        #     creator=wallet.address,
        #     asset_name='OZORA',
        #     unit_name='OZ',
        #     total=8_000_000,
        #     decimals=2,
        #     default_frozen=False,
        #     url='',
        #     metadata_hash=b'',
        #     manager=wallet.address,
        #     reserve=wallet.address,
        #     freeze=wallet.address,
        #     clawback=wallet.address
        # )
        # img = ImageFile(open('ask.png','rb'))
        # assets = Asset.objects.create_asset(
        #     asset_image=img,
        #     **props.__dict__
        # )
        # print(wallet.address)
        # ass = Asset.objects.get(asset_name='OZORA')
        # ass.total=1000
        # ass.save()
        # coin = Asset.objects.all().delete()
        # print(coin)
        # 10_000_000
        # coins = Asset.objects.create_coin(passphrase=wallet.private_key,asset_name='OZORA')
        # print(coin.count(),coin)

        