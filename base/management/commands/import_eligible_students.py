# import_eligible_students.py

import csv
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from base.models import EligibleStudent


UG_PATTERN = r"^UG(20|22)ICT\d{4}$"


class Command(BaseCommand):
    help = "Import eligible ICT students from CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file"
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing records if they exist"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options["csv_file"]
        update_existing = options["update"]

        created_count = 0
        updated_count = 0
        skipped_count = 0
        invalid_format_count = 0

        try:
            with open(file_path, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                required_columns = {"ug_number", "full_name"}
                if not required_columns.issubset(reader.fieldnames):
                    self.stdout.write(self.style.ERROR(
                        "CSV must contain ug_number and full_name columns"
                    ))
                    return

                for row in reader:
                    ug_number = row["ug_number"].strip().upper()
                    full_name = row["full_name"].strip()

                    # Validate UG pattern
                    if not re.match(UG_PATTERN, ug_number):
                        invalid_format_count += 1
                        self.stdout.write(self.style.WARNING(
                            f"Invalid UG format skipped: {ug_number}"
                        ))
                        continue

                    student, created = EligibleStudent.objects.get_or_create(
                        ug_number=ug_number,
                        defaults={"full_name": full_name}
                    )

                    if created:
                        created_count += 1
                    else:
                        if update_existing:
                            student.full_name = full_name
                            student.save()
                            updated_count += 1
                        else:
                            skipped_count += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("CSV file not found"))
            return

        self.stdout.write(self.style.SUCCESS("\nImport completed.\n"))
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped: {skipped_count}")
        self.stdout.write(f"Invalid Format: {invalid_format_count}")
