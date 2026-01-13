import django


__version__ = "v2.3.3"

if django.VERSION < (3, 2):
    default_app_config = "azbankgateways.apps.AZIranianBankGatewaysConfig"
