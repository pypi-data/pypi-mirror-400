from NEMO.serializers import ModelSerializer
from NEMO.views.api import (
    ModelViewSet,
    boolean_filters,
    date_filters,
    datetime_filters,
    key_filters,
    manykey_filters,
    number_filters,
    string_filters,
)
from rest_flex_fields import FlexFieldsModelSerializer

from NEMO_billing.quotes.models import Quote, QuoteConfiguration, QuoteItem


class QuoteConfigurationSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = QuoteConfiguration
        fields = "__all__"


class QuoteSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = Quote
        fields = "__all__"
        expandable_fields = {
            "project": "NEMO_billing.invoices.api.ProjectWithDetailsSerializer",
            "configuration": "NEMO_billing.quotes.api.QuoteConfigurationSerializer",
            "users": ("NEMO.serializers.UserSerializer", {"many": True}),
            "creator": "NEMO.serializers.UserSerializer",
            "approved_by": "NEMO.serializers.UserSerializer",
        }


class QuoteItemSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = "__all__"
        expandable_fields = {"quote": "NEMO_billing.quotes.api.QuoteSerializer"}


class QuoteConfigurationViewSet(ModelViewSet):
    filename = "quote_configurations"
    queryset = QuoteConfiguration.objects.all()
    serializer_class = QuoteConfigurationSerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "expiration_in_days": number_filters,
        "current_quote_number": number_filters,
        "email_cc": string_filters,
        "merchant_name": string_filters,
        "merchant_details": string_filters,
        "terms": string_filters,
        "currency": string_filters,
        "currency_symbol": string_filters,
        "tax": number_filters,
        "tax_name": string_filters,
        "create_permissions": string_filters,
        "approval_permissions": string_filters,
    }


class QuoteViewSet(ModelViewSet):
    filename = "quotes"
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "quote_number": string_filters,
        "project": key_filters,
        "configuration": key_filters,
        "users": manykey_filters,
        "emails": string_filters,
        "expiration_date": date_filters,
        "creator": key_filters,
        "approved_by": key_filters,
        "created_date": datetime_filters,
        "updated_date": datetime_filters,
        "published_date": datetime_filters,
        "last_emails_sent_date": datetime_filters,
        "status": string_filters,
        "add_tax": boolean_filters,
    }


class QuoteItemViewSet(ModelViewSet):
    filename = "quote_items"
    queryset = QuoteItem.objects.all()
    serializer_class = QuoteItemSerializer
    filterset_fields = {
        "id": key_filters,
        "quantity": number_filters,
        "amount": number_filters,
        "minimum_charge": number_filters,
        "service_fee": number_filters,
        "description": string_filters,
        "rate_type": number_filters,
        "quote": key_filters,
    }
