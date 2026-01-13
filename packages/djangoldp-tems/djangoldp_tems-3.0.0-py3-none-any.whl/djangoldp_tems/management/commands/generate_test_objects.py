from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from djangoldp_object3d.models.object import Object3DObject
from djangoldp_object3d.models.category import Object3DCategory
from djangoldp_object3d.models.format import Object3DFormat
from djangoldp_object3d.models.keyword import Object3DKeyword

from djangoldp_factchecking.models.object import FactCheckingObject
from djangoldp_factchecking.models.affiliation import FactCheckingAffiliation
from djangoldp_factchecking.models.topic import FactCheckingTopic

from djangoldp_mediaobject.models.keyword import MediaObjectKeyword
from djangoldp_mediaobject.models.language import MediaObjectLanguage

from djangoldp_tems.models.location import TEMSLocation
from djangoldp_tems.models.licence import TEMSLicence


class Command(BaseCommand):
    help = 'Generate test data for Object3D and FactChecking models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting test data generation...'))

        # Create licenses
        licenses = self.create_licenses()
        self.stdout.write(self.style.SUCCESS(f'Created {len(licenses)} licenses'))

        # Create locations
        locations = self.create_locations()
        self.stdout.write(self.style.SUCCESS(f'Created {len(locations)} locations'))

        # Create Object3D related objects
        object3d_categories = self.create_object3d_categories()
        self.stdout.write(self.style.SUCCESS(f'Created {len(object3d_categories)} 3D categories'))

        object3d_formats = self.create_object3d_formats()
        self.stdout.write(self.style.SUCCESS(f'Created {len(object3d_formats)} 3D formats'))

        object3d_keywords = self.create_object3d_keywords()
        self.stdout.write(self.style.SUCCESS(f'Created {len(object3d_keywords)} 3D keywords'))

        # Create FactChecking related objects
        fc_affiliations = self.create_factchecking_affiliations()
        self.stdout.write(self.style.SUCCESS(f'Created {len(fc_affiliations)} fact-checking affiliations'))

        fc_topics = self.create_factchecking_topics()
        self.stdout.write(self.style.SUCCESS(f'Created {len(fc_topics)} fact-checking topics'))

        fc_keywords = self.create_mediaobject_keywords()
        self.stdout.write(self.style.SUCCESS(f'Created {len(fc_keywords)} media object keywords'))

        fc_languages = self.create_mediaobject_languages()
        self.stdout.write(self.style.SUCCESS(f'Created {len(fc_languages)} languages'))

        # Create Object3D objects
        object3d_objects = self.create_object3d_objects(
            object3d_categories, object3d_formats, object3d_keywords, locations, licenses
        )
        self.stdout.write(self.style.SUCCESS(f'Created {len(object3d_objects)} 3D objects'))

        # Create FactChecking objects
        fc_objects = self.create_factchecking_objects(
            fc_affiliations, fc_topics, fc_keywords, fc_languages, locations, licenses
        )
        self.stdout.write(self.style.SUCCESS(f'Created {len(fc_objects)} fact-checking objects'))

        self.stdout.write(self.style.SUCCESS('\n✅ Test data generation complete!'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(object3d_objects)} 3D Objects'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(fc_objects)} Fact-Checking Objects'))

    def create_licenses(self):
        """Create common licenses"""
        license_data = [
            {"name": "CC BY 4.0", "urlid": "cc-by-4.0"},
            {"name": "CC BY-SA 4.0", "urlid": "cc-by-sa-4.0"},
            {"name": "CC BY-NC 4.0", "urlid": "cc-by-nc-4.0"},
            {"name": "Public Domain", "urlid": "public-domain"},
            {"name": "All Rights Reserved", "urlid": "all-rights-reserved"},
        ]

        licenses = []
        for data in license_data:
            license_obj, created = TEMSLicence.objects.get_or_create(
                urlid=data["urlid"],
                defaults={"name": data["name"]}
            )
            licenses.append(license_obj)

        return licenses

    def create_locations(self):
        """Create locations for objects"""
        location_data = [
            {"name": "Louvre Museum", "city": "Paris", "country": "France",
             "latitude": 48.860611, "longitude": 2.337644},
            {"name": "British Museum", "city": "London", "country": "United Kingdom",
             "latitude": 51.519400, "longitude": -0.126900},
            {"name": "Metropolitan Museum", "city": "New York", "country": "United States",
             "latitude": 40.779437, "longitude": -73.963244},
            {"name": "Vatican Museums", "city": "Vatican City", "country": "Vatican",
             "latitude": 41.906555, "longitude": 12.453889},
            {"name": "Acropolis", "city": "Athens", "country": "Greece",
             "latitude": 37.971536, "longitude": 23.726151},
            {"name": "Colosseum", "city": "Rome", "country": "Italy",
             "latitude": 41.890210, "longitude": 12.492231},
        ]

        locations = []
        for data in location_data:
            location, created = TEMSLocation.objects.get_or_create(
                name=data["name"],
                defaults=data
            )
            locations.append(location)

        return locations

    def create_object3d_categories(self):
        """Create categories for 3D objects"""
        categories_names = [
            "Architecture", "Sculpture", "Historical Artifact",
            "Archaeological Site", "Monument", "Cultural Heritage"
        ]

        categories = []
        for name in categories_names:
            category, created = Object3DCategory.objects.get_or_create(name=name)
            categories.append(category)

        return categories

    def create_object3d_formats(self):
        """Create 3D file formats"""
        formats = ["OBJ", "FBX", "GLTF", "STL", "PLY", "3DS"]

        format_objs = []
        for fmt in formats:
            format_obj, created = Object3DFormat.objects.get_or_create(name=fmt)
            format_objs.append(format_obj)

        return format_objs

    def create_object3d_keywords(self):
        """Create keywords for 3D objects"""
        keywords = [
            "ancient", "medieval", "renaissance", "baroque", "classical",
            "roman", "greek", "egyptian", "gothic", "neoclassical",
            "stone", "marble", "bronze", "architecture", "sculpture"
        ]

        keyword_objs = []
        for kw in keywords:
            keyword, created = Object3DKeyword.objects.get_or_create(name=kw)
            keyword_objs.append(keyword)

        return keyword_objs

    def create_factchecking_affiliations(self):
        """Create fact-checking affiliations"""
        affiliations = [
            "International Fact-Checking Network",
            "Poynter Institute",
            "Independent",
            "Academic Institution",
            "News Organization"
        ]

        affiliation_objs = []
        for aff in affiliations:
            affiliation, created = FactCheckingAffiliation.objects.get_or_create(name=aff)
            affiliation_objs.append(affiliation)

        return affiliation_objs

    def create_factchecking_topics(self):
        """Create fact-checking topics"""
        topics = [
            "Politics", "Science", "Health", "Climate", "Technology",
            "Economy", "Education", "Social Media", "Elections", "Public Policy"
        ]

        topic_objs = []
        for topic in topics:
            topic_obj, created = FactCheckingTopic.objects.get_or_create(name=topic)
            topic_objs.append(topic_obj)

        return topic_objs

    def create_mediaobject_keywords(self):
        """Create keywords for media objects"""
        keywords = [
            "misinformation", "disinformation", "verified", "fact-check",
            "investigation", "analysis", "debunked", "true", "false", "misleading"
        ]

        keyword_objs = []
        for kw in keywords:
            keyword, created = MediaObjectKeyword.objects.get_or_create(name=kw)
            keyword_objs.append(keyword)

        return keyword_objs

    def create_mediaobject_languages(self):
        """Create languages"""
        languages = ["English", "French", "Spanish", "German", "Italian"]

        language_objs = []
        for lang in languages:
            language, created = MediaObjectLanguage.objects.get_or_create(name=lang)
            language_objs.append(language)

        return language_objs

    def create_object3d_objects(self, categories, formats, keywords, locations, licenses):
        """Create 10 realistic 3D objects"""
        objects_data = [
            {
                "title": "Arc de Triomphe 3D Model",
                "description": "Detailed 3D reconstruction of the Arc de Triomphe in Paris, created using photogrammetry. This model captures the neoclassical architecture and intricate sculptural details of this iconic monument.",
                "time_period": "1806-1836",
                "country": "France",
                "year": 1836,
                "creator": "Jean Chalgrin (architect)",
                "rights_holder": "Public Domain",
                "polygons": 850000,
                "file_size": "125 MB",
                "texture": "4K PBR textures",
                "texture_formats": "PNG, JPEG",
                "texture_resolution": "4096x4096",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Parthenon Temple Reconstruction",
                "description": "Archaeological reconstruction of the Parthenon temple on the Acropolis of Athens. This model represents the temple in its original state, including painted elements that have been lost to time.",
                "time_period": "447-432 BCE",
                "country": "Greece",
                "year": -432,
                "creator": "Athens Archaeological Society",
                "rights_holder": "CC BY-SA 4.0",
                "polygons": 1200000,
                "file_size": "185 MB",
                "texture": "8K color and normal maps",
                "texture_formats": "PNG",
                "texture_resolution": "8192x8192",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Roman Colosseum Interior",
                "description": "High-resolution 3D model of the Colosseum's interior, showing the underground hypogeum, arena floor, and seating areas. Based on laser scanning and historical documentation.",
                "time_period": "70-80 CE",
                "country": "Italy",
                "year": 80,
                "creator": "Italian Ministry of Culture",
                "rights_holder": "CC BY-NC 4.0",
                "polygons": 2500000,
                "file_size": "340 MB",
                "texture": "Photogrammetry textures",
                "texture_formats": "JPG, PNG",
                "texture_resolution": "4096x4096",
                "ai": False,
                "allow_ai": False,
            },
            {
                "title": "Venus de Milo Sculpture",
                "description": "Highly detailed scan of the Venus de Milo, one of the most famous ancient Greek sculptures. This model captures the fine details of the marble surface and classical sculptural techniques.",
                "time_period": "130-100 BCE",
                "country": "Greece",
                "year": -130,
                "creator": "Louvre Museum Digitization Team",
                "rights_holder": "Public Domain",
                "polygons": 450000,
                "file_size": "68 MB",
                "texture": "High-resolution color scan",
                "texture_formats": "PNG",
                "texture_resolution": "2048x2048",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Notre-Dame Cathedral Spire",
                "description": "3D model of Notre-Dame's historic spire before the 2019 fire, reconstructed from historical photographs and architectural drawings. Part of the digital preservation project.",
                "time_period": "1220-1250, restored 1860",
                "country": "France",
                "year": 1860,
                "creator": "Cultural Heritage Digitization Project",
                "rights_holder": "CC BY 4.0",
                "polygons": 3200000,
                "file_size": "480 MB",
                "texture": "4K PBR materials",
                "texture_formats": "PNG",
                "texture_resolution": "4096x4096",
                "ai": True,
                "allow_ai": True,
            },
            {
                "title": "Sphinx of Giza Model",
                "description": "Archaeological 3D model of the Great Sphinx, created from aerial photogrammetry and ground-level laser scanning. Includes geological analysis layers.",
                "time_period": "c. 2500 BCE",
                "country": "Egypt",
                "year": -2500,
                "creator": "Egyptian Antiquities Ministry",
                "rights_holder": "All Rights Reserved",
                "polygons": 1800000,
                "file_size": "265 MB",
                "texture": "High-resolution photogrammetry",
                "texture_formats": "JPEG, TIFF",
                "texture_resolution": "8192x8192",
                "ai": False,
                "allow_ai": False,
            },
            {
                "title": "Michelangelo's David",
                "description": "Ultra-high-resolution scan of Michelangelo's David from the Galleria dell'Accademia. One of the most detailed 3D models of Renaissance sculpture ever created.",
                "time_period": "1501-1504",
                "country": "Italy",
                "year": 1504,
                "creator": "Florence Digital Archive",
                "rights_holder": "CC BY-NC 4.0",
                "polygons": 5000000,
                "file_size": "720 MB",
                "texture": "16K marble surface scan",
                "texture_formats": "PNG, EXR",
                "texture_resolution": "16384x16384",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Stonehenge Archaeological Site",
                "description": "Complete 3D model of Stonehenge including the stone circle, surrounding earthworks, and nearby burial mounds. Created for archaeological research and public education.",
                "time_period": "3000-2000 BCE",
                "country": "United Kingdom",
                "year": -2500,
                "creator": "English Heritage",
                "rights_holder": "CC BY-SA 4.0",
                "polygons": 980000,
                "file_size": "145 MB",
                "texture": "Aerial and ground photogrammetry",
                "texture_formats": "JPG",
                "texture_resolution": "4096x4096",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Baroque Church Interior",
                "description": "Detailed 3D scan of a Baroque church interior, featuring ornate ceiling frescoes, gilded decorations, and marble columns. Anonymous 18th-century Austrian church.",
                "time_period": "1720-1740",
                "country": "Austria",
                "year": 1730,
                "creator": "European Heritage Digitization Initiative",
                "rights_holder": "CC BY 4.0",
                "polygons": 4200000,
                "file_size": "615 MB",
                "texture": "HDR environment maps, PBR textures",
                "texture_formats": "PNG, EXR",
                "texture_resolution": "8192x8192",
                "ai": False,
                "allow_ai": True,
            },
            {
                "title": "Roman Forum Reconstruction",
                "description": "Archaeological reconstruction of the Roman Forum as it appeared in the 2nd century CE, based on excavation data, historical texts, and comparative analysis with other Roman sites.",
                "time_period": "2nd century CE",
                "country": "Italy",
                "year": 150,
                "creator": "Rome Archaeological Institute",
                "rights_holder": "CC BY-SA 4.0",
                "polygons": 6800000,
                "file_size": "980 MB",
                "texture": "Procedural and historical textures",
                "texture_formats": "PNG",
                "texture_resolution": "4096x4096",
                "ai": True,
                "allow_ai": True,
            },
        ]

        created_objects = []
        for i, data in enumerate(objects_data):
            obj = Object3DObject.objects.create(**data)

            # Add random categories (1-2)
            obj.categories.set(random.sample(categories, random.randint(1, 2)))

            # Add format
            obj.format = random.choice(formats)

            # Add keywords (2-4)
            obj.keywords.set(random.sample(keywords, random.randint(2, 4)))

            # Add location
            obj.location = random.choice(locations)

            # Add licenses (1-2)
            obj.licences.set(random.sample(licenses, random.randint(1, 2)))

            obj.save()
            created_objects.append(obj)

        return created_objects

    def create_factchecking_objects(self, affiliations, topics, keywords, languages, locations, licenses):
        """Create 10 realistic fact-checking articles"""
        objects_data = [
            {
                "title": "Climate Change Temperature Records: Fact Check",
                "description": "Analysis of claims regarding global temperature records from 1880 to present. This fact-check examines data from NASA, NOAA, and independent climate research institutions to verify statements made in recent political debates about climate change trends.",
                "organisation": "Climate Facts Initiative",
                "person": "Dr. Sarah Johnson",
                "version": "v2.1",
                "publication_date": timezone.now() - timedelta(days=30),
            },
            {
                "title": "COVID-19 Vaccine Efficacy Claims Verified",
                "description": "Comprehensive fact-check of COVID-19 vaccine efficacy claims circulating on social media. Reviews peer-reviewed studies, clinical trial data, and real-world effectiveness data from multiple countries.",
                "organisation": "Health Verification Network",
                "person": "Dr. Michael Chen",
                "version": "v1.5",
                "publication_date": timezone.now() - timedelta(days=45),
            },
            {
                "title": "Election 2024: Voter Fraud Allegations Investigation",
                "description": "Detailed investigation into allegations of voter fraud in the 2024 elections. Cross-references official election commission data, court documents, and independent audits to verify or debunk circulating claims.",
                "organisation": "Electoral Integrity Watch",
                "person": "Jennifer Martinez",
                "version": "v3.0",
                "publication_date": timezone.now() - timedelta(days=15),
            },
            {
                "title": "Renewable Energy Statistics Fact Check",
                "description": "Verification of statistics about renewable energy adoption rates and cost comparisons. Analyzes data from International Energy Agency, government reports, and industry sources.",
                "organisation": "Energy Facts Coalition",
                "person": "Prof. Robert Williams",
                "version": "v1.0",
                "publication_date": timezone.now() - timedelta(days=60),
            },
            {
                "title": "5G Health Effects: Scientific Evidence Review",
                "description": "Comprehensive review of scientific studies on 5G technology health effects. Examines claims made in viral social media posts against peer-reviewed research from WHO, IEEE, and national health agencies.",
                "organisation": "Tech Facts Alliance",
                "person": "Dr. Emily Zhang",
                "version": "v2.0",
                "publication_date": timezone.now() - timedelta(days=90),
            },
            {
                "title": "Economic Growth Claims During Pandemic Verified",
                "description": "Analysis of economic growth statistics claimed by various political figures during the COVID-19 pandemic. Cross-checks IMF data, national statistics offices, and World Bank reports.",
                "organisation": "Economic Truth Initiative",
                "person": "Marcus Thompson",
                "version": "v1.3",
                "publication_date": timezone.now() - timedelta(days=120),
            },
            {
                "title": "Immigration Statistics and Crime Rates: The Facts",
                "description": "Fact-check examining the relationship between immigration and crime rates in major metropolitan areas. Uses FBI data, academic studies, and local police statistics.",
                "organisation": "Social Research Verification",
                "person": "Dr. Anna Kowalski",
                "version": "v2.2",
                "publication_date": timezone.now() - timedelta(days=75),
            },
            {
                "title": "Artificial Intelligence Job Displacement Claims",
                "description": "Investigation into claims about AI-driven job displacement rates. Reviews labor statistics, industry reports, and academic research on automation's impact on employment.",
                "organisation": "Future of Work Institute",
                "person": "David Lee",
                "version": "v1.1",
                "publication_date": timezone.now() - timedelta(days=50),
            },
            {
                "title": "Plastic Pollution Ocean Statistics Verification",
                "description": "Fact-check of widely circulated statistics about plastic pollution in oceans. Verifies numbers against peer-reviewed oceanographic research and environmental monitoring data.",
                "organisation": "Environmental Facts Network",
                "person": "Dr. Maria Santos",
                "version": "v1.0",
                "publication_date": timezone.now() - timedelta(days=100),
            },
            {
                "title": "Education System Performance: International Comparison",
                "description": "Analysis of claims comparing education system performance across countries. Examines PISA scores, UNESCO data, and OECD education reports to verify political statements.",
                "organisation": "Education Verification Project",
                "person": "Prof. James Anderson",
                "version": "v1.4",
                "publication_date": timezone.now() - timedelta(days=80),
            },
        ]

        created_objects = []
        for data in objects_data:
            obj = FactCheckingObject.objects.create(**data)

            # Add affiliation
            obj.affiliation = random.choice(affiliations)

            # Add topics (1-3)
            obj.topics.set(random.sample(topics, random.randint(1, 3)))

            # Add keywords (2-4)
            obj.keywords.set(random.sample(keywords, random.randint(2, 4)))

            # Add language
            obj.language = random.choice(languages)

            # Add location (optional)
            if random.random() > 0.5:
                obj.location = random.choice(locations)

            # Add licenses (1)
            obj.licences.set([random.choice(licenses)])

            obj.save()
            created_objects.append(obj)

        return created_objects
