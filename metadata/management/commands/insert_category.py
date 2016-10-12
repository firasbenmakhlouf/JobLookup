# -*- coding: utf-8 -*-
from metadata.models import TanitJobsCategory
from django.core.management.base import BaseCommand

CHOICES = [
    'Tous secteurs',
    'Informatique',
    "Centres d'appels",
    'Industrie',
    'Ingenierie',
    "Technologie de l'information",
    'Commerce',
    'Formation',
    'Marketing',
    'Télécommunications',
    'Vente',
    'Transport',
    'Stratégie-Planification',
    'Science',
    'Commerce de détail',
    'Restauration',
    'Recherche',
    'Immobilier',
    'Controle Qualite',
    'Achat - Approvisionnement',
    'Pharmaceutiques',
    'Services a la clientele',
    'Media-Journalisme',
    'Gestion',
    'Juridique',
    'Assurances',
    'Installation-Entretien-Reparation',
    'Ressources humaines',
    'Sante',
    'Fonction publique',
    'Services veterinaires',
    'Finance',
    'Enseignement',
    'Distribution',
    'Design',
    'Consulting',
    'Construction',
    'Developpement des affaires',
    'Biotechnologie',
    'Banque',
    'Automobile',
    'Administration',
    'Comptabilite',
    'Autres',
]


class Command(BaseCommand):
    help = 'Fill the Database with the interests details'

    def handle(self, **options):
        objects = []
        for name in CHOICES:
            print name
            objects.append(TanitJobsCategory(name=name))
        TanitJobsCategory.objects.bulk_create(objects)
        print 'Tanit Jobs Category saved'
