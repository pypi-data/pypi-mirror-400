import json

from defusedxml.ElementTree import parse
from django.conf import settings
from django.core.management.base import BaseCommand

from djangoldp_ds4go.models import Category, Fact, Media


class Command(BaseCommand):
    help = "Import facts from RSS file"

    def add_arguments(self, parser):
        parser.add_argument("--rss_file", type=str, help="Path to the RSS file")

    def handle(self, *args, **options):
        rss_file = options["rss_file"]
        tree = parse(rss_file)
        root = tree.getroot()
        ns = {
            "schema": "https://schema.org/",
            "media": "http://search.yahoo.com/mrss/",
            "content": "http://purl.org/rss/1.0/modules/content/",
        }
        channel = root.find("channel")
        language_elem = channel.find("language")
        language = language_elem.text if language_elem is not None else "fr"

        for item in channel.findall("item"):
            guid = item.find("guid").text
            existing_fact = Fact.objects.filter(rss_guid=guid).first()
            title = item.find("title").text
            link = item.find("link").text
            review_elem = item.find("schema:review", ns)

            try:
                review = json.loads(review_elem.text) if review_elem is not None else {}
            except json.JSONDecodeError:
                review = {}
                self.stderr.write(
                    self.style.WARNING(
                        "Failed to parse review for item with guid %s. Ignoring."
                        % (guid)
                    )
                )

            description = item.find("description").text
            content_elem = item.find("content:encoded", ns)
            content = content_elem.text if content_elem is not None else ""
            author = item.find("author").text if item.find("author") is not None else ""
            enclosure_url = None
            enclosure = item.find("enclosure")

            if enclosure is not None:
                enclosure_url = enclosure.get("url")

            if existing_fact:
                fact = existing_fact
                self.stdout.write(f"Updating existing fact with guid {guid}")
            else:
                fact = Fact.objects.create(
                    rss_guid=guid,
                    link=link,
                    review=review,
                )
                self.stdout.write(f"Creating new fact: {title}")

            # Set translated fields
            setattr(fact, f"name_{language}", title)
            setattr(fact, f"description_{language}", description)
            setattr(fact, f"content_{language}", content)
            setattr(fact, f"author_{language}", author)

            if enclosure_url:
                setattr(fact, f"enclosure_{language}", enclosure_url).replace(
                    "medias/", getattr(settings, "MEDIA_URL", "/media/")
                )

            fact.save()

            # Categories
            categories = item.findall("category")
            for cat_elem in categories:
                cat_name = cat_elem.text
                category = self.get_or_create_category(cat_name, language)
                fact.categories.add(category)

            # Medias
            for media_elem in item.findall("media:content", ns):
                url = media_elem.get("url").replace(
                    "medias/", getattr(settings, "MEDIA_URL", "/media/")
                )
                file_size = int(media_elem.get("fileSize", 0))
                width = int(media_elem.get("width", 0))
                height = int(media_elem.get("height", 0))
                file_type = media_elem.get("type")
                desc = media_elem.find("media:description", ns)
                description = desc.text if desc is not None else ""
                existing_media = Media.objects.filter(
                    url=url, related_fact=fact
                ).first()

                if existing_media:
                    setattr(existing_media, f"description_{language}", description)
                    existing_media.save()
                else:
                    media = Media.objects.create(
                        url=url,
                        file_size=file_size,
                        width=width,
                        height=height,
                        file_type=file_type,
                        related_fact=fact,
                    )
                    setattr(media, f"description_{language}", description)
                    media.save()

            self.stdout.write(f"Processed fact: {title}")

    def get_or_create_category(self, cat_name, language):
        parts = cat_name.split("/")
        current_parent = None

        for part in parts:
            part = part.strip()
            category, created = Category.objects.get_or_create(
                name=part,
                parent_category=current_parent,
            )
            # FIXME: I don't know how to handle i18n here as these are strings: "Media Topic" could be "Totoro" in another lang?
            # if created or not getattr(category, f"name_{language}", None):
            #     setattr(category, f"name_{language}", part)
            #     category.save()
            current_parent = category

        return current_parent
