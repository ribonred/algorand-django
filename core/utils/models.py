from __future__ import annotations

from typing import Any, Callable, NoReturn
from functools import partial
from django.core import checks, exceptions
from django.db import models
from django.db.models.fields import NOT_PROVIDED, CharField
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from ulid import ULID
from django.conf import settings
from algosdk.v2client import algod
from algosdk import mnemonic


class BaseTimeStampModel(models.Model):
    """
    Base model for timestamp support, related models: :model:`Clients.Client` and its related models, :model:`orders.Order` etc.
    """
    created = models.DateTimeField(editable=True)
    updated = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

    @property
    def algod_client(self):
        client= algod.AlgodClient(settings.ALGO_TOKEN, settings.NODE)
        return client
    
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
    

    def balance_formatter(self,amount, asset_id=2):
        """
        Returns the formatted units for a given asset and amount. 
        """
        asset_info = self.algod_client.asset_info(asset_id)
        decimals = asset_info['params'].get("decimals")
        unit = asset_info['params'].get("unit-name")
        formatted_amount = amount/10**decimals
        return "{} {}".format(formatted_amount, unit)

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()

        self.updated = timezone.now()
        return super(BaseTimeStampModel, self).save(*args, **kwargs)






def prefixed_default(default: Callable | str, *, prefix: str) -> Callable:
    if callable(default):
        return lambda: f"{prefix}{default()}"  # type: ignore[operator]
    else:
        return lambda: f"{prefix}{default}"


class CharIDField(CharField):
    default_error_messages = {
        "invalid_type": _("The value must be text."),
        "invalid_prefix": _("“%(value)s” requires the prefix “%(prefix)s”."),
    }
    description = _("Collision-resistant universal identifier")

    def __init__(
        self,
        prefix: str = "",
        default: Callable | str | NOT_PROVIDED | None = NOT_PROVIDED,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        self.prefix = prefix

        self.init_default = default

        if self.prefix and default not in (NOT_PROVIDED, None):
            # We wrap the default passed in so that we can apply the prefix.
            kwargs["default"] = prefixed_default(
                default, prefix=self.prefix  # type: ignore[arg-type]
            )
        else:
            kwargs["default"] = default

        # Ensure a unique index is set up by default unless the caller
        # explicitly disables it; this seems like the sane thing to do.
        kwargs.setdefault("unique", True)

        super().__init__(*args, **kwargs)

    def get_internal_type(self) -> str:
        return "CharField"

    def deconstruct(
        self,
    ) -> tuple[str, str, list, dict]:
        """Provide init values to serialize as part of migration freezing."""
        name, path, args, kwargs = super().deconstruct()

        kwargs["prefix"] = self.prefix
        kwargs["default"] = self.init_default

        return name, path, args, kwargs

    def check(self, **kwargs: Any) -> list[checks.CheckMessage]:
        errors = super().check(**kwargs)
        errors.extend(self._check_prefix())
        return errors

    def _check_prefix(self) -> list[checks.Error]:
        # Types have to be ignored here because these are runtime type checks
        # that will run against 3rd-party codebases we can't possibly predict.
        if not isinstance(self.prefix, str):
            return [  # type: ignore [unreachable]
                checks.Error(
                    "'prefix' keyword argument must be a string",
                    hint=(
                        "Pass a string or alternatively remove the "
                        "argument to disable prefixing."
                    ),
                    obj=self,
                    id="CharIDField.E001",
                )
            ]
        return []

    def validate(self, value: object, model_instance: models.Model) -> None | NoReturn:
        """
        Validate the fields value is a string & prefixed correctly.
        Called from .clean() on parent.
        """
        # No non-string types.
        if not isinstance(value, str):
            raise exceptions.ValidationError(
                self.error_messages["invalid_type"],
                code="invalid_type",
            )

        # Value must have prefix if the prefix is set.
        if self.prefix and not value.startswith(self.prefix):
            raise exceptions.ValidationError(
                self.error_messages["invalid_prefix"],
                code="invalid_prefix",
                params={"value": value, "prefix": self.prefix},
            )

        return super().validate(value, model_instance)
UlidField = partial(
    CharIDField,
    default=ULID,
    max_length=30,
    help_text="Ulid-format identifier for this entity."
)