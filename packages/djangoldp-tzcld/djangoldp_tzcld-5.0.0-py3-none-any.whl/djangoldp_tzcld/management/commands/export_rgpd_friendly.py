import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from faker import Faker

fake = Faker("fr_FR")


def reference(value):
    return f"REF:{value}"


def get_fake_value(length):
    if length < 5:
        length = 5
    return fake.pystr(min_chars=length, max_chars=length)


class Command(BaseCommand):
    help = "Export the whole database to a giant csv file"

    def handle(self, *args, **options):
        replaced_dict = {}

        models_to_ignore = [
            "admin.logentry",
            "auth.group",
            "auth.permission",
            "contenttypes.contenttype",
            "djangoldp_account.opclient",
            "djangoldp_dashboard.dashboard",
            "djangoldp.activity",
            "djangoldp.follower",
            "djangoldp.ldpsource",
            "djangoldp.scheduledactivity",
            "guardian.groupobjectpermission",
            "guardian.userobjectpermission",
            "oidc_provider.client",
            "oidc_provider.code",
            "oidc_provider.responsetype",
            "oidc_provider.rsakey",
            "oidc_provider.token",
            "oidc_provider.userconsent",
            "sessions.session",
        ]
        models_to_anonymize = [
            "djangoldp_tzcld.tzcldprofilejob",
            "djangoldp_tzcld.tzcldterritorysynthesisfollowed",
        ]

        field_to_ignore = [
            "allow_create_backlink",
            "id",
            "is_backlink",
        ]
        fields_to_anonymize = [
            "admins",
            "attachment_structure",
            "author_user",
            "author",
            "contact",
            "details",
            "document",
            "email",
            "first_name",
            "img",
            "last_name",
            "link",
            "longdesc",
            "mail",
            "members",
            "mobile_phone",
            "owner",
            "password",
            "phone",
            "user",
            "username",
            "jabberID",
            "files",
            "picture",
            "default_redirect_uri",
        ]

        model_fields_to_anonymize = [
            "djangoldp_account.account.slug",
            "djangoldp_account.account.urlid",
            "djangoldp_account.chatprofile.slug",
            "djangoldp_account.chatprofile.urlid",
            "djangoldp_account.ldpuser.slug",
            "djangoldp_account.ldpuser.urlid",
            "djangoldp_community.communitymember",
            "djangoldp_notification.notification.object",
            "djangoldp_notification.notification.summary",
            "djangoldp_notification.notification.type",
            "djangoldp_notification.subscription.inbox",
            "djangoldp_notification.subscription.object",
            "djangoldp_profile.profile.urlid",
            "djangoldp_uploader.file.original_url",
            "djangoldp_uploader.file.stored_url",
        ]

        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if model._meta.abstract:
                    continue

                exportable = model.objects.all()
                if not exportable:
                    continue

                model_identifier = f"{model._meta.app_label}.{model._meta.model_name}"
                if model_identifier in models_to_ignore:
                    continue

                file_path = f"exports/{model_identifier}.csv"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)

                    fields = [
                        field.name
                        for field in model._meta.fields
                        if field.name not in field_to_ignore
                    ]
                    writer.writerow(fields)

                    for obj in exportable:
                        row = []
                        for field_name in fields:
                            original_value = getattr(obj, field_name)
                            value = str(original_value)
                            value_length = len(value)

                            if (
                                original_value
                                and value
                                and value in replaced_dict
                                and type(original_value) is not bool
                            ):
                                new_value = replaced_dict[value]
                            elif model_identifier in models_to_anonymize:
                                # Anonymize all fields
                                new_value = reference(get_fake_value(value_length))
                            elif (
                                f"{model_identifier}.{field_name}"
                                in model_fields_to_anonymize
                            ):
                                new_value = reference(get_fake_value(value_length))
                            elif field_name in fields_to_anonymize:
                                # Anonymize specific field
                                if field_name == "first_name":
                                    new_value = reference(fake.first_name())
                                elif field_name == "last_name":
                                    new_value = reference(fake.last_name())
                                elif field_name in ["mail", "email"]:
                                    new_value = reference(fake.email())
                                elif field_name == "phone":
                                    new_value = reference(fake.phone_number())
                                else:
                                    new_value = reference(get_fake_value(value_length))
                            else:
                                new_value = value.replace(settings.BASE_URL, "")

                            if value != new_value:
                                replaced_dict[value] = new_value

                            row.append(new_value)

                        writer.writerow(row)
