import os
import json
from django.core.management.base import BaseCommand
from base.models import Wilaya, Commune

class Command(BaseCommand):
    help = "Load Wilaya and Commune data from data.json into the database"

    def handle(self, *args, **kwargs):
        # Locate JSON inside the 'data' directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "data", "wilaya_commune.json")

        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)

        wilaya_dict = {}

        for item in data:
            wilaya_code = item["wilaya_code"]
            wilaya_name = item["wilaya_name_ascii"]
            commune_name = item["commune_name_ascii"]

            # Ensure Wilaya exists
            wilaya, created = Wilaya.objects.get_or_create(
                code=wilaya_code, defaults={"name": wilaya_name}
            )
            wilaya_dict[wilaya_code] = wilaya  # Cache Wilaya instance

            # Ensure Commune exists under the correct Wilaya
            Commune.objects.get_or_create(
                name=commune_name, wilaya=wilaya_dict[wilaya_code]
            )

        self.stdout.write(self.style.SUCCESS("Wilaya & Commune data loaded successfully!"))
